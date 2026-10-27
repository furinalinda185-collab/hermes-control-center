#!/usr/bin/env bash
# Hermes Control Center — refresh this repo from the live machine, commit, push.
#
#   ./scripts/snapshot.sh [--with-sessions] [--no-secrets] [--no-notes]
#                         [--no-push] [--dry-run]
#
# What it does:
#   hermes/skills,memories,SOUL.md,config.yaml,cron  <- copied from ~/.hermes
#   secrets/env.enc, auth.json.enc                   <- re-encrypted (.env, auth.json)
#   secrets/state.db.enc                             <- only with --with-sessions
#   vault/                                           <- notes, credentials redacted
#   MANIFEST.txt                                     <- regenerated
#
# Passphrase: $HERMES_BRAIN_PASSPHRASE, else a no-echo prompt. Never an argument,
# never written to disk, never in shell history.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HH="${HERMES_HOME:-$HOME/.hermes}"
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/vault}"
WITH_SESSIONS=0; WITH_SECRETS=1; WITH_NOTES=1; PUSH=1; DRY=0

for a in "$@"; do
  case "$a" in
    --with-sessions) WITH_SESSIONS=1 ;;
    --no-secrets)    WITH_SECRETS=0 ;;
    --no-notes)      WITH_NOTES=0 ;;
    --no-push)       PUSH=0 ;;
    --dry-run)       DRY=1 ;;
    -h|--help)       sed -n '2,17p' "$0"; exit 0 ;;
    *) echo "unknown arg: $a" >&2; exit 1 ;;
  esac
done

say()  { printf '→ %s\n' "$*"; }
run()  { if [ "$DRY" = 1 ]; then printf '   [dry] %s\n' "$*"; else "$@"; fi; }
die()  { printf 'error: %s\n' "$*" >&2; exit 1; }

[ -d "$HH" ] || die "no Hermes home at $HH"
command -v hermes >/dev/null || die "hermes not on PATH"

cd "$ROOT"
[ -d .git ] || die "$ROOT is not a git checkout"

# ---------------------------------------------------------------- knowledge
say "knowledge from $HH"
mkdir -p hermes/skills hermes/memories hermes/cron
# -L dereferences skill symlinks (ryoku -> /usr/share/ryoku/skills/ryoku);
# without it the repo would carry a link that resolves on exactly one machine.
run cp -aL "$HH/skills/." hermes/skills/
run cp -a  "$HH/memories/." hermes/memories/
[ -f "$HH/SOUL.md" ]     && run cp -a "$HH/SOUL.md" hermes/SOUL.md
[ -f "$HH/config.yaml" ] && run cp -a "$HH/config.yaml" hermes/config.yaml

# cron job definitions only: executions.db, ticker_* and output/ are runtime state
find "$HH/cron" -maxdepth 1 -type f ! -name 'executions.db' ! -name 'ticker_*' ! -name '.*' 2>/dev/null |
  while read -r f; do run cp -a "$f" "hermes/cron/$(basename "$f")"; done

# ------------------------------------------------------------------- secrets
if [ "$WITH_SECRETS" = 1 ]; then
  PASS="${HERMES_BRAIN_PASSPHRASE:-}"
  if [ -z "$PASS" ] && [ "$DRY" = 0 ]; then
    read -rsp "Passphrase (from your password manager, empty = skip): " PASS; echo
  fi
  if [ -z "$PASS" ]; then
    echo "  no passphrase — keeping existing secrets/*.enc untouched"
  else
    mkdir -p secrets
    export HERMES_BRAIN_PASSPHRASE="$PASS"
    enc() { # $1 src  $2 dest
      [ -f "$1" ] || return 0
      say "encrypt $(basename "$1") -> $2"
      run openssl enc -aes-256-cbc -pbkdf2 -iter 300000 -md sha256 \
        -pass env:HERMES_BRAIN_PASSPHRASE -in "$1" -out "$2"
    }
    enc "$HH/.env"      secrets/env.enc
    enc "$HH/auth.json" secrets/auth.json.enc

    if [ "$WITH_SESSIONS" = 1 ] && [ -f "$HH/state.db" ]; then
      TMP="$(mktemp -d)"
      trap 'rm -rf "$TMP"' EXIT
      # A live WAL database must be dumped, not copied.
      run sqlite3 "$HH/state.db" ".backup '$TMP/state.db'"
      enc "$TMP/state.db" secrets/state.db.enc
    fi
    unset HERMES_BRAIN_PASSPHRASE PASS
  fi
