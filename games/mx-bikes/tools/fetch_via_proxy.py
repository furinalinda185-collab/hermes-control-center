#!/usr/bin/env python3
"""Fetch MediaFire files through the r.jina.ai proxy.

MediaFire's download links are IP-bound and short-lived, so we must
resolve a link and start the download immediately, then verify the
payload is really the file (not the HTML "download_repair" page).
"""
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.expanduser("~/.local/share/mxb-tools"))
from mxb_dl import mediafire_direct_via_proxy  # noqa

DBG = "/tmp/dbg"
os.makedirs(DBG, exist_ok=True)


def fetch(name, page_url, tries=4):
    out = os.path.join(DBG, name)
    if os.path.exists(out) and os.path.getsize(out) > 100000:
        print(f"{name}: already {os.path.getsize(out)}", flush=True)
        return True
    for attempt in range(tries):
        link = mediafire_direct_via_proxy(page_url)
        if not link:
            print(f"{name}: attempt {attempt}: no link", flush=True)
            time.sleep(10)
            continue
        p = subprocess.run(
            ["curl", "-sL", "--max-time", "2400", "-A",
             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121.0",
             link, "-o", out],
            capture_output=True)
        sz = os.path.getsize(out) if os.path.exists(out) else 0
        with open(out, "rb") as f:
            magic = f.read(8)
        good = (magic[:4] == b'PK\x03\x04' or magic[:4] == b'Rar!'
                or magic[:6] == b'7z\xbc\xaf\x27\x1c')
        if good and sz > 100000:
            print(f"{name}: OK {sz} bytes", flush=True)
            return True
        print(f"{name}: attempt {attempt}: bad payload ({sz} bytes, "
              f"{magic[:8].hex()})", flush=True)
        try:
            os.remove(out)
        except OSError:
            pass
        time.sleep(15)
    return False


TARGETS = [
    ("akit.zip",
     "https://www.mediafire.com/file/pb6bd6tonr1v4ho/bikes.zip/file"),
    ("e10.zip",
     "https://www.mediafire.com/file/8jdwxy5mva3n7n7/E10_Update_Dec-13-23_Release.zip/file"),
    ("oem_mx.zip",
     "https://www.mediafire.com/file/lywg8di4sudik75/MX_OEM_v0.19.1.zip/file"),
    ("compound637.zip",
     "https://www.mediafire.com/file/ur1oqtt4ocj7qvv/Compound_637.rar/file"),
]

if __name__ == '__main__':
    names = sys.argv[1:] or None
    for name, url in TARGETS:
        if names and name not in names:
            continue
        fetch(name, url)
