# Hermes brain — portable handoff

Everything this machine's Hermes Agent learned, packaged so it survives a distro
swap. Source machine: Arch Linux (Ryoku desktop), Hermes profile `default`.
Snapshot date: 2026-10-23.

## What is in here

    hermes/                 → drops straight into ~/.hermes
      skills/               67 skills (3.6 MB). The `ryoku` skill was a symlink
                            into /usr/share/ryoku on the old distro; it is a
                            real directory here so the repo is self-contained.
      memories/MEMORY.md    persistent memory (the "who the user is" layer)
      SOUL.md               system-prompt identity file
      config.yaml           main configuration (no literal secrets — verified)
      cron/                 scheduled job definitions (none were active)

    system/ryoku-rashin/    the Ryoku system vault: AGENTS.md, desktop.md,
                            packages.md, user.md, habits.md, memory/, journal/.
                            Arch/Ryoku-specific — kept for reference, not
                            restored automatically. The `source/` checkout of the
                            Ryoku monorepo was deliberately excluded: it is
                            ~36 MB and re-clonable (see `ryoku-repo.md`).

    secrets/                AES-256-CBC, PBKDF2 (300k iterations, sha256)
      env.enc               ~/.hermes/.env — every API key
      auth.json.enc         ~/.hermes/auth.json — OAuth tokens, credential pools
      state.db.enc          ~/.hermes/state.db — full session history, 25 MB

The passphrase is **not** in this repo. It was written once to
`~/.hermes-handoff-passphrase.txt` on the old machine — put it in your password
manager before you wipe that disk.

## Restore on the new distro

    curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
    git clone <this-repo> ~/hermes-brain
    cd ~/hermes-brain
    ./restore.sh                     # knowledge only
    ./restore.sh --with-secrets      # + API keys and OAuth tokens
    ./restore.sh --with-secrets --with-sessions   # + past conversations
    ./restore.sh --with-secrets --drop-ryoku      # not going back to Ryoku

Then:

    hermes doctor        # will flag stale absolute paths from the old distro
    hermes model         # confirm provider/model still resolve
    hermes               # start a session; memory should already be loaded

## After restoring

`config.yaml` carries absolute paths from the old machine (`~/.hermes/tools/...`
binaries, browser paths, possibly `/usr/bin/...`). `hermes doctor` names each
one; fix them with `hermes config set <key> <value>`, never by hand-editing.

Two things do not travel and must be re-done on the new machine:

- **The `ryoku` skill** — it documents a desktop that only exists on Ryoku. It
  will load but every path in it will miss.
- **The `~/.local/share/ryoku/rashin` vault and the memory block pointing at
  it** — `MEMORY.md` opens with a "Ryoku Rashin system vault" entry telling every
  session to read `~/.local/share/ryoku/rashin/AGENTS.md` before exploring. On a
  new distro that file is gone, so the very first thing the agent reads is
  missing.

`--drop-ryoku` removes both (the skill directory and that `<!-- ryoku-rashin -->`
memory block) in one step. The vault is still in `system/ryoku-rashin/` if you
want to re-read it as a human.

Once restored, you can drop `secrets/state.db.enc` (25 MB) from the repo if you
do not want to carry conversation history in git.
