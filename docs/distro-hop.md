# Distro hop — runbook

Condensed here; the canonical, longer procedure is the `distro-hop` skill, and
this repo also carries it at `hermes/skills/system/distro-hop/SKILL.md`, so it
comes back automatically after a restore.

## Order of operations

1. **Freeze the machine.** Stop installing, finish or abandon half-done desktop
   tweaks. A snapshot of a moving target is a snapshot of a bug.
2. **Snapshot** (`./scripts/snapshot.sh --with-sessions` if history matters) and
   confirm the push landed: `git status -sb` clean, `git log --oneline -1`
   matches the timestamp you just made.
3. **Verify from outside.** Open the repo in a browser or `gh repo view` — not
   just `git status`. A local commit is not a backup.
4. **Save the passphrase.** `~/.hermes-handoff-passphrase.txt` → password manager.
   Without it the encrypted blobs are dead weight; with it they are your keys.
5. **Wipe and install** the new distro.
6. **Restore:** install Hermes, clone, `./restore.sh --with-secrets --drop-ryoku`
   (add `--with-sessions` for history).
7. **Repair:** `hermes doctor`, `hermes config set` for each stale path,
   `hermes model`, re-add groups (`uucp`/`dialout`, `video`, `input`), re-login.
8. **Re-snapshot** on the new machine and update `docs/machine.md`.

## What always gets forgotten

| Thing | Where it lives | Why it bites |
|---|---|---|
| Passphrase | `~/.hermes-handoff-passphrase.txt` | repo blobs become unreadable |
| Obsidian vault | `~/vault` | not in `~/.hermes`; now copied into `vault/` |
| Arduino CLI + core | `~/bin`, `~/.arduino15` | `arduino-cli` works but the `renesas_uno` core is missing |
| SSH / GPG keys | `~/.ssh`, `~/.gnupg` | `gh` auth, commit signing |
| Browser profiles | `~/.config/*` | logins, extensions |
| Project repos | `~/Projects`, `~/` | uncommitted work |
| System vault | `~/.local/share/ryoku/rashin` | snapshot lives in `system/` here |

## Known-good flags

    ./restore.sh                                   # knowledge only, safest
    ./restore.sh --with-secrets                    # + keys (needed to think)
    ./restore.sh --with-secrets --with-sessions    # + conversation history
    ./restore.sh --with-secrets --drop-ryoku       # leaving Ryoku behind
    ./restore.sh --with-secrets --drop-ryoku --force   # overwrite an existing state.db

`restore.sh` moves any existing `~/.hermes` to `~/.hermes.pre-restore-<ts>`
instead of deleting it — if a restore goes wrong, that directory is the undo.
