# Ryoku source map

The Ryoku monorepo that produced this system: where its source lives and
what each part does. Generated: the content between the markers is
overwritten on every reindex.

<!-- rashin:generated:begin -->
## Checkout

- Commit: cfd8899d (HEAD)
- Committed: 2026-09-26
- Indexed: 2026-09-26 16:17

## Layout

| Path | Files | Purpose |
|---|---|---|
| `ryoku/` | 3680 | the desktop: apps, hyprland (Lua), shell UI, hub, rashin, assets |
| `release/` | 268 | packaging: PKGBUILDs, the [ryoku] repo, keyring |
| `tests/` | 106 | standalone CI check scripts |
| `system/` | 96 | machine definition: boot chain, hardware policy, package sets |
| `installation/` | 87 | how a machine is built: TUI, backend installer, ISO |
| `docs/` | 34 | the guides |
| `ryoku-shell-installer/` | 28 | no-ISO converter for existing Arch installs |
| `bin/` | 26 | repo tooling and CI checks |
| `.githooks/` | 4 | commit and push gates |

## Key entry points

| Concern | Path |
|---|---|
| Hyprland config entry (Lua) | `ryoku/hyprland/hyprland.lua` |
| Shell daemon (Go) | `ryoku/shell/ipc/` |
| Settings app backend | `ryoku/hub/backend/` |
| Settings app UI (QML) | `ryoku/hub/quickshell/` |
| User CLI | `ryoku/cli/` |
| Rashin (this system) | `ryoku/rashin/` |
| Dev deploy loop | `ryoku/shell/deploy.sh` |
| Installer backend | `installation/backend/` |
| Package builds | `release/packages/` |

## Docs

- `docs/adding-a-window-manager.md` Adding a window manager
- `docs/bar.md` Frame bars
- `docs/barstyles.md` Bar styles
- `docs/cli.md` The `ryoku` command
- `docs/compositors.md` Compositors
- `docs/config-import.md` Config import
- `docs/conventions.md` Conventions
- `docs/development.md` Development
- `docs/frame.md` The frame
- `docs/hyprland-plugins.md` Hyprland compositor plugins
- `docs/i18n.md` Translation
- `docs/installation-hardware.md` Installing on real hardware
- `docs/kernels.md` Kernels
- `docs/launcher.md` The launcher
- `docs/plugins.md` Writing a Ryoku shell plugin
- `docs/power.md` Power, heat, and battery
- `docs/preinstalled.md` What ships preinstalled
- `docs/profile.md` The Profile plate
- `docs/rashin-terminal.md` Rashin in the terminal
- `docs/rashin.md` Ryoku Rashin
- `docs/roadmap.md` Ryoku Roadmap
- `docs/ryoku.md` What Ryoku is
- `docs/stage.md` Ryostage (舞台)
- `docs/store.md` The store
- `docs/structure.md` Repository structure
- `docs/theming.md` Theming: how colour reaches an app
- `docs/ui-ux.md` UI and UX
- `docs/updates.md` Updates and delivery
<!-- rashin:generated:end -->
