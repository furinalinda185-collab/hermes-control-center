# MX Bikes — installed mod inventory (reinstall list)

Captured 2026-10-27 from the live mods tree before the distro hop.
Companion files in this directory: `mods-manifest.txt` (all 549 files, exact bytes +
mtimes, the verification checklist), `mods-verify.txt` (`mxb_verify.py` output at capture),
`tools/` (the downloader/installer/verifier scripts), `README.md` (restore order).

Totals: **42 tracks** (motocross: 21 extracted + 20 locked pkz; supercross: 1
extracted), **148 bikes in 5 packs**, **6 tyre packs** — 18.77G tracks, 10.19G
bikes, 178M tyres, 29G on disk.

Install units are the *packs*, not the individual bikes: five bike downloads and six
tyre downloads reproduce all 148 bikes / 6 packs. Tracks are one download each.

## Tracks — motocross (21 extracted, 20 locked pkz)

Extracted = a folder the game loads directly (`.trh` + `.amb` present); these came
from a zip that was unpacked straight into the mods path. Locked pkz = PiBoSo-
encrypted archive, copied in as-is and decrypted by the game itself.

| Track | Form | Size |
|---|---|---|
| Across The Sea | extracted | 617M |
| Cairo GP | extracted | 504M |
| Cappadocia Hills | extracted | 703M |
| Country Side | extracted | 493M |
| FuryMXFacility | extracted | 455M |
| Highlands MX | extracted | 634M |
| Impact Designs Raceway | extracted | 659M |
| Into the Wild | extracted | 462M |
| Iron Ridge | extracted | 517M |
| KMX-Mesquite MX | extracted | 649M |
| KeLLz_Washougal | extracted | 689M |
| Lake_Elsinore_MX_By_Ps | extracted | 534M |
| Outpost Nevada | extracted | 476M |
| Raska MX | extracted | 330M |
| Senderville | extracted | 215M |
| SwamplandMX | extracted | 622M |
| Temecula Creek | extracted | 856M |
| The Hideout | extracted | 713M |
| The Island | extracted | 722M |
| arcolamx | extracted | 327M |
| hurrenmx.week.challenge | extracted | 429M |
| CWunadilla24 | locked pkz | 368M |
| Compound 637 EX TRACK | locked pkz | 169M |
| Compound 637 FLAT TRACK | locked pkz | 169M |
| Compound 637 MX TRACK | locked pkz | 169M |
| Compound 637 NORTH SX TRACK | locked pkz | 169M |
| Compound 637 PIT BIKE TRACK | locked pkz | 170M |
| Compound 637 SAND TRACK | locked pkz | 170M |
| Compound 637 SOUTH SX TRACK | locked pkz | 170M |
| Glen Helen Raceway 2018 | locked pkz | 539M |
| HM_swedish_midsummer_carnage_2 | locked pkz | 286M |
| Highside Motocross | locked pkz | 268M |
| KMX - Ponca City | locked pkz | 701M |
| KMX-Spring a Ding | locked pkz | 557M |
| Quarry Basin | locked pkz | 513M |
| ShmeezeVille | locked pkz | 209M |
| Silver Valley MX Park | locked pkz | 473M |
| Sleepy Hollow MX | locked pkz | 423M |
| TSX | locked pkz | 211M |
| kellz-fox-raceway-2023 | locked pkz | 465M |
| kellz-redbud-2023 | locked pkz | 415M |

## Tracks — supercross (1 extracted)

| Track | Form | Size |
|---|---|---|
| CJ - CJSX R1 | extracted | 553M |

`enduro/` and `supermoto/` exist but are empty — no mods installed there.

## Bikes — 5 packs, 148 bikes

### MX OEM (v0.19.1) — 53 bikes, 3.78G

Installed as one avatar per bike: `bikes/<bike>.pkz` (locked archive) plus a
`bikes/<bike>/` paints folder. If the pack ships as one archive, that single
download is what to grab.

