"""Install MX Bikes community mods into the Proton prefix.

MX Bikes mod distribution has two shapes:
  * a plain ZIP (extension renamed .pkz) -> unpack it
  * a PiBoSo-LOCKED .pkz -> the game decrypts it itself; it MUST be placed
    in the mods folder as an opaque file and never extracted.

Locked files are high-entropy and look like noise, which is exactly what we see
for most community tracks. So: try to unpack; if the payload is not a readable
archive, keep the file and drop it in place.
"""
import os
import re
import glob
import shutil
import json
import zipfile
import subprocess
import sys
import urllib.parse

sys.path.insert(0, os.path.expanduser("~/.local/share/mxb-tools"))
from mxb_dl import download  # noqa

USER_MX = ("/home/mamaroufaren/.local/share/Steam/steamapps/compatdata/655500/pfx/"
           "drive_c/users/steamuser/Documents/PiBoSo/MX Bikes")
MODS = os.path.join(USER_MX, "mods")
STAGE = "/tmp/mxb_stage"

TRACK_EXTS = ('.amb', '.trh', '.tsc', '.rdf')
DEFAULT_CAT = "motocross"


def log(*a):
    print(*a, flush=True)


def safe(name):
    name = re.sub(r'[<>:"/\\|?*]', '_', str(name)).strip()
    return name[:80] or "unnamed"


def kind_of(path):
    """'zip' | 'locked' | 'other' for a downloaded payload."""
    if zipfile.is_zipfile(path):
        return 'zip'
    try:
        with open(path, 'rb') as f:
            magic = f.read(8)
    except OSError:
        return 'other'
    if magic[:4] == b'Rar!' or magic[:6] == b'7z\xbc\xaf\x27\x1c':
        return 'other'
    return 'locked'


def grab_mirrors(urls, stem, ext):
    """Download every mirror in parallel; return (path, kind, size) for each
    that produced a file. Mirrors are independent copies, so any that succeeds
    is usable -- locked ones are fine too (the game decrypts them)."""
    import concurrent.futures
    os.makedirs(STAGE, exist_ok=True)
    outs = []
    for i, u in enumerate(urls):
        if "/folders/" in u or "/drive/folders" in u:
            # folder links: download into a directory instead
            outs.append((os.path.join(STAGE, f"{stem}_m{i}_dir"), u, True))
        else:
            outs.append((os.path.join(STAGE, f"{stem}_m{i}{ext}"), u, False))

    def one(job):
        o, u, is_dir = job
        try:
            ok, info = download(u, o)
        except Exception as e:
            return dict(path=o, ok=False, size=0, kind='-', info=str(e)[:120],
                        dir=is_dir)
        if is_dir:
            files = []
            if os.path.isdir(o):
                for root, _d, fs in os.walk(o):
                    for x in fs:
                        p = os.path.join(root, x)
                        files.append((p, os.path.getsize(p)))
            if not files:
                return dict(path=o, ok=False, size=0, kind='-', info=str(info)[:120],
                            dir=True)
            files.sort(key=lambda t: -t[1])
            best, bsize = files[0]
            kind = kind_of(best)
            return dict(path=best, ok=True, size=bsize, kind=kind,
                        info=str(info)[:120], dir=True, extra=[f[0] for f in files[1:]])
        size = os.path.getsize(o) if ok and os.path.exists(o) else 0
        return dict(path=o, ok=ok, size=size, kind=kind_of(o) if ok else '-',
                    info=str(info)[:160], dir=False)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(outs))) as ex:
        for r in ex.map(one, outs):
            results.append(r)
    return results


def find_track_dirs(root):
    """Locate directories that hold MX Bikes track files."""
    out = []
    for dirpath, _dirs, files in os.walk(root):
        low = [f.lower() for f in files]
        if any(any(f.endswith(ext) for f in low) for ext in TRACK_EXTS):
            out.append(dirpath)
    return out


def fetch(url, dest):
    """Download with mirror fallback handled by caller."""
    ok, info = download(url, dest)
    return ok, str(info)[:200]


def place_locked(src, dest_dir, name):
    os.makedirs(dest_dir, exist_ok=True)
    target = os.path.join(dest_dir, name)
    if os.path.exists(target):
        os.remove(target)
    shutil.move(src, target)
    return target


