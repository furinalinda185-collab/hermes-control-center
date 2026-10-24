# Ryoku desktop map

Where every subsystem's config lives, the binary that owns it, and how to
reload it. Read this before searching the filesystem. Generated: the content
between the markers is overwritten on every reindex.

<!-- rashin:generated:begin -->
## Acting on this desktop

Answer a "how do I" question GUI-first: when the change has a GUI path (a
Ryoku Hub page, the wallpaper/theme picker, or QS Bar Settings; see the GUI
map below), name that path first with its keybind, then give the command as
the headless fallback. You still act through commands (`ryoku`, `ryoku-shell`,
`ryoku-hub`, `ryogami`, `ryoku wm act`), never by editing shipped files. The
`ryoku` skill is the contract for that: `SKILL.md` (rules and the command
catalogue), `gui.md` (the GUI map), `bar.md` (the QS Bar model), `plugins.md`
(how a new widget is written and installed).
Read them at `/usr/share/ryoku/skills/ryoku/` (also linked into each agent's skills dir as `ryoku`).

## GUI map

Most desktop changes have a GUI surface; name it first, then the command as
the headless fallback. Compositor-gated pages are hidden when the running
window manager cannot back them, so a row here may not appear on every box.

| Want to change | Open | Deep link | Command behind it |
|---|---|---|---|
| Wallpaper or theme | Wallpaper picker (Super+W), or the bar Wallpaper widget | - | `ryogami wallpaper ui` |
| Bar or dock layout | QS Bar Settings | - | `ryoku-shell bar settings` |
| Launch an app | App launcher (Super+Space) | - | - |
| Ryoku Hub: General | Super+comma | `ryoku-shell hub open global` | - |
| Ryoku Hub: Updates | Super+comma | `ryoku-shell hub open updates` | - |
| Ryoku Hub: Displays | Super+comma | `ryoku-shell hub open displays` | - |
| Ryoku Hub: Connections | Super+comma | `ryoku-shell hub open connections` | - |
| Ryoku Hub: Input | Super+comma | `ryoku-shell hub open input` | - |
| Ryoku Hub: Graphics & Power | Super+comma | `ryoku-shell hub open gpu` | - |
| Ryoku Hub: Animations | Super+comma | `ryoku-shell hub open animations` | - |
| Ryoku Hub: Lockscreen | Super+comma | `ryoku-shell hub open lockscreen` | - |
| Ryoku Hub: Window Manager | Super+comma | `ryoku-shell hub open windowmanager` | - |
| Ryoku Hub: Plugins | Super+comma | `ryoku-shell hub open plugins` | - |
| Ryoku Hub: Bar Studio | Super+comma | `ryoku-shell hub open bar-studio` | - |
| Ryoku Hub: Desktop | Super+comma | `ryoku-shell hub open desktop` | - |
| Ryoku Hub: Widgets | Super+comma | `ryoku-shell hub open widgets` | - |
| Ryoku Hub: App Launcher | Super+comma | `ryoku-shell hub open launcher` | - |
| Ryoku Hub: Keybinds | Super+comma | `ryoku-shell hub open keybinds` | - |
| Ryoku Hub: Performance | Super+comma | `ryoku-shell hub open performance` | - |
| Ryoku Hub: Session | Super+comma | `ryoku-shell hub open session` | - |
| Ryoku Hub: Recording | Super+comma | `ryoku-shell hub open recording` | - |
| Ryoku Hub: Dictation | Super+comma | `ryoku-shell hub open dictation` | - |
| Ryoku Hub: Add-ons | Super+comma | `ryoku-shell hub open addons` | - |
| Ryoku Hub: Rashin | Super+comma | `ryoku-shell hub open rashin` | - |

Idle and power timeouts live under Graphics & Power (`gpu`).

## Subsystem map

| Subsystem | Config path | Owner | Reload |
|---|---|---|---|
| hyprland (window manager) | ~/.config/hypr/ | hyprland config | ryoku wm act config.reload |
| Shell surfaces (pill, sidebar, ryoshot, widgets, launcher, hub) | ~/.config/quickshell/ | ryoku-shell daemon | ryoku reload |
| Terminal | ~/.config/kitty/ | kitty | relaunch kitty |
| Shell + prompt | ~/.config/{fish,bash,zsh}/, ~/.config/starship.toml | fish, bash, or zsh; starship | open a new shell |
| Editor | ~/.config/nvim/ | Neovim (LazyVim) | relaunch nvim |
| File manager | ~/.config/yazi/ | yazi | relaunch yazi |
| Ryoku CLI | binary `ryoku`; state ~/.local/state/ryoku/ | ryoku | ryoku update \| rollback \| status \| materialize \| reload |
| Hub state | ~/.config/ryoku/hub.toml | ryoku-hub (Ryoku Settings) | written by Ryoku Settings; no reload |
| Theme + colour source | ~/.config/ryoku/theme.json | ryoku-hub | ryogami wallpaper repaint |
| Palette | ~/.cache/ryoku/colors.json | ryoku-shell daemon (matugen) | ryogami wallpaper repaint |
| Packages | pacman + yay database | pacman, yay | ryoku update |
| System vault | ~/.local/share/ryoku/rashin/ | ryoku-rashin | ryoku-rashin index |

## Ryoku package versions

- ryoku-shell 0.75.3.r3968.gcfd8899-1
- ryoku-hub 0.75.3.r3968.gcfd8899-1
- ryoku 0.75.3.r3968.gcfd8899-1
- ryoku-blobs 0.75.3.r3968.gcfd8899-1
- ryoku-desktop 0.75.3.r3968.gcfd8899-3
- ryoku-rashin 0.75.3.r3968.gcfd8899-1

## Bar and dock

<!-- rashin:generated:begin bar -->
The default bar is QS Bar (`qsbar`). Its layout is data in
`~/.config/ryoku/shell.json` under `qsbar.layout`:

```json
"qsbar": { "layout": { "version": 1,
  "left": [ids], "center": [ids], "right": [ids] } }
```

An entry is a widget id (a built-in below, or an installed plugin's id).
Placement and visibility are separate: a built-in renders when
`qsbar.widgets[<key>]` is true (a blank key is always shown); a plugin when
`~/.config/ryoku/plugins.json` has it `enabled` with `host: "topbarGlyph"`.
The shell daemon is the only writer of `shell.json`; change the bar with
`ryoku-shell bar ...`, never by editing the file.

### Built-in widgets

| id | label | visibility key | settings keys |
|---|---|---|---|
| launcher | Launcher | (always) | (none) |
| workspaces | Workspaces | (always) | (none) |
| status | Status | status | (none) |
| memory | Memory | memory | (none) |
| cpu | CPU | cpu | (none) |
| volume | Volume | volume | audioBoost |
| ai | AI usage | claude | aiTools |
| clock | Clock | (always) | clock12h, weatherImperial, weather |
| media | Now playing | mpris | mprisBarStyle |
| quick | Quick | quick | (none) |
| network | Network | network | (none) |
| battery | Battery | battery | (none) |
| brightness | Brightness | brightness | (none) |
| power | Power | power | (none) |
| bluetooth | Bluetooth | bluetooth | (none) |
| cputemp | CPU temperature | cpuTemperature | barTemperatureSource |
| gpu | GPU | gpu | (none) |
| storage | Storage | storage | (none) |
| layout | Keyboard layout | layout | (none) |

Source: `~/.config/quickshell/shell/modules/bar/barstyles/qsbar/core/widgets.json`.

### Commands

```
bar list [--json] | catalog [--json]
bar move <id> --section left|center|right [--index N | --before <id> | --after <id>]
bar show <id> | hide <id> | set <id> <key> <value>
bar position top|bottom | form full|fit|dock|notch|islands | defaults | settings [route]
dock show|hide | edge auto|top|bottom|left|right | autohide on|off | pin <app>|unpin <app> | list [--json]
```

Run these through `ryoku-shell` (e.g. `ryoku-shell bar move clock --section right`).
Installed plugins live in `~/.local/share/ryoku/plugins/<id>/`; their bar
placement and settings persist in `~/.config/ryoku/plugins.json`.

### Adding a widget

A widget that is not in the table above is a plugin, never an edit to the
shipped QML under `~/.config/quickshell/` or `/usr/share/ryoku/`. Read the
`ryoku` skill's `plugins.md` for the contract (manifest.json, service/Main.qml,
content/Widget.qml, host `topbarGlyph`), write it in its own directory, then:

```
ryoku plugin validate <dir>
ryoku plugin add <dir-or-git-url> --bar --yes
```

It lands on the bar and under QS Bar Settings > Community (`ryoku-shell bar
settings community`); `ryoku plugin remove <id>` takes it off again, and
`ryoku plugin share <id>` (only when the user asks to publish) opens the
Ryostore pull request that lists it for everyone.
<!-- rashin:generated:end bar -->
<!-- rashin:generated:end -->
