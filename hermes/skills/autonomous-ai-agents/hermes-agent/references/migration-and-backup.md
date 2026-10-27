# Migrating a Hermes home to another machine

Use when the user is changing distros, replacing a laptop, or wants their agent's
accumulated knowledge in a private repo they can clone onto a fresh install.
The deliverable is a restored, byte-identical environment — verified by cloning
and running the restore, not by a successful push.

Work from `$HERMES_HOME` (a non-default profile lives under
`~/.hermes/profiles/<name>/`, not `~/.hermes`).

## What travels, and what stays

Everything that encodes this user's history goes. Everything the installer
re-fetches or that is re-clonable stays behind and is named in `MANIFEST.txt`.

| Path | Travel? | Why |
|---|---|---|
| `skills/` | yes | the accumulated procedures; the highest-value payload |
| `memories/MEMORY.md` | yes | who the user is; loaded into every session |
| `SOUL.md` | yes | identity/system-prompt file |
| `config.yaml` | yes | 100+ KB, holds routing and paths — see post-restore |
| `cron/` job definitions | yes | `.json` only, never `executions.db`/`*.lock` |
| `plugins/` `hooks/` `skins/` `tui-widgets/` `desktop-plugins/` `pets/` | if non-empty | never assume they exist |
| `.env`, `auth.json` | yes, **encrypted** | every API key and OAuth token |
| `state.db` | optional, 25 MB | conversation history; snapshot it, see below |
| `tools/` (1–2 GB), `hermes-agent/` | no | node/python/ffmpeg/chromium runtimes; installer re-fetches |
| `sessions/` `logs/` `cache/` `pastes/` `sandboxes/` | no | derived, or too noisy to diff |
| machine vaults (`~/.local/share/<distro>/...`) | reference only | keep under `system/` in the repo, never auto-restore |

## Procedure

1. **Inventory before copying.** Count what you have so `MANIFEST.txt` is
   generated, not narrated: `find skills -name SKILL.md | wc -l`, `du -sh` each
   top-level entry, `hermes cron list`. A 30-second inventory is what catches the
   1.7 GB `tools/` directory before it lands in the repo.
2. **Snapshot the session DB consistently.** Copying a live WAL database gives a
   torn file:
   `sqlite3 "$HH/state.db" ".backup '/tmp/handoff-state.db'"`
3. **Dereference symlinks.** Installed skills are often symlinks into a package
   directory (a distro-provided skill points at `/usr/share/<distro>/skills/...`),
   and those targets vanish on the new machine. Copy with `cp -aL` (follow links)
   so the repo is self-contained, then strip `*.lock` / `.locks/`, and **delete
   any nested `.git`** inside copied plugin repos — an embedded repo commits as a
   gitlink and restores empty.
4. **Encrypt the credentials.** AES-256-CBC + PBKDF2, one file each, in
   `secrets/`:  
   `openssl enc -aes-256-cbc -pbkdf2 -iter 300000 -md sha256 -salt \
      -pass "pass:$PASS" -in "$HH/.env" -out secrets/env.enc`  
   Generate `$PASS` with `openssl rand -base64 32`, write it to a `chmod 600`
   file **outside** the repo, and put it in the user's password manager. Show it
   to them once; a repo they cannot decrypt is worse than no repo.
5. **Lay out the repo** so the restore is a copy, not a merge: `hermes/` (mirrors
   `~/.hermes` exactly), `secrets/`, `system/<machine-vault>/`, `restore.sh`,
   `README.md`, `MANIFEST.txt`. `.gitignore`: `*.lock`, `*.db-shm`, `*.db-wal`.
6. **Cut the plaintext fallback too.** `hermes backup -o ~/hermes-full-backup-<date>.zip -k 0`
   then `chmod 600` it. It contains the plaintext `.env`, so it is for USB, never
   for git — but `hermes import <zip>` restores everything wholesale and is the
   answer when the passphrase is lost.
7. **Push private, then verify from a clean clone.** Clone into scratch, run the
   restore against a throwaway `HERMES_HOME`, and compare hashes:
   `sha256sum` of `.env` and `auth.json` against the originals, plus
   `select count(*) from sessions;` on the restored `state.db`. Then `rm -rf` the
   scratch home — it holds decrypted keys.
8. **Post-restore, on the new machine:** `hermes doctor` (flags stale absolute
   paths), `hermes model` (confirms provider routing), then a live session to
   confirm memory loaded.

`templates/restore-hermes-home.sh` is a proven restore script: flags for
secrets/sessions/dropping the old distro's skill, refuses to clobber an existing
home (moves it to `.pre-restore-<ts>`), and `chmod 600` on everything decrypted.

## Pitfalls

- **Encrypt credentials even when the user asks for plaintext.** Say once that git
  history is permanent and a private repo is one visibility toggle from public,
  then ship encrypted files with the same restore path. Do not argue twice.
- **A memory entry naming an old-machine path is worse than no entry.** The very
  first thing every new session reads would point at a file that does not exist.
  Strip the whole marked block (`<!-- ...:begin -->` … `<!-- ...:end -->`) plus
  its leading `§` separator, and remove the dead skill directory, behind a
  `--drop-<distro>` flag. Only the encrypted store or the vault copy keeps them.
- **Never report the migration done because the push succeeded.** Clone it and
  restore it; a repo that clones but does not decrypt is a failed handoff.
- **`rsync` is not guaranteed on the target machine.** `cp -aL` + `find ... -delete`
  does the same job with coreutils only; the script must not depend on rsync.
- **`config.yaml` carries absolute paths** (`$HOME/.hermes/tools/...`, browser
  binaries, `/usr/bin/...`). They restore fine and break silently — `hermes doctor`
  is the gate, and fixes go through `hermes config set`, never a hand edit.
- **Scan tracked text for key patterns before pushing:**
  `git grep -lIE '(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AIza[A-Za-z0-9_-]{25,})'`.
  Doc placeholders (`ghp_xx...xxxx`) are expected hits — read the line, do not
  delete the file.
- **`state.db.enc` is ~25 MB of binary.** Fine for a one-time handoff, wrong for
  a repo the user commits to regularly; tell them they can drop it after restore.
