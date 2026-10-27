"""Download MX Bikes mod files from MediaFire / Google Drive / MEGA / Dropbox / 1drv."""
import os
import re
import glob
import shutil
import subprocess
import sys
import json
import time
import html as html_mod
import urllib.parse

import requests

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
MEGA_PY = os.path.expanduser("~/.local/share/mxb-tools/venv/bin/python")


def _curl(url, out, extra=None, timeout=1800):
    cmd = ["curl", "-sL", "--max-time", str(timeout), "-A", UA,
           "--retry", "3", "--retry-delay", "3", "-C", "-", url, "-o", out]
    if extra:
        cmd[1:1] = extra
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 0


def mediafire_direct(page_url):
    """Return the real download URL behind a MediaFire file page, or None."""
    p = subprocess.run(["curl", "-sL", "--max-time", "90", "-A", UA, page_url],
                       capture_output=True, text=True)
    html = p.stdout
    if "Just a moment" in html or "Enable JavaScript and cookies" in html:
        return None
    m = re.search(r'href="(https://download\d+\.mediafire\.com/[^"]+)"', html)
    if not m:
        m = re.search(r'"(https://download\d+\.mediafire\.com/[^"]+)"', html)
    return m.group(1) if m else None


def mediafire_direct_via_proxy(page_url):
    """MediaFire's own page is Cloudflare-blocked per-IP; a text-extraction
    proxy fetches the page for us and exposes the same download link.

    Ask for the raw HTML: the default markdown rendering truncates the page
    before the download button for large files.
    """
    p = subprocess.run(
        ["curl", "-sL", "--max-time", "120",
         "-H", "X-Return-Format: html",
         "https://r.jina.ai/" + page_url],
        capture_output=True, text=True)
    m = re.search(r'(https://download\d+\.mediafire\.com/[^\s"\'<>)]+)', p.stdout)
    if not m:
        return None
    return m.group(1)


def mediafire(url, out):
    """Scrape the MediaFire page for the real download host.

    MediaFire's page is Cloudflare-blocked per-IP. When that happens, a
    text-extraction proxy fetches the page for us and exposes the same
    download link -- try that before the long in-request backoff.
    """
    p = subprocess.run(["curl", "-sL", "--max-time", "90", "-A", UA, url],
                       capture_output=True, text=True)
    html = p.stdout
    blocked = ("Just a moment" in html
               or "Enable JavaScript and cookies" in html)
    if not blocked:
        m = re.search(r'href="(https://download\d+\.mediafire\.com/[^"]+)"', html)
        if not m:
            m = re.search(r'"(https://download\d+\.mediafire\.com/[^"]+)"', html)
        if m:
            return _curl(m.group(1), out), m.group(1)
        return False, "no direct link found (password protected or removed)"

    direct = mediafire_direct_via_proxy(url)
    if direct:
        if _curl(direct, out):
            return True, f"mediafire via proxy {os.path.getsize(out)}"
        return False, "mediafire proxy link failed"
    return False, "rate limited (cloudflare) and proxy route failed"


def gdrive(url, out):
    """Google Drive file -> direct download.

    Large files (>100MB) get an HTML interstitial with a confirm token; we
    scrape that form and repost it, keeping the same cookie jar so the
    uuid stays valid.
    """
    fid = re.search(r'/file/d/([A-Za-z0-9_-]+)', url)
    if not fid:
        fid = re.search(r'[?&]id=([A-Za-z0-9_-]+)', url)
    if not fid:
        return False, "no google file id"
    fid = fid.group(1)

    cookie = "/tmp/gdcook_" + fid[-8:]
    def _get(u):
        cmd = ["curl", "-sL", "--max-time", "900", "-A", UA,
               "-c", cookie, "-b", cookie, u]
        return subprocess.run(cmd, capture_output=True).stdout

    dl = f"https://drive.usercontent.google.com/download?id={fid}&export=download"
    data = _get(dl)
    if data[:200].lstrip()[:1] == b"<":
        h = data.decode('utf-8', 'ignore')
        if "Error 404" in h or "not found" in h.lower()[:400]:
            return False, "gdrive mirror is dead (404)"
        m = re.search(r'<form id="download-form" action="([^"]+)"(.*?)</form>',
                      h, re.S)
        if m:
            action = html_mod.unescape(m.group(1))
            fields = dict(re.findall(
                r'<input type="hidden" name="([^"]+)" value="([^"]*)"', m.group(2)))
            q = "&".join(f"{k}={v}" for k, v in fields.items())
            data = _get(f"{action}?{q}")
    with open(out, "wb") as f:
        f.write(data)
    if data[:4] == b"PK\x03\x04" or data[:4] == b"Rar!":
        return True, "gdrive"
    if data[:200].lstrip()[:1] == b"<":
        if b"Quota exceeded" in data or b"Too many users" in data:
            return False, "gdrive quota exceeded"
        return False, "gdrive returned HTML"
    if len(data) > 0:
        return True, "gdrive"
    return False, "gdrive empty"


