# Machine — inventory

Measured on the live system 2026-10-26, before the distro hop. Everything here is
observation, not configuration: if `docs/hermes-home.md` and this file disagree
with the live machine, the machine wins and this file needs refreshing.

## OS and desktop

| | |
|---|---|
| Distro | Arch Linux, rolling (`ID=arch`, `BUILD_ID=rolling`) |
| Kernel | 7.2.8-1-cachyos (CachyOS kernel on Arch, not the stock `linux` package) |
| Desktop | Ryoku 0.75.3.r3968.gcfd8899-1 (`ryoku-hub`, `ryoku-shell`), Hyprland compositor |
| Logind session | compositor running as a Hyprland process; `XDG_*` vars are empty in non-login shells — read them from inside the session, not from an agent shell |
| Packages | 1,129 installed (`pacman -Q \| wc -l`) |

Ryoku's own system vault lives at `~/.local/share/ryoku/rashin/` (`AGENTS.md`,
`desktop.md`, `packages.md`, `user.md`, `habits.md`, `memory/`, `journal/`). A
snapshot of it sits in `system/ryoku-rashin/` in this repo. `~/.hermes/skills/ryoku`
is a symlink into `/usr/share/ryoku/skills/ryoku`.

## Hardware

| | |
|---|---|
| CPU | Intel Core Ultra 9 275HX, 24 logical CPUs |
| RAM | 30 GiB usable, ~26 GiB available at rest |
| Disk | `/dev/nvme1n1p2`, 952 G, 600 G used (64%), 353 G free |
| GPU | Intel Arrow Lake-S iGPU + NVIDIA RTX 5070 Ti Mobile (GB205M) |
| Microcontroller | Arduino UNO R4 WiFi, USB serial — `/dev/ttyACM0` when plugged in |
| User groups | `mamaroufaren libvirt video uucp kvm input wheel` |

The Arduino is not permanently attached; `/dev/ttyACM0` only exists while it is
plugged in. `uucp` is already in the group list, which is what gives the user
write access to it.

## Toolchain

| Tool | Path | Note |
|---|---|---|
| `hermes` | `~/.local/bin/hermes` | v0.22.1+946.g8dcf6d5, installed from git into `~/.hermes/hermes-agent` (1.2 G) |
| `gh` | `/usr/bin/gh` | authenticated as `furinalinda185-collab`, scopes `repo`, `workflow`, `gist`, `read:org` |
| `git`, `node`, `npm` | `/usr/bin/*` | |
| `python3` | `~/.hermes/installs/<id>/environments/<id>/venv/bin/python3` | Hermes's own venv; no PyYAML in it, use `/usr/bin/python3` for ad-hoc YAML work (also lacks it — parse with grep or install `python-yaml`) |
| `arduino-cli` | `~/bin/arduino-cli` | core `arduino:renesas_uno` installed; FQBN `arduino:renesas_uno:unor4wifi` |
| `openssl` | `/usr/bin/openssl` | 3.x, used for the encrypted blobs in `secrets/` |
| `ffmpeg`, `yt-dlp`, `jq`, `rg` | `/usr/bin/*` | media + shell work |
| `prowl` | not on `PATH` | the `prowl` skill describes cited code intelligence; the CLI is not installed here (it is a plugin-provided toolset, not a binary) |

## Disk pressure after a hop

`~/.hermes` is 4.5 G: `tools/` 1.7 G, `installs/` 1.3 G, `hermes-agent/` 1.2 G,
`cache/` 360 M, `state.db` 27 M, `logs/` 5.6 M, `skills/` 3.6 M. Only the last
three travel; the rest is rebuilt by the installer and `hermes update`. If the
new distro's root partition is small, budget ~5 G for a fresh Hermes home plus
the tools it downloads on first use.

## Observed quirks

- `pacman -Q` currently prints `error: ryoku: missing required signature` while
  still listing packages. Harmless for reads; worth fixing before an upgrade.
- `hostname` is not installed (Arch base does not ship it); use
  `cat /etc/hostname` or `uname -n`.
- Kernel is CachyOS-branded under an Arch userland. On a hop, kernel and
  userland must come from the same repo set, or DKMS/nvidia modules will drift.
