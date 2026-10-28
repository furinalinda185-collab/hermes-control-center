---
name: distro-hop
description: "Use when hopping distros: snapshot and restore Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [distro-hop, migration, backup, restore, arch, hermes-home]
    category: system
    related_skills: [hermes-agent, ryoku]
---

# Distro hop

## When to Use

Use when the user is switching distros, reinstalling / wiping the OS, moving to a
new machine, or asking "will I lose my Hermes stuff?". Also load this before any
`restore.sh` run, and after a hop when refreshing the control center.

Source of truth: GitHub `furinalinda185-collab/hermes-control-center`, cloned at
`~/hermes-control-center` (formerly `hermes-brain`). It holds the knowledge
snapshot, `restore.sh`, `scripts/snapshot.sh`, and the machine docs.

**Core rule:** a backup only counts once it is pushed and readable from a device
that is *not* the machine being wiped. Verify the remote, not the local copy.

## What travels, what does not

From `~/.hermes` (4.5G total — do not copy it whole):

| Path | Size | Travels? |
|---|---|---|
| `skills/` | 3.6M | yes — materialize symlinks (`cp -aL`); `ryoku` is a symlink into `/usr/share/ryoku` |
| `memories/MEMORY.md`, `user.md` | <10K | yes |
| `SOUL.md`, `config.yaml`, `cron/` | small | yes |
| `.env`, `auth.json` | small | yes — **encrypted only** |
| `state.db` | 25-30M | optional (session history) — encrypt, dump with `sqlite3 .backup` |
| `tools/` | 1.7G | no — rebuilt/re-downloaded |
| `installs/`, `hermes-agent/` | 1.3G + 1.2G | no — `hermes update` restores them |
| `cache/`, `logs/` | ~365M | no |

Non-Hermes things that are easy to forget: the Obsidian vault (`~/vault`),
passphrase file (`~/.hermes-handoff-passphrase.txt`), SSH/GPG keys, browser
profiles, `~/bin` (arduino-cli), project repos.

Game installs do not travel on their own. `games/mx-bikes/` in the repo holds the
ReShade shader+presets, game/profile configs, the mod tooling scripts, a
`mods-inventory.md`/`.tsv` reinstall list (the install *units*: 42 tracks, 5 bike
packs, 6 tyre packs) and `mods-manifest.txt` (bytes+mtime for every file under the
29G `mods/`). Mod *content* cannot go to GitHub (100MB/file, ~5G repo): restore is
a re-download checked against the inventory and manifest, then
`tools/mxb_verify.py`. Copy-paste recipe and remote-verification commands:
`references/game-preservation.md`. Same rule for any other game — configs, an
install-unit inventory and a manifest go in the repo; the packs never do.

When the user is mid-wipe ("I'm swapping right now"), commit the feasible subset
first and state the gap and its alternative in the same reply. A size limit has no
answer worth a clarification round-trip, and a stalled backup is worse than a
partial one that names what it left behind.