`MX1OEM_1996_Honda_CR250`, `MX1OEM_1997_Honda_CR250`, `MX1OEM_2002_Kawasaki_KX250`, `MX1OEM_2003_Suzuki_RM250`, `MX1OEM_2023_Fantic_XX250`, `MX1OEM_2023_Honda_CRF450R`, `MX1OEM_2023_Husqvarna_FC_350`, `MX1OEM_2023_Husqvarna_FC_450`, `MX1OEM_2023_Husqvarna_TC_250`, `MX1OEM_2023_KTM_250_SX`, `MX1OEM_2023_KTM_350_SX-F`, `MX1OEM_2023_KTM_450_SX-F`, `MX1OEM_2023_Kawasaki_KX450`, `MX1OEM_2023_Suzuki_RM-Z450`, `MX1OEM_2023_TM_MX_144`, `MX1OEM_2023_TM_MX_250`, `MX1OEM_2023_TM_MX_300_Fi`, `MX1OEM_2023_TM_MX_450_Fi`, `MX1OEM_2023_Yamaha_YZ250`, `MX1OEM_2023_Yamaha_YZ450F`, `MX1OEM_2024_Beta_RX_450`, `MX1OEM_2024_GasGas_MC_250`, `MX1OEM_2024_GasGas_MC_350F`, `MX1OEM_2024_GasGas_MC_450F`, `MX1OEM_2025_Fantic_XXF_450`, `MX1OEM_2025_Triumph_TF_450-RC`, `MX2OEM_1996_Honda_CR125`, `MX2OEM_2002_Kawasaki_KX125`, `MX2OEM_2003_Suzuki_RM125`, `MX2OEM_2023_Fantic_XX125`, `MX2OEM_2023_Honda_CRF250R`, `MX2OEM_2023_Husqvarna_FC_250`, `MX2OEM_2023_Husqvarna_TC_125`, `MX2OEM_2023_KTM_125_SX`, `MX2OEM_2023_KTM_250_SX-F`, `MX2OEM_2023_Kawasaki_KX250`, `MX2OEM_2023_Suzuki_RM-Z250`, `MX2OEM_2023_TM_MX_125`, `MX2OEM_2023_TM_MX_250_Fi`, `MX2OEM_2023_Yamaha_YZ125`, `MX2OEM_2024_GasGas_MC_125`, `MX2OEM_2024_GasGas_MC_250F`, `MX2OEM_2024_Triumph_TF_250-X`, `MX2OEM_2024_Yamaha_YZ250F`, `MX2OEM_2025_Fantic_XXF_250`, `MX3OEM_2021_KTM_KX_500`, `MX3OEM_2022_Beta_300_RX`, `MX3OEM_2023_KTM_300_SX`, `MX3OEM_2023_TM_MX_300`, `MX3OEM_2023_TM_MX_530_Fi`, `MX3OEM_Service_Honda_CR500AF`, `MXEOEM_2018_Alta_Redshift_MXR`, `MXEOEM_2023_Stark_VARG`

### Supermoto OEM — 26 bikes, 2.00G

Installed as one avatar per bike: `bikes/<bike>.pkz` (locked archive) plus a
`bikes/<bike>/` paints folder. If the pack ships as one archive, that single
download is what to grab.

`SM1OEM_2023_Honda_CRF450R`, `SM1OEM_2023_Husqvarna_FS_450`, `SM1OEM_2023_KTM_450_SMR`, `SM1OEM_2023_Kawasaki_KX450`, `SM1OEM_2023_Suzuki_RM-Z450`, `SM1OEM_2023_TM_SMK_450_Fi`, `SM1OEM_2023_Yamaha_YZ450F`, `SM1OEM_2024_Beta_RX_450`, `SM1OEM_2024_GasGas_MS_450F`, `SM1OEM_2025_Fantic_XXF_450`, `SM1OEM_2025_Triumph_TF_450-RC`, `SM2OEM_2023_Honda_CRF250R`, `SM2OEM_2023_Husqvarna_FS_250`, `SM2OEM_2023_KTM_250_SMR`, `SM2OEM_2023_Kawasaki_KX250`, `SM2OEM_2023_Suzuki_RM-Z250`, `SM2OEM_2023_TM_SMK_250_Fi`, `SM2OEM_2024_GasGas_MS_250F`, `SM2OEM_2024_Triumph_TF_250-X`, `SM2OEM_2024_Yamaha_YZ250F`, `SM2OEM_2025_Fantic_XXF_250`, `SMCOEM_1996_Honda_CR250`, `SMCOEM_2002_Kawasaki_KX250`, `SMCOEM_2003_Suzuki_RM250`, `SMEOEM_2018_Alta_Redshift_MXR`, `SMEOEM_2023_Stark_VARG`