fi

# --------------------------------------------------------------------- notes
if [ "$WITH_NOTES" = 1 ] && [ -d "$VAULT" ]; then
  say "notes from $VAULT"
  mkdir -p vault
  shopt -s nullglob
  for f in "$VAULT"/*.md; do
    base="$(basename "$f")"
    [ "$base" = "README.md" ] && continue        # keep the repo's own index
    run cp -a "$f" "vault/$base"
  done
  shopt -u nullglob
  # Redact anything that looks like a credential. Notes are for humans; a key
  # belongs in .env + secrets/env.enc, never in git history.
  if [ "$DRY" = 0 ]; then
    find vault -maxdepth 1 -name '*.md' -print0 | while IFS= read -r -d '' f; do
      before="$(sha256sum "$f" | cut -d' ' -f1)"
      sed -i -E \
        -e 's/(oc_sk_)[A-Za-z0-9_-]{10,}/\1REDACTED/g' \
        -e 's/(sk-)[A-Za-z0-9_-]{20,}/\1REDACTED/g' \
        -e 's/(gho_|ghp_|github_pat_)[A-Za-z0-9_-]{20,}/\1REDACTED/g' \
        -e 's/(gsk_)[A-Za-z0-9_-]{20,}/\1REDACTED/g' \
        -e 's/(xox[baprs]-)[A-Za-z0-9-]{10,}/\1REDACTED/g' \
        -e 's/(AIza)[A-Za-z0-9_-]{30,}/\1REDACTED/g' "$f"
      [ "$before" != "$(sha256sum "$f" | cut -d' ' -f1)" ] && {
        printf '\n> Credentials in this note were redacted by scripts/snapshot.sh on %s.\n> The live value belongs in ~/.hermes/.env, encrypted at secrets/env.enc.\n' \
          "$(date -u +%F)" >> "$f"
        echo "  redacted credentials in $f"
      }
    done
  fi
fi

# ------------------------------------------------------------------ manifest
say "MANIFEST.txt"
if [ "$DRY" = 0 ]; then
  skills=$(find hermes/skills -name SKILL.md | wc -l)
  files=$(find hermes/skills -type f | wc -l)
  {
    echo "Hermes Control Center manifest — generated $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo
    printf 'hermes/skills        %s SKILL.md files, %s files, %s\n' \
      "$skills" "$files" "$(du -sh hermes/skills | cut -f1)"
    printf 'hermes/memories      %s\n' "$(du -sh hermes/memories | cut -f1)"
    printf 'hermes/config.yaml   %s lines\n' "$(wc -l < hermes/config.yaml)"
    printf 'vault                %s notes\n' "$(find vault -maxdepth 1 -name '*.md' | wc -l)"
    printf 'docs                 %s pages\n' "$(find docs -maxdepth 1 -name '*.md' | wc -l)"
    printf 'nix                  %s files\n' "$(find nix -type f 2>/dev/null | wc -l)"
    printf 'system/ryoku-rashin  %s files, %s\n' \
      "$(find system/ryoku-rashin -type f | wc -l)" "$(du -sh system/ryoku-rashin | cut -f1)"
    printf 'secrets              %s\n' "$(ls secrets/*.enc 2>/dev/null | xargs -n1 basename | tr '\n' ' ')"
    echo
    echo "Excluded on purpose: tools/ (1.7G), installs/ (1.3G), hermes-agent/ (1.2G),"
    echo "cache/, logs/, state.db WAL/SHM, *.lock, system/ryoku-rashin/source."
  } > MANIFEST.txt
fi

# -------------------------------------------------------------------- commit
if [ "$DRY" = 0 ]; then
  git add -A
  if git diff --cached --quiet; then
    echo "→ no changes to commit"
  else
    msg="snapshot: $(date -u +%Y-%m-%dT%H:%MZ) from $(cat /etc/hostname 2>/dev/null || uname -n)"
    say "commit"
    git -c user.name="${GIT_AUTHOR_NAME:-$(git config user.name || echo hermes)}" \
        -c user.email="${GIT_AUTHOR_EMAIL:-$(git config user.email || echo hermes@localhost)}" \
        commit -q -m "$msg"
    git --no-pager log --oneline -1
  fi

  if [ "$PUSH" = 1 ]; then
    say "push $(git remote get-url origin 2>/dev/null || echo '<no remote>')"
    git push origin HEAD
    git status -sb | head -2
  else
    echo "→ not pushed (--no-push); remember: an unpushed snapshot is not a backup"
  fi
fi
