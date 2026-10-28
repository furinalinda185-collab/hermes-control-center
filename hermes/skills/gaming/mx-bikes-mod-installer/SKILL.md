---
name: mx-bikes-mod-installer
description: Install MX Bikes community tracks and bikes on Linux/Proton.
---

# MX Bikes community mod installation (Linux / Proton)

Use when installing MX Bikes community tracks/bikes, or when mxb-mods.com
downloads fail or return files that won't open.

Tooling lives in `~/.local/share/mxb-tools/` (venv at `venv/`, MEGA key decoding
needs `pycryptodome` + `requests` inside it). Scripts:

- `mxb_dl.py` — multi-host downloader: MediaFire, Google Drive (file + folder),
  MEGA, Dropbox, 1drv. `download(url, out) -> (ok, info)`.
- `mega_dl.py` — standalone MEGA downloader (chunked, AES-CTR decrypt).
- `mxb_parse.py` — scrape a mxb-mods.com post into `{downloads, beta, files[]}`
  where each file has `kind` in `default` / `optional` / `server`.
- `mxb_plan.py` — pick popular items from the ranked list.
- `mxb_cats.py` — map posts to the game's `mods/tracks/<category>` folder.
- `mxb_install2.py` — the installer: `mxb_install2.py plan.json track|bike`.
- `mxb_verify.py` — report what is installed (valid track folders, locked PKZs,
  bike counts).
- `fetch_missing.py` — patient retry loop for mirrors that block per-IP.

## Where mods go (Proton prefix, NOT the game dir)

`~/.local/share/Steam/steamapps/compatdata/<appid>/pfx/drive_c/users/<user>/Documents/PiBoSo/MX Bikes/mods/`
- `tracks/motocross|supercross|supermoto|enduro|straight rhythm/`
- `bikes/`, `tyres/`, `rider/`

For MX Bikes the appid is 655500.

## Rule 1 — locked PKZs must NOT be extracted

Most community `.pkz` are ZIPs whose *contents* are encrypted by PiBoSo's
iNLock tool. The game decrypts them itself. They are **not** zipfiles and look
like high-entropy noise.

Correct handling: download the file and place it in the mods folder **as-is**.
Do not try to unzip it, do not treat the failure as a corrupt download.
Wiki: https://wiki.mxb-mods.com/pkz-files/

The game expects the track's own name. The site publishes it as `Track ID` on
the post page — use that for the filename, not the generic link label
("Track", "Track Link", "Main pkz" are placeholders).

## Rule 2 — take the PLAYER file, never the "server version"

Posts publish a "Server version" for dedicated-server owners. Players need the
default/player file. Downloading the server version gives a black screen.

## Rule 3 — pick popular items by real signals

`Total downloads:` on the post page is the best popularity number. A published
**server version** is the strongest signal that a track runs on dedicated
servers. Rank by (has server version, downloads).

## Mirror handling

- **MediaFire**: two different walls, and they need different answers.
  1. *Cloudflare 403* on the file page: the download host itself is fine, so
     fetch the page through a text-extraction proxy and use the link it
     exposes — `https://r.jina.ai/<mediafire-url>`. Send
     `X-Return-Format: html`, because the default markdown rendering
     truncates the page before the download button on large files. Strip any
     `[...]` suffix from the extracted link. This works for files that have
     no CAPTCHA (Compound 637 came down this way).
  2. *CAPTCHA* on `download_repair.php` ("Help us verify you're human"):
     MediaFire serves this for some popular files, and it needs a human.
     No script can pass it — those files must be fetched from a mirror that
     doesn't gate them (MEGA / Google Drive) or by hand. A MediaFire direct
     link 302-redirects to `download_repair.php?...&ip=<your ip>`, so the
     link is IP-bound and short-lived too: resolve and download immediately,
     and always verify the payload magic (PK / Rar! / 7z) instead of trusting
     the HTTP status.
- **Google Drive**: >100MB files return an HTML interstitial with a
  `confirm=t` + `uuid` form. Repost to
  `drive.usercontent.google.com/download?id=...&confirm=t&uuid=...` **using the
  same cookie jar**. Very popular files hit "Quota exceeded"; some mirrors are
  404 (dead). Folder links: list via
  `drive.google.com/embeddedfolderview?id=<id>#list`, grab `id="entry-<id>"`.
