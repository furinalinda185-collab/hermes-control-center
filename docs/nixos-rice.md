# NixOS rice — target configuration

Reference rice for the hop after this one: **NixOS + Hyprland**, flake-based, by
Harvey Jacobs-Grant (Sly-Harvey), MIT licensed, 2024.

    upstream   https://github.com/Sly-Harvey/NixOS
    branch     master
    pinned     d1c1ce4dc6  (2026-10-23, "Updated flake")
    size       ~197 MB, 601 files, ~490 KB of Nix

The point of this doc: when NixOS gets installed, the desktop should come up
already rice'd — not as a from-scratch project.

## Why this repo

It is a **flake + home-manager + per-host variable file** configuration, which is
the closest thing the Nix world has to Ryoku's "pick it in a GUI" model. Every
choice the user used to make in Ryoku Hub / QS Bar Settings lives in one file,
`hosts/<host>/variables.nix`:

| Knob | Options |
|---|---|
| `desktop` | hyprland, i3, gnome, plasma6 |
| `bar` | waybar, noctalia, wayle |
| `waybarTheme` | stylish, minimal |
| `sddmTheme` | astronaut, black_hole, purple_leaves, jake_the_dog, hyprland_kath |
| `terminal` / `editor` / `browser` / `fileManager` | kitty, alacritty, wezterm / nixvim, zed, vscode, helix, doom-emacs, nvchad, neovim / librewolf, zen-beta, firefox, floorp / yazi, lf, thunar |
| `videoDriver` | nvidia, amdgpu, intel, nvk |
| `nvidiaChannel` | stable, latest, beta, legacy_580, legacy_xxx |
| `games`, `bluetoothSupport`, `batterySupport` | booleans |
| `timezone`, `locale`, `clock24h`, `kbdLayout`, `kbdVariant`, `consoleKeymap`, `capslockAsESC` | localization |

`install.sh` (run from the NixOS ISO) asks for the GPU driver, username and host,
writes `variables.nix`, and rebuilds. `dev-shells/` carries 45 per-language
`flake.nix` + `.envrc` pairs — `platformio` and `arduino` work has a home there.

## Layout that matters

    flake.nix                  inputs: nixpkgs-unstable, nixos-25.11, hyprland,
                               home-manager, nixvim, noctalia, plasma-manager,
                               spicetify, firefox-addons, zen-browser, flatpak
    hosts/Default|Singularity/ configuration.nix, hardware-configuration.nix,
                               host-packages.nix, variables.nix
    modules/default.nix        imports gated on variables.nix
    modules/core/              boot, hardware, network, sddm, security, users
    modules/hardware/video/    amdgpu, intel, nvidia, nvk
    modules/desktop/           hyprland (waybar/rofi/swaync/hyprlock/hypridle/
                               wlogout/noctalia), i3, gnome, plasma6
    modules/programs/          terminal, editor, browser, file-manager, media, cli
    pkgs/, overlays/           local packages

## variables.nix for this laptop

The machine is a hybrid-GPU laptop: Intel Core Ultra 9 275HX + RTX 5070 Ti
Mobile (GB205M, Blackwell), AX211 Wi-Fi/BT, 30 GiB RAM. Upstream defaults do not
fit it — three of them are wrong in ways that break the boot or the battery, not
just taste. The ready-to-paste file is [nix/variables.laptop.nix](../nix/variables.laptop.nix).

| Knob | Upstream | For this machine | Why |
|---|---|---|---|
| `videoDriver` | `nvidia` | `nvidia` (keep) | iGPU-only would waste the 5070 Ti |
| `nvidiaChannel` | `legacy_580` | **`latest`** | 580 is the legacy branch; Blackwell wants a current driver |
| `hardware.nvidia.open` | `false` (in `modules/hardware/video/nvidia.nix`) | **`true`** | Blackwell/GB20x needs the open kernel module; the proprietary one will not load |
| `batterySupport` | `false` | **`true`** | it is a laptop: upower, tlp, lid handling |
| `bluetoothSupport` | `false` | **`true`** | Intel AX211 Bluetooth is present (`rfkill` shows `hci0`) |
| `timezone` | `Europe/London` | **`America/Los_Angeles`** | matches `/etc/localtime` |
| `locale` | `en_GB.UTF-8` | **`en_US.UTF-8`** | `LANG` on this machine |
| `kbdLayout` / `kbdVariant` | `gb` / `extd` | **`us` / empty** | US layout |
| `consoleKeymap` | `uk` | **`us`** | `/etc/vconsole.conf` |
| `hostname` | `nixos` | pick one, e.g. `singularity` | only `hosts/*` gets built |
| `username` | `railgun` | **`mamaroufaren`** | `install.sh` sets it from `$USER` |
| `games` | `false` | user's call | pulls steam/gamemode |