def install_track(item):
    """Install one track. Returns (ok, message)."""
    cat = item.get('category') or DEFAULT_CAT
    dest_cat = os.path.join(MODS, "tracks", cat)
    os.makedirs(dest_cat, exist_ok=True)
    files = [f for f in item['files'] if f['kind'] == 'default'] or \
            [f for f in item['files'] if f['kind'] != 'server']
    if not files:
        return False, "no default file"

    # Collect every distinct mirror URL, ordered so that the most reliable
    # hosts come first (mediafire serves the raw file; google drive may hand
    # back an HTML interstitial).
    urls = []
    for f in files:
        u = f['url']
        if u not in urls:
            urls.append(u)
    if not urls:
        return False, "no urls"

    def host_rank(u):
        ul = u.lower()
        if 'mediafire.com/file/' in ul:
            return 0
        if 'drive.google.com' in ul:
            return 1
        if 'mega.nz' in ul:
            return 2
        return 3

    urls.sort(key=host_rank)
    log(f"    mirrors: {len(urls)}")
    stem = safe(item['slug'])
    ext = '.pkz'
    results = grab_mirrors(urls, stem, ext)
    for r in results:
        log(f"      {r['kind']:7s} {r['size']:>12,}  {os.path.basename(r['path'])}"
            + ("" if r['ok'] else f"  ERR {r['info'][:70]}"))

    good = [r for r in results if r['ok'] and r['size'] > 0]
    if not good:
        return False, "all mirrors failed"
    # prefer a readable archive; otherwise fall back to a locked pkz
    good.sort(key=lambda r: (r['kind'] != 'zip', -r['size']))

    for r in good:
        stage_path = r['path']
        size = r['size']
        k = r['kind']
        if k == 'locked':
            tid = item.get('track_id') or stem
            tid = safe(tid).strip()
            if tid.lower().endswith('.pkz'):
                tid = tid[:-4]
            name = tid + '.pkz'
            place_locked(stage_path, dest_cat, name)
            log(f"    LOCKED pkz -> mods/tracks/{cat}/{name} ({size:,})")
            cleanup(results, keep=stage_path)
            return True, f"locked:{name}"
        work = os.path.join(STAGE, "w_" + stem)
        shutil.rmtree(work, ignore_errors=True)
        os.makedirs(work, exist_ok=True)
        try:
            if k == 'zip':
                with zipfile.ZipFile(stage_path) as z:
                    z.extractall(work)
            else:
                subprocess.run(["bsdtar", "-xf", stage_path, "-C", work], check=True)
        except Exception as e:
            log(f"    FAILED extract: {str(e)[:120]}")
            shutil.rmtree(work, ignore_errors=True)
            continue
        tdirs = find_track_dirs(work)
        if tdirs:
            for td in tdirs:
                tgt = os.path.join(dest_cat, os.path.basename(td))
                if os.path.exists(tgt):
                    shutil.rmtree(tgt, ignore_errors=True)
                shutil.copytree(td, tgt)
                log(f"    extracted -> mods/tracks/{cat}/{os.path.basename(td)}")
            shutil.rmtree(work, ignore_errors=True)
            cleanup(results)
            return True, "extracted"
        inner = glob.glob(os.path.join(work, "**", "*.pkz"), recursive=True)
        if inner:
            name = os.path.basename(inner[0])
            shutil.move(inner[0], os.path.join(dest_cat, name))
            log(f"    inner pkz -> mods/tracks/{cat}/{name}")
            shutil.rmtree(work, ignore_errors=True)
            cleanup(results)
            return True, f"inner:{name}"
        log("    nothing installable inside")
        shutil.rmtree(work, ignore_errors=True)
    cleanup(results)
    return False, "no installable payload"


def cleanup(results, keep=None):
    for r in results:
        p = r['path']
        if p == keep:
            continue
        try:
            if os.path.exists(p):
                os.remove(p)
        except OSError:
            pass