- **MEGA**: two separate traps.
  1. A plain GET of a large file returns **HTTP 509**, while a **Range**
     request for the same file returns 206. So always download in Range
     windows, requesting a **fresh API URL per window** — the API still
     answers while the storage GET is throttled.
  2. The quota attached to a fresh URL is **unpredictable**: sometimes 32 MiB
     is served, sometimes only 4 KiB, and it can flip between calls. So make
     the window size adaptive: start at 32 MiB, halve/quarter it on a 509,
     and grow it back after a success. Accept a short response (206 with
     fewer bytes than requested) and continue from where it stopped rather
     than treating it as a failure.
  3. `mega.py` (pip) silently leaves a **0-byte file** when the GET is
     throttled, so always compare the result against the size the API
     reports and treat a short/empty file as a failure. Its other two bugs
     are an unbound `i` on a final chunk <16 bytes and a MAC check that
     raises on a valid file — patch both.
  4. Keys are URL-safe base64 **without padding**: translate `-_` → `+/` and
     pad before decoding. The key is 8 words.
  5. To resume a partial file, AES-CTR is positional: rebuild the counter
     with `initial_value = base + written//16` (verified to match the
     full-stream keystream). `Counter.new()` returns a dict in current
     pycryptodome — there is no `.seek()`.
  Beware bare `except:` blocks around a closure that references an
  out-of-scope variable — that silently hides the real error and looks
  like a network failure.

## Diagnosing "black screen / nothing works"

Audit the mods tree before touching graphics settings; these are the causes that
actually turn up, in order of how often they explain the symptom:

- **Extracted server PKZ.** A player track folder has a big `.map` (200-700 MB)
  plus object `.edf`/`.tcl`/`.dds`. A *server* build has only
  `.trh .rdf .amb .ini .ssc .cfg` and **no `.map`** — extract it and the game
  shows a black screen. Fingerprint: folder is tens of MB, not hundreds. Posts
  often label the player link and the server link separately, and both may use
  the same filename (`Outpost_Nevada.pkz` appears twice). Always install the
  player build.
- **Layout copied out of its parent.** Files named `<name>.tcl`, `start.tcl`,
  `track.tcl` with no `.map`/`.trh` of their own are a *layout*: it renders only
  from inside `<parent track>/<layout>/`. A copy at `tracks/<cat>/<name>/`
  black-screens. The `.ini` `name =` names the parent ("Outpost: Nevada - Outer Trail").
- **HTML saved as `.pkz`.** Scan every `.pkz` for a first bytes of
  `<!DOCTYPE`/`<html` — mirror error pages get saved under the right filename.
- **Junk in `mods/bikes/`.** Extracted model archives leave `*.fbm/` texture
  folders and a stray `paints/` at the bikes root; a mis-unpacked archive leaves
  `bikes/<Name>/mods/bikes/<Bike>/paints/*.pnt` (keep the `.pnt`, drop the wrapper).
  A bike folder with a `.bike` but no `model.edf` and a Unity/foreign container
  (`.TDB` starting `nUtiSFy`) is not an MX Bikes bike — quarantine it.
- **Loose tyre files at `mods/tyres/` root.** beta21 added in-game tyre
  selection; duplicated `.tyre`/`.cfg` sitting beside `<pack>.pkz` (which already
  contains them) makes stock bikes fail to spawn. Only `<pack>.pkz` and
  `<pack>/paints` belong there.

Reference formats: stock `bikes.pkz`, `tyres.pkz`, `misc.pkz`, `ui.pkz` are
**plain zips** (readable with `zipfile`) while OEM/most community bike pkz are
iNLock-encrypted. A stock bike `.ini` has `tyres_type = mx` and no `version`;
mod bikes declare `version =` (e.g. `190303` = beta19 era) and `cat =` (garage
class). `p_mx`/`m_sm` are the game's own tyre packs (ids stock bikes select by
`tyres_type`) — a `mods/tyres/p_mx.pkz` is an *override* of a stock pack.

## ReShade on Proton (MX Bikes is OpenGL)

"Install a shader" for MX Bikes means ReShade. Hooks are `opengl32.dll`:

1. Extract `ReShade64.dll` from the official setup exe — `bsdtar -xf` works,
   no 7zip needed — and copy it to the game dir as `opengl32.dll`.
2. Wine prefers its builtin opengl32, so set `WINEDLLOVERRIDES="opengl32=n,b"`.
   Without a Steam restart use `<Proton dir>/user_settings.py`
   (`user_settings = {"WINEDLLOVERRIDES": "opengl32=n,b"}`); it is per-Proton
   version, not per game, but `n,b` only matters to games shipping their own
   opengl32.dll. `Proton` appends its own overrides afterwards, so this composes.