### Enduro OEM — 25 bikes, 1.76G

Installed as one avatar per bike: `bikes/<bike>.pkz` (locked archive) plus a
`bikes/<bike>/` paints folder. If the pack ships as one archive, that single
download is what to grab.

`EN1OEM_2014_Husaberg_FE250`, `EN1OEM_2014_Husaberg_TE125`, `EN1OEM_2014_Husaberg_TE250`, `EN1OEM_2014_Husqvarna_FE250`, `EN1OEM_2014_Husqvarna_TE125`, `EN1OEM_2014_Husqvarna_TE250`, `EN1OEM_2015_GasGas_EC125`, `EN1OEM_2015_GasGas_EC250`, `EN1OEM_2015_GasGas_EC250F`, `EN1OEM_2021_KTM_150EXC`, `EN1OEM_2021_KTM_250EXC`, `EN1OEM_2021_KTM_250EXCF`, `EN2OEM_2014_Husaberg_FE350`, `EN2OEM_2014_Husaberg_FE450`, `EN2OEM_2014_Husqvarna_FE350`, `EN2OEM_2014_Husqvarna_FE450`, `EN2OEM_2015_GasGas_EC300F`, `EN2OEM_2015_GasGas_EC450F`, `EN2OEM_2021_KTM_350EXCF`, `EN2OEM_2021_KTM_450EXCF`, `EN3OEM_2014_Husaberg_TE300`, `EN3OEM_2014_Husqvarna_TE300`, `EN3OEM_2015_GasGas_EC300`, `EN3OEM_2021_KTM_300EXC`, `EN3OEM_2021_KTM_500EXCF`

### Freeride OEM — 19 bikes, 1.27G

Installed as one avatar per bike: `bikes/<bike>.pkz` (locked archive) plus a
`bikes/<bike>/` paints folder. If the pack ships as one archive, that single
download is what to grab.

`FREERIDE_1996_Honda_CR250`, `FREERIDE_1997_Honda_CR250`, `FREERIDE_2002_Kawasaki_KX250`, `FREERIDE_2003_Suzuki_RM250`, `FREERIDE_2023_Fantic_XX250`, `FREERIDE_2023_Fantic_XXF_450`, `FREERIDE_2023_Honda_CRF450R`, `FREERIDE_2023_Husqvarna_FC_450`, `FREERIDE_2023_Husqvarna_TC_250`, `FREERIDE_2023_KTM_250_SX`, `FREERIDE_2023_KTM_450_SX-F`, `FREERIDE_2023_Kawasaki_KX450`, `FREERIDE_2023_Suzuki_RM-Z450`, `FREERIDE_2023_TM_MX_250`, `FREERIDE_2023_TM_MX_450_Fi`, `FREERIDE_2023_Yamaha_YZ250`, `FREERIDE_2023_Yamaha_YZ450F`, `FREERIDE_2024_GasGas_MC_250`, `FREERIDE_2024_GasGas_MC_450F`

### A-Kit pack — 25 bikes, 1.38G

Installed as one avatar per bike: `bikes/<bike>.pkz` (locked archive) plus a
`bikes/<bike>/` paints folder. If the pack ships as one archive, that single
download is what to grab.

