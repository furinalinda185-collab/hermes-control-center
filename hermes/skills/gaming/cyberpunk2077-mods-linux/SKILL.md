---
name: cyberpunk2077-mods-linux
description: Mod Cyberpunk 2077 on Linux/Proton.
---

# Cyberpunk 2077 modding on Linux / Proton

Game dir: `~/.local/share/Steam/steamapps/common/Cyberpunk 2077`, appid 1091500,
prefix `steamapps/compatdata/1091500`, exe in `bin/x64` (that dir is ReShade's base
path, not the game root).

## When to Use

Any request to mod, prettify, or speed up Cyberpunk 2077 on this machine: installing
ReShade / a shader preset, the RED4ext + CET + redscript framework stack, visual
overhauls (DreamPunk, LUTs, weather mods), LOD / render-distance or "performance"
mods, or answering "is this mod safe to install right now" after a game patch.

## Recheck live settings before tuning

Treat `~/cyberpunk-mods/README.md` as historical, not live state. Parse the current UserSettings.json and report relevant options before editing: the user may have switched DLSS to DLAA or disabled path tracing. Back up settings and active ReShade preset per tuning pass. Do not claim FPS gains without a comparable benchmark, or a pop-in fix without a repeatable driving test. Distinguish texture streaming, geometry LOD transitions, and traffic spawning; old DistanceBoost INI advice is not proof of effectiveness on a current patch. A post-process highlight rolloff cannot recover already clipped scene detail and affects HUD/neon too.

## Frameworks can fail to load *inside the game process* (ERROR_NOACCESS)

Proton Experimental 11.0-100 (2026-10) cannot load Cyberpunk mod DLLs from inside
the game process at all: `red4ext/RED4ext.dll` (release **and** the PR#154 dev
build) and CET's `cyber_engine_tweaks.asi` all abort with "No access to memory
location" / ASI error `998`, showing a modal MessageBox before D3D init and
leaving a 0-byte `red4ext/logs/*.log`. This is NOT the patch breakage (that one
dies 5-10 s after the logo with a populated log).

Confirmed fix: **switch the game to GE-Proton** (11-11 worked). The same DLLs
load immediately and RED4ext logs "successfully initialized" + "0 plugin(s)
loaded". Bisect cheaply if you doubt it: the identical DLL maps fine under the
distro `wine` in a throwaway prefix, so the download is fine and the fault is the
Proton build.

Two gotchas when installing a GE-Proton:

- **`user_settings.py` was silently ignored** — `import user_settings` fails
  inside the proton script and the failure is invisible (it logs to Steam's
  stdout). Do not trust it. Verify with
  `tr '\0' '\n' < /proc/<game pid>/environ | grep WINEDLLOVERRIDES`.
- **Steam launch options are encrypted**, so the reliable route is a *user-level*
  desktop entry at `~/.local/share/applications/steam.desktop` (copy it, do not
  edit the shipped one) with
  `Exec=env WINEDLLOVERRIDES="opengl32=n,b;dxgi=n,b;d3dcompiler_47=n,b;winmm,version=n,b" /usr/bin/steam %U`.
  Then verify by quitting Steam, `gtk-launch steam`, relaunching the game and
  reading the game process's `/proc/<pid>/environ`.
- Selecting GE-Proton for one appid: with Steam **closed**, insert into
  `~/.local/share/Steam/config/config.vdf` inside the `"Steam"` block of
  `InstallConfigStore > Software > Valve`:
  `"CompatToolMapping" { "1091500" { "name" "GE-Proton11-11" "config" "" "Priority" "250" } }`.
  Back the file up first; saves live in the same compatdata prefix, so switching
  Proton does not touch them.

After the host works, the plugins are a separate question: **pre-patch plugin
builds still crash the game.** A plugin compiled before the patch hangs at
`RED4ext: Loading plugin from .../<X>.dll` with a Wine "Program Error" window;
one crashing plugin blocks the whole boot. Quarantine them one by one
(`mv red4ext/plugins/<X> staging/`) to identify which are usable, and compare
release *dates* against the patch date rather than version numbers — the psiberx
mods publish on GitHub (`psiberx/cp2077-archive-xl`, `-tweak-xl`, `-codeware`).

## Pop-in / draw distance with no framework at all