def gdrive_folder(url, out):
    """Google Drive folder -> download every file in it into `out`."""
    fid = re.search(r'/folders/([A-Za-z0-9_-]+)', url)
    if not fid:
        return False, "no folder id"
    fid = fid.group(1)
    os.makedirs(out, exist_ok=True)
    # public folder listing via the public web endpoint
    api = (f"https://drive.google.com/embeddedfolderview?id={fid}#list")
    p = subprocess.run(["curl", "-sL", "--max-time", "90", "-A", UA, api],
                       capture_output=True, text=True)
    ids = []
    for m in re.finditer(r'id="entry-([A-Za-z0-9_-]+)"', p.stdout):
        if m.group(1) not in ids:
            ids.append(m.group(1))
    if not ids:
        # fall back to gdown --folder
        cmd = ["/home/mamaroufaren/.local/bin/gdown", "--folder", "-O", out, url]
        q = subprocess.run(cmd, capture_output=True, text=True)
        ok = os.path.isdir(out) and any(os.scandir(out))
        return ok, (q.stdout + q.stderr)[-200:] if not ok else "gdrive-folder"
    got = 0
    for fid2 in ids:
        dst = os.path.join(out, f"gd_{fid2}.bin")
        ok, _ = gdrive(f"https://drive.google.com/file/d/{fid2}/view", dst)
        if ok:
            got += 1
    return got > 0, f"{got} files from folder"


def mega(url, out):
    """MEGA public file link -> download.

    Use the ranged downloader (mega_dl): MEGA rejects a plain GET on large
    files with HTTP 509 but serves Range requests, and it resumes a partial
    file so a throttle window doesn't lose progress. mega.py is kept as a
    fallback because it can succeed when ranged reads are throttled.
    """
    script2 = ("import sys; sys.path.insert(0, %r); import mega_dl; "
               "ok, info = mega_dl.download(%r, %r); print('OK' if ok else 'ERR', info)"
               % (os.path.dirname(os.path.abspath(__file__)), url, out))
    try:
        subprocess.run([MEGA_PY, "-c", script2], capture_output=True, text=True,
                       timeout=3600)
    except subprocess.TimeoutExpired:
        return False, "mega timeout (ranged)"
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return True, f"mega (ranged) {os.path.getsize(out)}"

    # fallback: mega.py single streaming GET
    file_id = url.split('/file/')[1].split('#')[0]
    body = '[{"a":"g","g":1,"p":"%s"}]' % file_id
    try:
        r = requests.post("https://g.api.mega.co.nz/cs", data=body, timeout=60)
        fd = r.json()[0]
        want = fd.get("s") if isinstance(fd, dict) else None
    except Exception:
        want = None

    dest = os.path.join("/tmp/mxb_mega_tmp",
                        os.path.basename(out) + "_" + str(abs(hash(url)) % 99999))
    shutil.rmtree(dest, ignore_errors=True)
    os.makedirs(dest, exist_ok=True)   # mega.py does not create the target dir
    script = f'''
import mega, os
os.makedirs("{dest}", exist_ok=True)
m = mega.Mega()
m.login()
m.download_url("{url}", "{dest}")
print("OK")
'''
    try:
        subprocess.run([MEGA_PY, "-c", script], capture_output=True, text=True,
                       timeout=3600)
    except subprocess.TimeoutExpired:
        return False, "mega timeout"
    got = None
    for f in sorted(glob.glob(os.path.join(dest, "*"))):
        if os.path.isfile(f) and os.path.getsize(f) > 0:
            got = f
            break
    if got:
        if os.path.exists(out):
            os.remove(out)
        os.replace(got, out)
    shutil.rmtree(dest, ignore_errors=True)
    if os.path.exists(out) and os.path.getsize(out) > 0:
        size = os.path.getsize(out)
        if want and size != want:
            os.remove(out)
            return False, f"mega truncated {size}/{want}"
        return True, f"mega {size}"
    return False, "mega failed"


def dropbox(url, out):
    dl = url.replace("?dl=0", "?dl=1")
    return _curl(dl, out), "dropbox"


def onedrive(url, out):
    # 1drv.ms -> resolve to direct download
    p = subprocess.run(["curl", "-sL", "--max-time", "90", "-A", UA, url],
                       capture_output=True, text=True)
    m = re.search(r'"(https://[^"]*\.download\.1drv\.com[^"]*)"', p.stdout)
    if not m:
        m = re.search(r'href="(https://[^"]*download\.1drv\.com[^"]*)"', p.stdout)
    if not m:
        return False, "1drv resolve failed"
    return _curl(m.group(1), out), m.group(1)[:100]


def download(url, out):
    u = url.lower()
    if "mediafire.com" in u:
        return mediafire(url, out)
    if "drive.google.com" in u:
        if "/file/d/" in u:
            return gdrive(url, out)
        if "/folders/" in u or "/drive/folders" in u:
            return gdrive_folder(url, out)
        return gdrive(url, out)
    if "mega.nz" in u:
        return mega(url, out)
    if "dropbox.com" in u:
        return dropbox(url, out)
    if "1drv.ms" in u:
        return onedrive(url, out)
    return _curl(url, out), "direct"


if __name__ == "__main__":
    url, out = sys.argv[1], sys.argv[2]
    ok, info = download(url, out)
    size = os.path.getsize(out) if os.path.exists(out) else 0
    print(json.dumps({"ok": ok, "url": url, "out": out, "size": size,
                      "info": str(info)[:200]}))
    sys.exit(0 if ok else 1)