`AK Beta RX 250F`, `AK Beta RX 450F`, `AK Ducati Desmo250`, `AK Ducati Desmo450`, `AK Fantic XXF 250F`, `AK Fantic XXF 450F`, `AK GasGas MC 250F`, `AK GasGas MC 450F`, `AK Honda CRF 250F`, `AK Honda CRF 450F`, `AK Husky FC 250F`, `AK Husky FC 450F`, `AK KTM SXF 250F`, `AK KTM SXF 450F`, `AK Kawasaki KX 250F`, `AK Kawasaki KX 450F`, `AK Stark Varg`, `AK Suzuki RMZ 250F`, `AK Suzuki RMZ 450F`, `AK TM Racing 250F`, `AK TM Racing 450F`, `AK Triumph TF 250F`, `AK Triumph TF 450F`, `AK Yamaha YZF 250F`, `AK Yamaha YZF 450F`

## Tyres — 6 packs

| Pack | Form | Size |
|---|---|---|
| AK_mx | locked pkz | 6 KB |
| oem_en | locked pkz | 24M |
| oem_freeride | locked pkz | 24M |
| oem_mx | locked pkz | 24M |
| oem_sm | locked pkz | 60M |
| p_mx | locked pkz | 46M |

`tyres/oem_freeride/` also exists but holds only an empty `paints/` folder — nothing
to restore beyond the pkz. `AK_mx.pkz` is tiny (6 KB) because it is tyre
*definitions* (soft/medium/hard compounds) for the A-Kit bikes, not textures.

`p_mx` / `m_sm`-style entries are **overrides of the game's own packs** (stock bikes
select them by `tyres_type`) — do not put loose `.tyre`/`.cfg` files beside them or
stock bikes stop spawning.

## Rider / misc

`mods/rider/` and `mods/misc/` hold only the game's own subfolders
(`animations`, `boots`, `fonts`, `helmetcams`, `helmets`, `protections`, `riders` / `fonts`, `pitboard`) —
no extra mod content was installed there.

## Wanted but NOT installed at capture

- E10 factory bikes (bike pack)
- MOUSE Motopark (track)
- 4 MEGA-only tracks: bigsendmx, poor-boyz-mx, 2023-dreamland-mx, mnsr-raceway

Grab these too after restore — `tools/fetch_missing.py` retries them across all
three mirrors.

## How to reinstall this list on NixOS

No download URLs were recorded during the original session, only the installed
names — so each item is re-found on **mxb-mods.com** by name (for locked tracks
the pkz filename *is* the site's `Track ID`, which makes the lookup exact).

1. Steam + Proton working first: `steam -applaunch 655500` must reach the menu.
2. `pip install pycryptodome requests` in a venv at `~/.local/share/mxb-tools/`;
   copy the scripts there from `tools/`.
3. For each item, get the post URL from mxb-mods.com, then:
   `mxb_parse.py slugs.txt plan.json` (slug per line) →
   `mxb_install2.py plan.json track|bike` (`mxb_cats.py` decides the category,
   `mxb_dl.py URL OUT` is the raw single-file downloader).
4. Rules that break a reinstall if ignored:
   - locked `.pkz`: place **as-is**, never extract (they are not zipfiles);
   - take the **player/default** file, never the "server version";
   - extract zip packs **straight into the mods path** — `/tmp` is a 16G tmpfs and
     the big packs are 2-4G;
   - mirror blocks (MediaFire 403, Drive quota, MEGA 509) clear in 20-40 min;
     `fetch_missing.py` rotates mirrors and gets small/optional files fastest.
5. Mods root on the new box:
   `~/.local/share/Steam/steamapps/compatdata/655500/pfx/drive_c/users/<user>/Documents/PiBoSo/MX Bikes/mods/`
   → `tracks/<motocross|supercross|supermoto|enduro|straight rhythm>/`, `bikes/`, `tyres/`.
6. Verify: `python3 tools/mxb_verify.py` — expect the counts above (42 tracks
   loadable, 148 bike pkz, 6 tyre packs), then diff `mods-manifest.txt`
   (path + byte size) against the restored tree.