## 1. Pre-flight (old machine)

    hermes --version
    hermes doctor                      # note every absolute path it complains about
    du -sh ~/.hermes/* | sort -h       # confirm nothing new has grown huge
    git -C ~/hermes-control-center status --short
    grep -rInE 'sk-[A-Za-z0-9]|gho_|gsk_|xox[bap]-' ~/vault ~/.hermes/config.yaml

That last grep is not paranoia: notes and configs leak keys, and this repo gets
pushed. Redact before committing, even to a private repo.

## 2. Snapshot

    cd ~/hermes-control-center && ./scripts/snapshot.sh

It copies knowledge (`cp -aL`), encrypts `.env` and `auth.json`, redacts
credentials out of `vault/` notes, refreshes `MANIFEST.txt`, commits and pushes.
`--with-sessions` adds a consistent `state.db` dump to the encrypted blobs.
Passphrase comes from `$HERMES_BRAIN_PASSPHRASE` or a `read -rs` prompt —
never an argument, never a file in the repo, never shell history.

Manual equivalent of the crypto step:

    openssl enc -aes-256-cbc -pbkdf2 -iter 300000 -md sha256 \
      -pass env:HERMES_BRAIN_PASSPHRASE -in ~/.hermes/.env -out secrets/env.enc

Same flags for `auth.json.enc` and `state.db.enc`. Keep `iter`/`md` fixed —
`restore.sh` hard-codes them.

## 3. New machine

    curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
    git clone https://github.com/furinalinda185-collab/hermes-control-center ~/hermes-control-center
    cd ~/hermes-control-center
    ./restore.sh --with-secrets --drop-ryoku
    ./restore.sh --with-secrets --with-sessions --drop-ryoku   # + history

Then repair what cannot travel:

    hermes doctor
    hermes config set <key> <value>    # for each stale absolute path
    hermes model                       # confirm provider/model still resolve

`--drop-ryoku` is required unless the new distro really runs Ryoku: it deletes the
`ryoku` skill and the `<!-- ryoku-rashin -->` block in `MEMORY.md` that points
every session at `~/.local/share/ryoku/rashin/AGENTS.md`. Left in place, the first
thing a new session reads does not exist.

## 4. Verify — do not report success without these

    hermes --version
    hermes doctor                                  # no stale paths
    find ~/.hermes/skills -name SKILL.md | wc -l   # matches snapshot count (67 live / 68 in repo)
    grep -c OPENCODE_GO_API_KEY ~/.hermes/.env     # 1 after --with-secrets
    hermes model                                   # or start a session and /model
    arduino-cli version                            # hardware that carried over

Then start a session and confirm memory is loaded (the agent should already know
the user's facts without being told).

## Pitfalls

- **Copying `state.db` with `cp` while Hermes runs** can capture a torn WAL. Dump
  with `sqlite3 ~/.hermes/state.db ".backup /tmp/state.db"` and encrypt that.
- **Symlinked skills** (`ryoku` → `/usr/share/ryoku/skills/ryoku`) need `cp -aL`
  or the repo ends up with a broken link. That is why the repo carries a real dir.
- **`config.yaml` absolute paths** (tools binaries, browser path, `/usr/bin/...`)
  fail silently after a hop. `hermes doctor` names them; fix with
  `hermes config set`, never by hand-editing 2,300 lines.
- **Renaming the repo** means `git remote set-url`, a README/AGENTS sweep, and a
  fresh clone check. `restore.sh` locates itself, so it keeps working.
- **Group membership** (uucp/dialout for `/dev/ttyACM0`, video, input) is not in
  any config file — re-add after install and re-login, or every hardware tool
  fails with a permission error.
- **Do not delete the old machine's passphrase file** before the first restore
  on the new system succeeds. `~/.hermes-handoff-passphrase.txt` is the only copy.
- **`--with-sessions` overwrites `state.db`** only with `--force`; a fresh install
  has none, so a silent "skipping" line mid-output is easy to miss.
- **Repo mirrors drift silently.** `~/.local/share/ryoku/rashin/memory/*.md`
  mirrors `system/ryoku-rashin/memory/`, and `~/.hermes/skills/**` mirrors
  `hermes/skills/**`. Editing the local copy without copying it into the repo in
  the same session means the next restore reinstates the stale version — which is
  exactly the state a hop cannot detect afterwards.
- **`snapshot.sh` needs the passphrase**, so it cannot run in a session where the
  passphrase is unavailable. Fall back to `git add` on the specific changed files
  plus a `MANIFEST.txt` line for any new top-level directory, commit and push —
  never skip the push because the full snapshot could not run.

## After the hop

Update the control center: `docs/machine.md` (new distro/kernel/hardware),
`docs/hermes-home.md` (config drift), the memory block for the new desktop, and
re-run `./scripts/snapshot.sh`. If the old distro is gone for good, drop
`system/<old-desktop>/` from the repo or keep it read-only for reference.

## If the target is NixOS

Installing without a USB stick (from the running distro, subvolumes, no dd) and
the traps that cost real time - the bootloader step that silently does nothing,
`install-grub.sh` dying on a missing toplevel argument, the shared-ESP generation
limit, and the polkit dead end: [`references/nixos-no-usb.md`](references/nixos-no-usb.md).

The planned rice is `Sly-Harvey/NixOS` (flake + home-manager + Hyprland, MIT),
read `docs/nixos-rice.md` in the control center before touching anything and use
`nix/variables.laptop.nix` for the host variables. Two upstream defaults break on
this laptop: `hardware.nvidia.open` must be `true` (Blackwell GB205M) and
`nvidiaChannel` must be `latest`, not `legacy_580`. NixOS adds its own wrinkles to
steps 3-4: `config.yaml` absolute paths are all stale (no writable `/usr/bin`),
and `~/.local/bin` needs to be on `PATH` from the flake's zsh config, not a profile
drop-in.

### Installing from the running system, no USB

The NixOS manual supports this ("Install NixOS on another partition, from your
existing Linux distribution"). `pacman -S nix`, `nix-channel --add
https://nixos.org/channels/nixos-25.11 nixpkgs && nix-channel --update`,
`nix-env -f '<nixpkgs>' -iA nixos-install-tools`; then `btrfs subvolume create
@nixos` and `btrfs subvolume snapshot @home @nixos-home` (instant and CoW — the old
home stays put as the rollback), mount root + home + ESP under `/mnt/nixos`,
`nixos-generate-config --root /mnt/nixos`, then `nixos-install --root /mnt/nixos
--flake ~/nixos#<host> --no-root-passwd`. Build the toplevel with `nix build` as
the user first: cache misses on hyprland and nixvim run ~13 min, and it reduces
the install to a copy.

**Pitfall: silent bootloader no-op.** `/etc/NIXOS` is touched *before* the
bootloader step, so a finished-looking install can leave a completely empty ESP.
Check `/boot/grub/grub.cfg` and `efibootmgr` before rebooting. Re-run the step as
`NIXOS_INSTALL_BOOTLOADER=1 nixos-enter --root /mnt/nixos -c
'/run/current-system/bin/switch-to-configuration boot'`; calling `install-grub.sh`
directly dies at `$ARGV[1] or die`, because it needs the toplevel path that
switch-to-configuration supplies. `device = "nodev"` plus `efiSupport = true` is
the correct EFI GRUB setup, and it coexists with Limine on a shared ESP.

**Also required:** replace `hosts/<host>/hardware-configuration.nix` — upstream's
is LUKS + ext4 for a different machine — and drop the `modules/hardware/drives`
import, which hardcodes upstream's `/mnt/games` and `/mnt/work` UUIDs.
