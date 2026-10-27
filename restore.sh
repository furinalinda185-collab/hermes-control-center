#!/usr/bin/env bash
# Restore this Hermes Control Center onto a fresh machine.
#   ./restore.sh [--with-secrets] [--with-sessions] [--drop-ryoku] [--force]
set -euo pipefail

WITH_SECRETS=0; WITH_SESSIONS=0; FORCE=0; DROP_RYOKU=0
for a in "$@"; do
  case "$a" in
    --with-secrets)  WITH_SECRETS=1 ;;
    --with-sessions) WITH_SESSIONS=1 ;;
    --drop-ryoku)    DROP_RYOKU=1 ;;
    --force)         FORCE=1 ;;
    -h|--help)       sed -n '2,3p' "$0"; exit 0 ;;
    *) echo "unknown arg: $a"; exit 1 ;;
  esac
done

ROOT="$(cd "$(dirname "$0")" && pwd)"
HH="${HERMES_HOME:-$HOME/.hermes}"

command -v hermes >/dev/null || {
  echo "Hermes is not installed. Run:"; echo "  curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"; exit 1; }

if [ -d "$HH" ] && [ -n "$(ls -A "$HH" 2>/dev/null)" ]; then
  BAK="$HH.pre-restore-$(date +%Y%m%dT%H%M%S)"
  echo "Existing Hermes home found. Moving it to $BAK"
  mv "$HH" "$BAK"
fi
mkdir -p "$HH"

echo "→ knowledge"
cp -a "$ROOT/hermes/skills"    "$HH/"
cp -a "$ROOT/hermes/memories"  "$HH/"
[ -f "$ROOT/hermes/SOUL.md" ]     && cp "$ROOT/hermes/SOUL.md"     "$HH/"
[ -f "$ROOT/hermes/config.yaml" ] && cp "$ROOT/hermes/config.yaml" "$HH/"
if [ -d "$ROOT/hermes/cron" ]; then mkdir -p "$HH/cron"; cp -a "$ROOT/hermes/cron/." "$HH/cron/" 2>/dev/null || true; fi
chmod 700 "$HH"

# --drop-ryoku: strip the Arch/Ryoku-specific skill and its memory block, which
# would otherwise point every new session at a vault that does not exist.
if [ "$DROP_RYOKU" = 1 ]; then
  rm -rf "$HH/skills/ryoku"
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
    echo "  dropped ryoku skill + its memory block"
  fi
fi

decode() { # $1 = enc file, $2 = destination
  openssl enc -d -aes-256-cbc -pbkdf2 -iter 300000 -md sha256 -pass "pass:$PASS" -in "$1" -out "$2"
}

if [ "$WITH_SECRETS" = 1 ] || [ "$WITH_SESSIONS" = 1 ]; then
  PASS="${HERMES_BRAIN_PASSPHRASE:-}"
  if [ -z "$PASS" ]; then
    read -rsp "Passphrase (from your password manager): " PASS; echo
  fi
fi

if [ "$WITH_SECRETS" = 1 ]; then
  for pair in "env.enc:.env" "auth.json.enc:auth.json"; do
    src="$ROOT/secrets/${pair%%:*}"; dst="$HH/${pair##*:}"
    if [ -f "$src" ]; then decode "$src" "$dst"; chmod 600 "$dst"; echo "  restored ${pair##*:}"; fi
  done
fi

if [ "$WITH_SESSIONS" = 1 ]; then
  src="$ROOT/secrets/state.db.enc"
  if [ -f "$src" ]; then
    if [ -f "$HH/state.db" ] && [ "$FORCE" != 1 ]; then
      echo "  state.db already exists — skipping (use --force to overwrite)"; fi
    if [ ! -f "$HH/state.db" ] || [ "$FORCE" = 1 ]; then
      decode "$src" "$HH/state.db"; chmod 600 "$HH/state.db"; echo "  restored state.db"; fi
  fi
fi

echo
echo "Done. Next:"
echo "  hermes doctor    # flags stale paths from the old distro"
echo "  hermes model     # confirm provider/model resolve"
[ -d "$HH/skills/ryoku" ] && echo "  rm -rf $HH/skills/ryoku   # or re-run with --drop-ryoku"
