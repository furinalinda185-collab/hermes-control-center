#!/usr/bin/env python3
"""Pull the Redline Valley PLAYER build from MEGA (retry until IP quota lifts)
and install it as a locked .pkz. Quarantines on failure.

MEGA returns HTTP 509 while the per-IP quota is exhausted; the quota resets
on its own, so retry with waits instead of hammering.
"""
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.expanduser("~/.local/share/mxb-tools"))
from mega_dl import download  # noqa: E402

URL = "https://mega.nz/file/7IpikCQL#5lcpZfxHTPgW6setMtIwBH7RLCisvFTIVh2V4RoreDs"
OUT = os.path.expanduser("~/.hermes/cache/scratch/Redline_Valley_By_Ps.pkz")
MODS = os.path.expanduser(
    "~/.local/share/Steam/steamapps/compatdata/655500/pfx/drive_c/users/"
    "steamuser/Documents/PiBoSo/MX Bikes/mods/tracks/motocross")
EXPECT = 540829613
TRIES = int(os.environ.get("TRIES", "10"))
WAIT = int(os.environ.get("WAIT", "240"))

for i in range(TRIES):
    print(f"[try {i+1}/{TRIES}] {time.strftime('%H:%M:%S')}", flush=True)
    try:
        ok, info = download(URL, OUT)
    except Exception as e:                                  # noqa: BLE001
        ok, info = False, f"{type(e).__name__}: {e}"
    print("   ->", ok, info, flush=True)
    if ok and os.path.exists(OUT):
        size = os.path.getsize(OUT)
        head = open(OUT, "rb").read(512).lstrip()[:200]
        if size != EXPECT:
            print(f"   !! size {size} != expected {EXPECT}", flush=True)
        elif head[:9].lower().startswith((b"<!doctype", b"<html")):
            print("   !! payload is an HTML page, not a pkz", flush=True)
        else:
            dest = os.path.join(MODS, "Redline Valley By Ps.pkz")
            shutil.move(OUT, dest)
            print("INSTALLED:", dest, size, "bytes", flush=True)
            sys.exit(0)
        os.remove(OUT)
    time.sleep(WAIT)

print("GAVE UP after", TRIES, "tries", flush=True)
sys.exit(1)
