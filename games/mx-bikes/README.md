# MX Bikes — cross-distro backup

Backed up from the Arch/Ryoku install before a distro swap. Steam app **655500**,
runs under Proton. Everything here is what fits in a GitHub repo; the bulk of the
content does not and is covered by a manifest instead.

## What is in this directory

| Path | What | Restore target |
|---|---|---|
| `shader/reshade-shaders/` | ReShade shader pack (Shaders/ + Textures/, 1.4M) | `<game root>/reshade-shaders/` |
| `shader/opengl32.dll` | ReShade64.dll renamed — the OpenGL hook (5.2M) | `<game root>/opengl32.dll` |
| `shader/ReShade.ini` | ReShade config incl. `PresetPath=` | `<game root>/ReShade.ini` |
| `shader/PeK_MXB_*.ini` | Pek preset pack (10 presets) | `<game root>/` |
| `config/global.ini` + `config/controllers/` + `core.ini` `mxbikes.ini` `joysticks.cfg` `proxy_udp.ini` | game-level config | `<game root>/` |
| `config/profiles/` | profile: `profile.ini`, `controls.txt`, `records.ini`, `cockpit/`, `setups/`, `trainers/`, per-track `.ini`/`.trn` — **not** the 217M of `tracks/*/*.dfm` (telemetry caches, regenerate in-game) | `.../Documents/PiBoSo/MX Bikes/profiles/` |
| `tools/*.py` | the mod downloader/installer/verifier scripts (no venv) | `~/.local/share/mxb-tools/` |
| `mods-inventory.md` | **the reinstall list** — 42 tracks, 148 bikes in 5 packs, 6 tyre packs, with sizes, install form, and the reinstall procedure | — read before restoring |
| `mods-inventory.tsv` | same list machine-readable (kind, category, name, form, bytes, path) | — feed to the installer |
| `mods-manifest.txt` | every file under `mods/`: bytes, mtime, path (549 files, 29G) | — verification only |
| `mods-verify.txt` | `mxb_verify.py` output at backup time | — reference |

Game root = `~/.local/share/Steam/steamapps/common/MX Bikes/`
Mods root = `~/.local/share/Steam/steamapps/compatdata/655500/pfx/drive_c/users/steamuser/Documents/PiBoSo/MX Bikes/mods/`

## What is NOT in this repo (and why)

- **`mods/` — 29G** (tracks 18G, bikes 11G, tyres 171M). GitHub caps files at
  100MB and repos at ~5G, so the content can only come back by re-downloading.
  `mods-manifest.txt` is the checklist: after restore, run `tools/mxb_verify.py`
  and diff against it.
- **`replays/` — 260M**, **`cache/` — 2.0G** (regenerable), and the profile
  `*.dfm` files (217M, regenerate on first track load).
- Stock `bikes.pkz`/`tracks.pkz`/etc. — Steam reinstalls them.

## Restore order on the new distro

1. Reinstall the game + Proton via Steam (`steam -applaunch 655500` must work
   before adding mods; a bare `proton run mxbikes.exe` never opens a window).
2. Copy `config/` pieces to their targets (game root + `PiBoSo/MX Bikes/`).
   Re-join `uucp`/`dialout` group + re-login if hardware tools need `/dev/ttyACM0`.
3. Shader: copy `shader/opengl32.dll`, `reshade-shaders/`, `ReShade.ini` and the
   `PeK_MXB_*.ini` presets into the game root, then make Wine use the native
   opengl32 — per-Proton-version `user_settings.py`:
   `user_settings = {"WINEDLLOVERRIDES": "opengl32=n,b"}` (restart Steam).
   Verify from `ReShade.log`, not by eye: `Initializing crosire's ReShade`
   loaded from `OPENGL32.dll`, zero `Failed to compile`, no "uses unknown
   technique". Wayland: use borderless windowed, exclusive fullscreen may not hook.
4. Mods: copy `tools/*.py` to `~/.local/share/mxb-tools/`, create the venv
   (`pycryptodome` + `requests`), run `mxb_verify.py` to see what is missing,
   then re-download from mxb-mods.com with `mxb_dl.py` / `fetch_missing.py`.
   Rules that matter: locked `.pkz` go in **as-is** (never extracted), take the
   player file not the "server version", extract zip packs straight into the
   final mods path (never stage in `/tmp`, it is a 16G tmpfs). Mirror blocks
   (MediaFire/Drive/MEGA) clear after 20-40 min; `fetch_missing.py` rotates them.
   Known gaps at backup time: E10 factory bikes, MOUSE Motopack, and 4 MEGA-only
   tracks (bigsendmx, poor-boyz-mx, 2023-dreamland-mx, mnsr-raceway).
5. Diff `mods-manifest.txt` (path + byte size) against the restored tree.

Details live in the `mx-bikes-mod-installer` skill and
`system/ryoku-rashin/memory/mx-bikes-mods.md`.