3. Shader packs: `reshade-shaders` branch `slim` is trimmed to 13 effects and
   branch `nvidia`/`legacy` to classic renamed files; presets expect the old
   names (`LumaSharpen.fx`, `NFAA.fx`, `AdaptiveTonemapper.fx`, `ACES.fxh`,
   `Sepia.fx`) which live in `Mortalitas/GShade` (`Shaders/` raw). qUINT comes
   from `martymcmodding/qUINT`. Do not mix packs that include different
   `qUINT_common.fxh` versions — those effects fail with "do not mix file versions".
4. Presets: mxb-mods "ReShade Presets" category. Pek's pack is served straight
   from the site's `wp-content/uploads` (no mirror wall). Drop presets in the game
   root and point `PresetPath=` in `ReShade.ini` at one.
5. Verify from `ReShade.log` in the game root, not by eye: it must show
   `Initializing crosire's ReShade version` loaded from `OPENGL32.dll`, zero
   `Failed to compile`, and **no** "uses unknown technique" for the active preset.
   Missing texture warnings repeat every frame — remove the effect that wants them.

Wayland: ReShade may not hook in exclusive fullscreen; use borderless.

## Verification

`python3 mxb_verify.py` reports extracted track folders (valid = has `.trh` +
`.amb`), locked PKZ entries, and bike counts. The game itself must be started
through Steam (`steam -applaunch 655500`); run directly under Proton it exits
without loading anything.

## Preserving an install (backup before a wipe, reinstall afterwards)

A full content tree runs tens of GB (tracks + bikes + tyres measured 29G), so it
never goes into a git repo — GitHub caps files at 100MB and repos at ~5G. Back up
what is not re-downloadable and record enough to rebuild the rest:

- **Record the source URL at install time.** The filesystem records what is
  installed and never where it came from; once the installer's temp plans are
  gone a post URL is unrecoverable and a reinstall degrades into a by-name
  re-search on mxb-mods.com for every item. Keep an appendable plan/inventory
  (post URL + `Track ID` + pack name + install path) as you install.
- **Two artifacts, both needed.** A *manifest* proves a restored tree matches:
  `find mods -type f -printf '%s\t%TY-%Tm-%TdT%TH:%TM\t%P\n' | sort -t$'\t' -k3`.
  An *inventory* is what a future session actually installs from: one row per
  install unit (kind, category, name, form, bytes, path). Manifest alone cannot
  tell anyone what to download.
- **Group bikes into packs by filename prefix** — `MX*OEM`, `SM*OEM`, `EN*OEM`,
  `FREERIDE_`, `AK ` — because the download unit is the pack, not the ~150
  individual `.pkz`. Tyres work the same way: six `mods/tyres/*.pkz` are six pack
  downloads, and `p_mx`/`oem_*` are overrides of stock packs.
- **Leave out what regenerates**: `profiles/<profile>/tracks/*/*.dfm` (~16MB of
  per-track telemetry each), `cache/`, and replays. Keep `profile.ini`,
  `controls.txt`, `records.ini`, `cockpit/`, `setups/`, `trainers/`.
- For this machine the control center carries it at `games/mx-bikes/` —
  `README.md` (restore order), `mods-inventory.md`/`.tsv` (reinstall list),
  `mods-manifest.txt` (per-file checklist), `tools/` (these scripts). The repo
  side of the procedure — how to copy, manifest and verify it remotely — is the
  `game-preservation` reference inside the `distro-hop` skill (not this one).

## Disk-space trap

`/tmp` is a small tmpfs (16 GB here) and the biggest packs are 2-4 GB.
Extracting a 3.8 GB pack into `/tmp` and then copying it into the mods tree
needs ~8 GB and will die with `OSError: [Errno 122] Disk quota exceeded`.
Extract zip members **straight into the final mods path** — never stage a big
pack in `/tmp`.

## Getting past the mirror blocks

All three hosts block this IP aggressively and independently:

- MediaFire (Cloudflare 403) clears on its own after roughly 20-40 minutes.
  **Small files slip through far more often than big ones** — when a post
  offers optional/secondary mirrors (model files, tyres, templates), fetch
  those first; they tend to get through while the main pack is still blocked.
- Google Drive: "Quota exceeded" is file-popularity-based, not IP-based, and
  can last up to 24 hours for very popular files.
- MEGA: HTTP 509 until the IP quota resets.

Run `fetch_missing.py` with a long ROUNDS/SLEEP so it keeps rotating through
every mirror; the blocks lift eventually and the download then succeeds.
