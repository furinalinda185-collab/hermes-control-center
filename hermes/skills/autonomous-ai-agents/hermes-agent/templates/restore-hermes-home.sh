#!/usr/bin/env bash
# Restore a Hermes home from a handoff repo built per
# references/migration-and-backup.md. Copy next to restore.sh and adjust the
# --drop-<distro> stanza for the machine you are leaving.
#
#   ./restore.sh [--with-secrets] [--with-sessions] [--drop-ryoku] [--force]
set -euo pipefail

WITH_SECRETS=0; WITH_SESSIONS=0; FORCE=0; DROP_MACHINE_SKILL=0
for a in "$@"; do
  case "$a" in
    --with-secrets) WITH_SECRETS=1 ;;
    --with-sessions) WITH_SESSIONS=1 ;;
    --drop-ryoku)   DROP_MACHINE_SKILL=1 ;;   # rename per distro
    --force)        FORCE=1 ;;
    -h|--help)      sed -n '2,8p' "$0"; exit 0 ;;
    *) echo "unknown arg: $a"; exit 1 ;;
  esac
done

ROOT="$(cd "$(dirname "$0")" && pwd)"
HH="${HERMES_HOME:-$HOME/.hermes}"

command -v hermes >/dev/null || {
  echo "Hermes is not installed. Run:"
  echo "  curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"; exit 1; }

# Never merge into an existing home: move it aside first.
if [ -d "$HH" ] && [ -n "$(ls -A "$HH" 2>/dev/null)" ]; then
  BAK="$HH.pre-restore-$(date +%Y%m%dT%H%M%S)"
  echo "Existing Hermes home found. Moving it to $BAK"
  mv "$HH" "$BAK"
fi
mkdir -p "$HH"

echo "-> knowledge"
cp -a "$ROOT/hermes/skills"   "$HH/"
cp -a "$ROOT/hermes/memories" "$HH/"
[ -f "$ROOT/hermes/SOUL.md" ]     && cp "$ROOT/hermes/SOUL.md"     "$HH/"
[ -f "$ROOT/hermes/config.yaml" ] && cp "$ROOT/hermes/config.yaml" "$HH/"
if [ -d "$ROOT/hermes/cron" ]; then
  mkdir -p "$HH/cron"; cp -a "$ROOT/hermes/cron/." "$HH/cron/" 2>/dev/null || true
fi
chmod 700 "$HH"

# Drop the old distro's skill AND the memory block that points at its vault;
# a stale path in MEMORY.md misdirects every future session.
if [ "$DROP_MACHINE_SKILL" = 1 ]; then
  rm -rf "$HH/skills/ryoku"                      # rename per distro
  mem="$HH/memories/MEMORY.md"
  if [ -f "$mem" ] && grep -q 'ryoku-rashin:begin' "$mem"; then
    python3 - "$mem" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s = re.sub(r"<!-- ryoku-rashin:begin -->.*?<!-- ryoku-rashin:end -->\n?", "", s, flags=re.S)
s = re.sub(r"^\s*§\s*\n", "", s)
open(p, "w", encoding="utf-8").write(s)
PY
    echo "  dropped machine skill + its memory block"
  fi
fi

decode() { # $1 = encrypted file, $2 = destination
  openssl enc -d -aes-256-cbc -pbkdf2 -iter 300000 -md sha256 \
    -pass "pass:$PASS" -in "$1" -out "$2"
}

if [ "$WITH_SECRETS" = 1 ] || [ "$WITH_SESSIONS" = 1 ]; then
  PASS="${HERMES_BRAIN_PASSPHRASE:-}"
  if [ -z "$PASS" ]; then
    read -rsp "Passphrase (from your password manager): " PASS; echo
  fi
fi

for pair in "env.enc:.env" "auth.json.enc:auth.json"; do
  [ "$WITH_SECRETS" = 1 ] || break
  src="$ROOT/secrets/${pair%%:*}"; dst="$HH/${pair##*:}"
  [ -f "$src" ] || continue
  decode "$src" "$dst"; chmod 600 "$dst"; echo "  restored ${pair##*:}"
done

if [ "$WITH_SESSIONS" = 1 ] && [ -f "$ROOT/secrets/state.db.enc" ]; then
  if [ -f "$HH/state.db" ] && [ "$FORCE" != 1 ]; then
    echo "  state.db exists - skipping (--force to overwrite)"
  else
    decode "$ROOT/secrets/state.db.enc" "$HH/state.db"
    chmod 600 "$HH/state.db"; echo "  restored state.db"
  fi
fi

echo
echo "Done. Next: hermes doctor; hermes model; then a live session to confirm memory."