`DistanceBoost` and `DecalsHideDistance` are real engine cvars — grep them out of
`bin/x64/Cyberpunk2077.exe` with `strings` before trusting a forum ini. Safe on
any patch: `engine/config/platform/pc/LODBoost.ini` with `[Streaming]` /
`DistanceBoost = 40.000000`, and `[LevelOfDetail] DecalsHideDistance = 100.0`
in `rendering.ini` (vanilla 40.0). Unknown sections are ignored silently, so a
wrong guess costs nothing.

Be honest about scope: this shifts streaming/decal range only. It does not
regenerate LOD levels, and a boot test proves nothing about pop-in — only the
user driving can confirm. Ask which pop-in they mean (textures resolving late,
geometry switching LOD, or traffic spawning) before tuning.

## Order of operations after a game patch

1. **Check the framework before installing anything.** Patch day breaks every
   RED4ext native plugin: the game silent-crashes 5-10 s after the CDPR logo and
   `RED4ext.log` ends right after initialisation. Query
   `api.github.com/repos/WopsS/RED4ext/issues?state=all` for "<patch> compatibility"
   and compare the latest release tag with the versions plugins were built for.
   A merged-but-unreleased fix is not a fix — the issue stays open with people
   posting hand-built zips that mostly do not work.
2. `redscript` + `CET` usually ship a patch-day build (release name literally says
   the game version); ArchiveXL/TweakXL/Codeware lag until RED4ext drops.
3. Archive-only content (LUTs, `.archive` packs) and ReShade work with no
   frameworks at all — those are what you can safely install on day one.

## ReShade on DX12 under Proton

Cyberpunk is DX12 -> ReShade hooks through **`dxgi.dll`** in `bin/x64`, not d3d11.

- Extract `ReShade64.dll` from the **add-on** setup (`ReShade_Setup_<v>_Addon.exe`)
  with `bsdtar -xf` — no 7zip needed. Rename to `dxgi.dll`.
- Overrides: `WINEDLLOVERRIDES="dxgi=n,b;d3dcompiler_47=n,b"`. Put them in
  `<Proton dir>/user_settings.py`. **That dict is shared by every game on that
  Proton build** — merge into the existing value (read the file first; a previous
  session may already have `opengl32=n,b` for another game). Never clobber it.
  Steam's launch options are the other route but recent Steam encrypts them in
  `userdata/*/config/localconfig.vdf`, so `user_settings.py` is the reliable path.
- Shaders: `crosire/reshade-shaders` default branch is `slim` and is trimmed — it
  has no SMAA/FXAA. `Mortalitas/GShade` `Shaders/` has the classic set. Mixing:
  take the core fxh (`ReShade.fxh`, `ReShadeUI.fxh`, `Macros.fxh`, `Blending.fxh`,
  `TriDither.fxh`) from **slim**, and only the effects you need from GShade. Old
  GShade effects using the `fastopt` attribute (`Deband.fx`, `Clarity.fx`) fail on
  ReShade 6 with `E5017 ... Unhandled attribute 'fastopt'` — use slim's `Deband.fx`
  and skip Clarity.
- `ReShade.ini` is tolerated when hand-written: `[GENERAL] EffectSearchPaths`,
  `TextureSearchPaths`, `PresetPath`, plus `[OVERLAY] ShowFPS=1` is a handy
  liveness probe.

## Verifying a shader layer actually renders

Do not trust "the DLL is in place". In order of cheapness:

1. `bin/x64/ReShade.log`: `loaded from ... dxgi.dll into ... Cyberpunk2077.exe`,
   `Redirecting D3D12CreateDevice`, swapchain `ResizeBuffers` with the real
   resolution, `Successfully compiled ... .fx` for every effect, and **zero**
   `ERROR`/`Failed to compile`.
2. `ShowFPS=1` -> screenshot (`grim` on Wayland) and look for the FPS number.
3. Prove the *preset* applies, not just the DLL: set one effect to an extreme
   (Vibrance 1.0), relaunch, screenshot, compare mean HSV saturation against a
   normal run. A real jump (~+35%) means techniques are live; identical numbers
   mean the preset never loaded even though the effect compiled.

The startup banner only shows for a few seconds — screenshot immediately after
the window appears, or you will only see game art.

ReShade's overlay (and its `Home` key) does not react to synthetic key events
(`wtype`, `hyprctl dispatch`, `xdotool -window`) — it reads the raw input path.
Verify with log lines and screenshot deltas, and leave the interactive A/B to the
user: bind `[INPUT] KeyEffects` to an easy key (F10 = `121,0,0,0`) so a single
keypress toggles the whole chain and the look can be judged in seconds.

## Launching from the CLI (needed to verify anything)