def install_bike(item):
    """Bike packs: outer zip -> mods/{bikes,tyres,rider}. Locked pkz stay packed."""
    os.makedirs(STAGE, exist_ok=True)
    files = [f for f in item['files'] if f['kind'] == 'default'] or \
            [f for f in item['files'] if f['kind'] != 'server']
    urls = []
    for f in files:
        u = f['url']
        # skip informational links (project pages, not files)
        if 'oem.mxb-mods.com' in u or u.rstrip('/').endswith('mxb-mods.com'):
            continue
        if u not in urls:
            urls.append(u)
    if not urls:
        return False, "no file urls"

    def host_rank(u):
        ul = u.lower()
        if 'mediafire.com/file/' in ul:
            return 0
        if 'drive.google.com' in ul:
            return 1
        if 'mega.nz' in ul:
            return 2
        return 3

    urls.sort(key=host_rank)
    log(f"    mirrors: {len(urls)}")
    stem = "b_" + safe(item['slug'])
    results = grab_mirrors(urls, stem, '.zip')
    for r in results:
        log(f"      {r['kind']:7s} {r['size']:>12,}  {os.path.basename(r['path'])}"
            + ("" if r['ok'] else f"  ERR {r['info'][:70]}"))

    good = [r for r in results if r['ok'] and r['size'] > 0]
    if not good:
        return False, "all mirrors failed"
    good.sort(key=lambda r: (r['kind'] != 'zip', -r['size']))

    for r in good:
        stage_path = r['path']
        if r['kind'] == 'locked':
            name = safe(item['slug']).replace('b_', '') + '.pkz'
            place_locked(stage_path, os.path.join(MODS, 'bikes'), name)
            log(f"    LOCKED pack -> mods/bikes/{name} ({r['size']:,})")
            cleanup(results, keep=stage_path)
            return True, "locked"
        work = os.path.join(STAGE, "wb_" + safe(item['slug']))
        shutil.rmtree(work, ignore_errors=True)
        os.makedirs(work, exist_ok=True)
        try:
            if r['kind'] == 'zip':
                with zipfile.ZipFile(stage_path) as z:
                    z.extractall(work)
            else:
                subprocess.run(["bsdtar", "-xf", stage_path, "-C", work], check=True)
        except Exception as e:
            log(f"    FAILED extract: {str(e)[:120]}")
            shutil.rmtree(work, ignore_errors=True)
            continue
        # locate the mods tree inside the pack
        src_root = None
        cand = os.path.join(work, "mods")
        if os.path.isdir(cand):
            src_root = cand
        else:
            for d in sorted(os.listdir(work)):
                p = os.path.join(work, d)
                if os.path.isdir(p) and any(
                        os.path.isdir(os.path.join(p, s)) for s in ('bikes', 'tyres', 'rider')):
                    src_root = p
                    break
        if src_root is None:
            src_root = work
        copied = 0
        for sub in ('bikes', 'tyres', 'rider', 'misc'):
            s = os.path.join(src_root, sub)
            if not os.path.isdir(s):
                continue
            d = os.path.join(MODS, sub)
            os.makedirs(d, exist_ok=True)
            for entry in os.listdir(s):
                sp = os.path.join(s, entry)
                dp = os.path.join(d, entry)
                if os.path.isdir(sp):
                    if os.path.exists(dp):
                        shutil.rmtree(dp, ignore_errors=True)
                    shutil.copytree(sp, dp)
                else:
                    shutil.copy2(sp, dp)
                copied += 1
        log(f"    installed {copied} entries")
        shutil.rmtree(work, ignore_errors=True)
        cleanup(results)
        if copied:
            return True, f"{copied} entries"
    cleanup(results)
    return False, "no installable payload"


if __name__ == '__main__':
    plan = json.load(open(sys.argv[1]))
    kind = sys.argv[2]
    results = []
    for item in plan:
        log(f"[{kind}] {item['title']} ({item.get('downloads',0)} dl)")
        ok, msg = (install_track(item) if kind == 'track' else install_bike(item))
        results.append(dict(slug=item['slug'], title=item['title'], ok=ok, msg=msg))
        log(f"    => {'OK ' if ok else 'FAILED'} {msg}")
    json.dump(results, open(f"/tmp/mxb_result_{kind}.json", "w"), indent=1)
    n_ok = sum(1 for r in results if r['ok'])
    log(f"\nSUMMARY {kind}: {n_ok}/{len(results)} installed")
