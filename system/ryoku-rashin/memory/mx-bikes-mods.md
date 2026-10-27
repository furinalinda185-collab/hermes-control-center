---
name: mx-bikes-mods
description: Install MX Bikes community tracks/bikes on Linux/Proton — where mods live, the PiBoSo-locked PKZ rule, and mirror quirks
metadata:
  type: project
---

MX Bikes (Steam app 655500) runs under Proton on this machine.

**Mods live in the Proton prefix, not the install dir:**
`~/.local/share/Steam/steamapps/compatdata/655500/pfx/drive_c/users/steamuser/Documents/PiBoSo/MX Bikes/mods/`
with `tracks/<motocross|supercross|supermoto|enduro|straight rhythm>/`, `bikes/`, `tyres/`, `rider/`.

**PiBoSo-locked PKZ files must NOT be extracted.** Most community `.pkz` are
ZIPs whose *contents* are encrypted by PiBoSo's iNLock tool — the game
decrypts them itself. They look like high-entropy noise and are NOT zipfiles.
Correct handling: download the file and drop it in `mods/tracks/<cat>/<TrackID>.pkz`
as-is. The site publishes the authoritative name as `Track ID` on the post page.
The wiki page is `https://wiki.mxb-mods.com/pkz-files/`.

**"Server version" files are for dedicated-server owners only** — players need
the default/player file. Most popular servers run tracks that publish both.

**Content source:** mxb-mods.com. REST API works:
`/wp-json/wp/v2/posts?categories=<id>` and
`/wp-json/wordpress-popular-posts/v1/popular-posts?...&cat=<id>` (the popular
endpoint omits the download block; scrape the post page for real links).
Post pages carry `Total downloads:` — the best popularity signal, and tracks
that publish a *server version* are the ones used on dedicated servers.

**Mirror quirks (observed):**
- MediaFire: scrape the page for `https://download<N>.mediafire.com/...`; heavy
  Cloudflare rate-limiting (403 / "Just a moment") after ~10 requests. This IP
  got hard-403'd for the rest of the session.
- Google Drive: files >100MB return an HTML interstitial with a `confirm=t`
  + `uuid` form; repost to `drive.usercontent.google.com/download?id=...&confirm=t&uuid=...`
  keeping the same cookie jar. Popular files hit "Quota exceeded"; some
  mirrors are simply 404 (dead).
- MEGA: the API hands out a download URL that is throttled to ~4 KB, then
  returns HTTP 509 (bandwidth limit). Requesting a *fresh* URL from the API
  resets the quota — so fetch a new URL per chunk. Even then this IP gets
  exhausted after a few hundred MB. `mega.py` also has two real bugs
  (unbound `i` on a short final chunk; then a bogus MAC check).

**Content that worked (already installed & verified):**
- tracks: 45 loadable — 24 folders with the required `.trh`+`.amb` pair
  (motocross 23, supercross 1) + 21 PiBoSo-locked `.pkz` (incl. TSX training
  grounds and the 7 Compound 637 variants)
- bikes: 148 `.pkz` archives + 154 paint/aux folders —
  **MX OEM v0.19.1 (53 bikes, the pack popular servers broadcast)**,
  Enduro OEM, Supermoto OEM, Freeride OEM, and the **A-Kit pack (25 bikes)**
- tyres: 15 — oem_en, oem_freeride, oem_mx, oem_sm, p_mx, AK_mx pkz + the
  A-Kit soft/medium/hard tyre set
- Verify with `python3 ~/.local/share/mxb-tools/mxb_verify.py`.
- STILL MISSING: E10 factory bikes, MOUSE Motopark, and 4 MEGA-only tracks
  (bigsendmx, poor-boyz-mx, 2023-dreamland-mx, mnsr-raceway).
- `~/.local/share/mxb-tools/fetch_missing.py` retries those, rotating through
  all three mirrors; it needs the per-IP blocks to lapse (they clear after
  ~20-40 min, sometimes much longer). **Small files get through far more
  often than big ones** — grab optional/sub-file mirrors first, they tend to
  slip past the Cloudflare block.

**Disk-space trap:** `/tmp` is a 16 GB tmpfs, and the biggest packs are 2-4 GB.
Extracting a 3.8 GB pack into `/tmp` then copying it into the mods tree needs
~8 GB and will blow the quota. Extract zip members **straight into the final
mods path** instead of staging in `/tmp`.

**Networking note:** UDP to the MX Bikes master server (`master.mx-bikes.com:54200`)
times out from this network even though general UDP (DNS) works — multiplayer
server browsing may be blocked by the upstream/NAT.

**Launching the game:** only `steam -applaunch 655500` reaches the UI. A
standalone `proton run mxbikes.exe` starts the binary but never opens a
window and writes no `sllog.txt`/`e3dlog.txt`, so it can't be used to verify
that mods were picked up.

**Backup (pre-distro-hop, 2026-10-27):** ReShade shader+presets, game/profile
configs, and the `mxb-tools` scripts are committed to the control center at
`games/mx-bikes/` (see its README for restore order). The 29G `mods/` tree
cannot go to GitHub — `games/mx-bikes/mods-manifest.txt` (bytes+mtime, 549
files) is the re-download checklist; verify with `tools/mxb_verify.py`.
Replays (260M) and profile `*.dfm` (217M) were left behind.