Two edits outside `variables.nix` are needed for this hardware:

1. `modules/hardware/video/nvidia.nix` → `hardware.nvidia.open = true`.
2. That same module forces `GBM_BACKEND=nvidia-drm` and `__GLX_VENDOR_LIBRARY_NAME=nvidia`,
   i.e. the dGPU becomes the render device. On a laptop that is hot and thirsty.
   Either accept it (simplest, matches upstream design) or switch to Intel-primary
   PRIME offload (`videoDriver = "intel"` + `hardware.nvidia.prime.offload.enable`).
   Decide after the first boot on battery.

## Install order

1. **Snapshot the control center first** — `~/hermes-control-center/scripts/snapshot.sh
   --with-sessions`, verify the push. See the `distro-hop` skill; nothing else in
   this plan is worth doing before that.
2. Copy `nix/variables.laptop.nix` off this repo (it is in git, so it survives).
3. Boot the NixOS ISO (25.11 or unstable, matching the flake), get networking.
4. `git clone https://github.com/Sly-Harvey/NixOS ~/nixos && cd ~/nixos`
5. `sudo ./install.sh` — selects the disk, GPU driver, creates partitions, installs.
   Then replace `hosts/<host>/variables.nix` with the laptop file and
   `sudo nixos-rebuild switch --flake .#<host>`.
6. Fix the driver: `open = true`, `nvidiaChannel = latest`, rebuild, reboot,
   confirm `nvidia-smi` and that Hyprland starts on the right output.
7. **Restore Hermes** (below), then `systemctl --user enable --now syncthing`
   only if wanted.
8. Rice pass: wallpaper (`SUPER+SHIFT+W`), bar, SDDM theme, fonts, monitor
   layout in `modules/desktop/hyprland/`.

## What Ryoku gave that NixOS will not

| Ryoku | NixOS equivalent |
|---|---|
| Ryoku Hub (GUI settings app) | edit `variables.nix`, `nixos-rebuild switch` — no GUI, and that is the deal |
| QS Bar / shell picker | `bar = waybar \| noctalia \| wayle`, `waybarTheme` |
| Ryoku shell keybinds | `modules/desktop/hyprland/` + its `variables.nix` |
| QS power menu | `wlogout` module |
| Ryoku notifications | `swaync` + `dunst` modules |
| `ryoku` skill in `~/.hermes` | dead on NixOS — `restore.sh --drop-ryoku` |

Practical consequence for how to answer desktop questions after the hop: there is
no Hub to point at. Name the file, the knob, and the rebuild command.

## Hermes on NixOS

Hermes installs into `~/.hermes` (not `/usr`), so it coexists with an immutable
system: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`, then
`./restore.sh --with-secrets --drop-ryoku`. Two differences from Arch:

- `/usr/bin/python3` and friends do not exist as writable paths; `config.yaml`
  absolute paths will be stale and `hermes doctor` will list them. Fix with
  `hermes config set`, never by hand.
- `~/.local/bin` must be on `PATH` — zsh is the flake's shell, so add it in
  `modules/core/zsh.nix` or `~/.zshrc` rather than relying on a profile drop-in.

## Arduino on NixOS

- The UNO R4 WiFi needs `/dev/ttyACM0` access: add the user to `uucp`-equivalent
  (`dialout`) or install udev rules from the `arduino` package; then re-login.
- `arduino-cli` + core `arduino:renesas_uno` install per-user into `~/.arduino15`,
  which survives rebuilds.
- Or use the upstream `dev-shells/platformio` flake for the same board.

## Risks

- **Blackwell driver**: if the open module still refuses, the fallback is
  `nvidiaChannel = "beta"` or pinning `nixpkgs` — expect the first hour of the
  rice to be driver work, not wallpaper.
- **Hybrid graphics**: `GBM_BACKEND=nvidia-drm` on a laptop can black-screen if
  the compositor picks the wrong connector; keep a TTY and the ISO around.
- **`nixos-unstable` moves**: `flake.lock` is pinned in the repo at d1c1ce4d; a
  fresh `nix flake update` later is a separate, testable change.
- **`install.sh` is destructive** to the selected disk. Confirm the target device
  twice; the control center snapshot from step 1 is the only undo.

## Verification after install

    nixos-rebuild switch --flake .#<host>    # exits 0
    nvidia-smi                               # 5070 Ti Mobile, driver ≥ 570
    hyprctl monitors                         # panel at expected resolution/refresh
    systemctl status sddm                    # graphical target up
    timedatectl                              # America/Los_Angeles
    rfkill list                              # hci0 not blocked
    hermes doctor                            # no stale paths, skills=67
    arduino-cli board list                   # UNO R4 WiFi when plugged in

Then update `docs/machine.md` and re-snapshot the control center. Log what diverged
from upstream here, so the next hop starts from truth.