- Steam must already be running; use `steam -applaunch 1091500 --launcher-skip`
  (`--launcher-skip` bypasses REDprelauncher, which otherwise waits for a click).
- **Pass Steam's display env** or the game starts, spins at 400-500% CPU with no
  window ever mapping: `DISPLAY=:0 WAYLAND_DISPLAY=wayland-1 XDG_RUNTIME_DIR=/run/user/1000`.
  That hangs identically with or without ReShade, which makes it look like a
  ReShade crash — check for a window before blaming the shader layer.
- `DISPLAY=:0` alone is not enough to prove the game has one; query the
  compositor: `HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/hypr/) hyprctl clients -j`.
- Killing the game with `kill`/`kill -9` leaves a `reaper SteamLaunch AppId=1091500`
  process behind and Steam then **silently ignores further `-applaunch`** (and
  respawns `gameoverlayui -pid <dead pid>` in a loop). Kill the reaper too:
  `ps -eo pid,args | grep '[r]eaper SteamLaunch AppId=1091500'`.
- `pkill -f <string>` matches the agent's own shell command line and kills the
  shell (exit -15). Match with `/usr/bin/grep '[p]attern'` or `pkill -x <comm>`.

## Nexus is closed to plain HTTP

`curl` on nexusmods.com returns **403** (Cloudflare) and downloads need a logged-in
account, so there is no anonymous scripted path. Options: drive a real browser
session, use the user's login, or ask them to drop the zips somewhere local.
GitHub-hosted frameworks (RED4ext, CET, redscript, psiberx plugins) download fine.

## DreamPunk specifically

Patreon-exclusive (NextGen Dreams); no free build on Nexus. Three parts: main files
(LUT/weather archives + `options.json`), custom ReShade shaders (needs the add-on
build), and `NGD_Bridge` (a RED4ext plugin — drop `red4ext/plugins/NGD_Bridge` when
RED4ext does not support the running patch; the shaders still work).

**Paid mods stay paid.** Kemono/pawchive-style mirrors repost the creator's
subscriber-only files; do not fetch from them, and say so plainly in one line
without moralising. The two legitimate paths: the user downloads it from their own
subscription and hands over a local path, or you author an equivalent look yourself
(next section). Before offering alternatives, check what the mod actually is —
DreamPunk is a LUT + grading pack, so a hand-built ReShade grade covers most of it.

## Authoring a grade preset

A restrained chain beats a loud one here: Cyberpunk's art direction is already hard
graded, and path tracing amplifies banding in fog and sky. Working chain and start
values, also saved as `templates/reshade-preset.ini`:

    Deband (weber, t1 .006, t2 .030, iterations 2) -> Tonemap -> Curves -> Vibrance -> CAS
    Tonemap   gamma 1.0, exposure 0, saturation 1.03, bleach .05, defog .03
    Curves    Mode 2 (luma+chroma), Formula 1, Contrast .06
    Vibrance  .15 on luma
    CAS       Sharpening .35, Contrast 0

Effect params that exist (GShade vintage, all compile on ReShade 6): `Curves.fx`
= Mode / Formula / Contrast only (no per-channel tint); `Tonemap.fx` = Gamma /
Exposure / Saturation / Bleach / Defog / FogColor; `Levels.fx` = BlackPoint /
WhitePoint / HighlightClipping; `CAS.fx` technique is `ContrastAdaptiveSharpen`,
not `CAS`. Skill names in `Techniques=` must be the **technique**, not the file name.

Do not put SMAA in the active chain while DLSS/DLAA is on — it only softens an
already-reconstructed image. Keep a `*_Clean.ini` (deband+sharpen) and a `*_SMAA.ini`
next to the graded preset so the user can switch without re-authoring.

Bigger lever than any shader: read `UserSettings.json` (in the prefix, under
`AppData/Local/CD Projekt Red/Cyberpunk 2077`) and check `DLSS` / `ResolutionScaling`.
Ultra Performance at 1600p means an ~850x530 internal render — say so, price the
switch to Quality (~1700x1070), and only change it with the user's go-ahead.

## Staging pattern

Keep `~/cyberpunk-mods/{downloads,staging,backups}` plus one idempotent script that
extracts every zip into the game dir (`bsdtar -xf x.zip -C "$CP"` — all framework
zips are root-relative), merges the Proton overrides, and has `check` / `install` /
`info` / `uninstall` modes. `check` compares the latest RED4ext tag with the first
version that supports the running patch, so the user has one command instead of a
manual re-research after every CDPR update.
