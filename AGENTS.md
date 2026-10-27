# AGENTS.md — read this before touching the repo

This repository is the control center for one machine's Hermes Agent install. It
is both a backup and a reference. If you are an agent operating here, the rules
below override convenience.

Repo: `furinalinda185-collab/hermes-control-center` (private), local clone
`~/hermes-control-center`. Live Hermes home: `~/.hermes`, profile `default`.

## What to trust

- `README.md` — the index and current state. Start there.
- `docs/machine.md` — hardware/OS facts as measured on the live machine.
- `docs/hermes-home.md` — what lives in `~/.hermes`, effective config, sizes.
- `docs/distro-hop.md` — the migration runbook; the `distro-hop` skill (also in
  `hermes/skills/system/distro-hop/`) is the canonical, longer version.
- `vault/` — the user's own notes, not agent output. Quote, don't rewrite.
- `secrets/*.enc` — opaque. Never decrypt into the working tree, never print a
  decrypted value into a transcript.
- `system/ryoku-rashin/` — read-only reference from the Arch/Ryoku install. Its
  paths are not live; do not treat them as current configuration.

## Hard rules

1. **No plaintext secrets.** Not in notes, not in docs, not in `config.yaml`, not
   in commit messages. Encrypted blobs in `secrets/` only. Before any commit:

       grep -rInE 'sk-[A-Za-z0-9]|oc_sk_|gho_|gsk_|xox[bap]-' . \
         --exclude-dir=.git --exclude='*.enc' --exclude='*.db'

   must return nothing but documented placeholders.
2. **Never hand-edit `hermes/config.yaml`.** It is a snapshot. Change the live
   file with `hermes config set <key> <value>`, then re-run `scripts/snapshot.sh`.
3. **Restore only through `restore.sh`.** It moves an existing `~/.hermes` to
   `~/.hermes.pre-restore-<ts>` and knows the `--drop-ryoku` / `--with-secrets`
   semantics. Hand-copying leaves the Ryoku memory block behind.
4. **Snapshot, don't invent.** `scripts/snapshot.sh` copies real files and
   regenerates `MANIFEST.txt`. Do not hand-write counts or sizes.
5. **`state.db` is a live SQLite database.** Dump with
   `sqlite3 ~/.hermes/state.db ".backup <tmp>"`, never `cp` a running database.
6. **Do not rewrite history on `main`.** Snapshots are append-only commits; a
   force-push would silently destroy the only copy of something.

## Fast orientation

    git log --oneline -5          # what changed recently
    cat MANIFEST.txt              # counts/sizes of this snapshot
    ls hermes/skills              # skill categories (68 SKILL.md files)
    ./restore.sh --help           # restore flags
    ./scripts/snapshot.sh --help  # refresh flags

## Live machine shape (as of 2026-10-26)

- Arch Linux rolling, kernel 7.2.8-1-cachyos, Ryoku 0.75.3 desktop on Hyprland.
- Hermes v0.22.1+946.g8dcf6d5, profile `default`, provider `opencode-go`
  (default `mimo-v2.6-flash`; `deepseek-v4.1-flash` in use as of this snapshot),
  local fallback `local-nemotron` on `127.0.0.1:8080`.
- Arduino UNO R4 WiFi on `/dev/ttyACM0` when plugged in; `arduino-cli` in `~/bin`.
- Obsidian vault at `~/vault` (source of `vault/` here).

## When done

If you changed machine facts, config, skills, or notes: update the matching doc,
then run `./scripts/snapshot.sh` so the repo and the machine agree again. A
control center that lags reality is worse than none.
