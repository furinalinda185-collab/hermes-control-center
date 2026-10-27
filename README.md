# Hermes Control Center

Operational home of this machine's Hermes Agent: what the machine is, what the
agent knows, how to carry all of it to another distro, and where to look when
something breaks.

| | |
|---|---|
| Machine | Arch Linux (rolling) + Ryoku 0.75.3, Hyprland |
| Hermes | v0.22.1+946.g8dcf6d5 (2026.9.24), profile `default` |
| Snapshot | 2026-10-26 (prior full snapshot 2026-10-23) |
| Repo | `furinalinda185-collab/hermes-control-center` (private) |
| Local clone | `~/hermes-control-center` (renamed from `~/hermes-brain`) |

This repo is the last thing that survives a wipe: the agent's skills, memory,
config, encrypted credentials, the system docs, and the user's notes. Treat it as
the backup that must always be current, not as an archive.

## Start here

| I want to… | Read |
|---|---|
| Move everything to a new distro | [docs/distro-hop.md](docs/distro-hop.md) + the `distro-hop` skill |
| Restore on a fresh install, right now | [Restore](#restore) below, then `./restore.sh --help` |
| Know what hardware/OS this is | [docs/machine.md](docs/machine.md) |
| Change a model, provider, tool path | [docs/hermes-home.md](docs/hermes-home.md) |
| Update the snapshot after changes | [Keeping this current](#keeping-this-current) |
| Find the user's own notes | [vault/](vault/README.md) |
| Understand what got encrypted, and how | [Secrets](#secrets) |

If you are an agent with a shell, read [Rules for agents](#rules-for-agents)
below, then [docs/hermes-home.md](docs/hermes-home.md) before touching anything
under `hermes/`.

## Layout

    hermes/                 drops straight into ~/.hermes
      skills/               68 SKILL.md files (3.6 MB); `ryoku` materialized
                            from its /usr/share/ryoku symlink
      memories/MEMORY.md    persistent memory — the "who the user is" layer
      SOUL.md               system-prompt identity file
      config.yaml           main configuration (no literal secrets)
      cron/                 scheduled job definitions (none active)

    docs/
      machine.md            OS, kernel, CPU/RAM/disk, peripherals, toolchain
      hermes-home.md        ~/.hermes anatomy, effective config, providers,
                            models, what is safe to ignore, what breaks on a hop
      distro-hop.md         the runbook, condensed; canonical detail in the skill

    vault/                  Obsidian notes (source: ~/vault), one redacted key note
    system/ryoku-rashin/    the Ryoku system vault: AGENTS.md, desktop.md,
                            packages.md, habits.md, memory/, journal/
                            Arch/Ryoku-specific — reference only, never restored
    secrets/                AES-256-CBC, PBKDF2 300k, sha256
      env.enc               ~/.hermes/.env — every API key
      auth.json.enc         ~/.hermes/auth.json — OAuth tokens, pools
      state.db.enc          ~/.hermes/state.db — session history (~27 MB)

    restore.sh              restore knowledge (+ secrets/sessions on request)
    scripts/snapshot.sh     refresh this repo from the live machine, commit, push
    MANIFEST.txt            generated inventory: counts and sizes

The `source/` checkout of the Ryoku monorepo is deliberately absent: ~36 MB and
re-clonable, see `system/ryoku-rashin/ryoku-repo.md`.

## Restore

    curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
    git clone https://github.com/furinalinda185-collab/hermes-control-center ~/hermes-control-center
    cd ~/hermes-control-center
    ./restore.sh                                 # knowledge only
    ./restore.sh --with-secrets                  # + API keys and OAuth tokens
    ./restore.sh --with-secrets --with-sessions  # + past conversations (state.db)
    ./restore.sh --with-secrets --drop-ryoku     # not going back to Ryoku

Then:

    hermes doctor        # flags stale absolute paths from the old machine
    hermes model         # confirm provider/model still resolve
    hermes               # start a session; memory should already be loaded

`--drop-ryoku` removes the `ryoku` skill and the `<!-- ryoku-rashin -->` block in
`MEMORY.md`. Both point at `/usr/share/ryoku` and `~/.local/share/ryoku/rashin`,
which only exist on a Ryoku install. Left in place, the first thing every new
session reads is missing.

Two things never travel and must be redone by hand: absolute paths inside
`config.yaml` (fix with `hermes config set <key> <value>`, never by editing), and
group membership for hardware (`uucp`/`dialout` for `/dev/ttyACM0`, plus
`video`, `input`) — re-add and re-login.

## Keeping this current

    cd ~/hermes-control-center && ./scripts/snapshot.sh

Copies skills/memories/SOUL/config/cron, encrypts `.env` and `auth.json`, redacts
credentials out of the notes, regenerates `MANIFEST.txt`, commits and pushes.
`--with-sessions` adds `state.db` (dumped consistently, ~27 MB per snapshot).
The passphrase comes from `$HERMES_BRAIN_PASSPHRASE` or a `read -rs` prompt;
empty skips re-encryption and leaves the existing blobs alone.

Run it after: new skills or memories, model/provider changes, new API keys, a
desktop change (Ryoku version, new bar config), or anything worth remembering.
Do not run it while actively installing packages — snapshot the settled state.

## Secrets

Encrypted with `openssl enc -aes-256-cbc -pbkdf2 -iter 300000 -md sha256`, same
flags in `restore.sh` and `scripts/snapshot.sh`. The passphrase is not in this
repo; the only copy was written once to `~/.hermes-handoff-passphrase.txt` — get
it into a password manager before that disk is wiped.

Provider keys present on this machine (names only): `OPENCODE_GO_API_KEY`,
`DISCORD_BOT_TOKEN`, plus browser/timeout tuning vars. `config.yaml` contains no
literal keys — verify with a `sk-|gho_|gsk_` grep before every commit.

## Rules for agents

1. Never commit a plaintext secret — not in notes, docs, config, or commit
   messages. Encrypted blobs in `secrets/` only. Verify before every commit:
   `grep -rInE 'sk-|oc_sk_|gho_|gsk_|xox[bap]-' . --exclude-dir=.git --exclude='*.enc'`
2. Never hand-edit `hermes/config.yaml` — it is a snapshot. Change the live file
   with `hermes config set`, then re-run `scripts/snapshot.sh`.
3. Restore only through `restore.sh`; it backs up an existing `~/.hermes` and
   handles `--drop-ryoku` / `--with-secrets` for you.
4. Snapshot, don't invent: `scripts/snapshot.sh` copies real files and regenerates
   `MANIFEST.txt`. Do not hand-write counts or sizes.
5. `state.db` is live SQLite — dump with `sqlite3 .backup`, never `cp` it.
6. `system/ryoku-rashin/` is a read-only reference from the Arch/Ryoku install;
   its paths are not live.

## Status

- Snapshot refreshed 2026-10-27: skill `distro-hop` added (68 skills), vault
  notes added, machine docs written, repo renamed to Hermes Control Center.
- Live system is still the pre-hop Arch/Ryoku install. After the actual hop,
  update `docs/machine.md` and re-run the snapshot.
- The repo carries the old distro's system vault under `system/ryoku-rashin/` for
  reference only. Delete it once the hop is done and nothing points back.
