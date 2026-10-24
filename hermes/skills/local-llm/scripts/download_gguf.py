#!/usr/bin/env python3
"""Parallel resume-aware chunked downloader for a single large file (stdlib only).

Usage: download_gguf.py URL DEST [N_WORKERS]

Splits the file into N equal ranges fetched concurrently with HTTP Range
requests. Partial part files are resumed (not restarted) via
`Range: bytes=<start+have>-<end>` in append mode. Parts assemble into DEST
only when every chunk's byte count matches; the final size is asserted
against the HEAD Content-Length.
"""
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


def head_length(url):
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as r:
        return int(r.headers["Content-Length"])


def fetch(url, parts_dir, i, a, b):
    p = os.path.join(parts_dir, f"part{i:02d}")
    want = b - a + 1
    if os.path.exists(p) and os.path.getsize(p) == want:
        return i, True, "cached"
    for attempt in range(10):
        try:
            have = os.path.getsize(p) if os.path.exists(p) else 0
            if have > want:
                os.remove(p)
                have = 0
            mode = "ab" if have else "wb"
            req = urllib.request.Request(
                url, headers={"Range": f"bytes={a + have}-{b}"}
            )
            with urllib.request.urlopen(req, timeout=120) as r, open(p, mode) as f:
                while True:
                    buf = r.read(1 << 20)
                    if not buf:
                        break
                    f.write(buf)
            if os.path.getsize(p) == want:
                return i, True, "ok"
        except Exception:
            time.sleep(2 * (attempt + 1))
    return i, False, "failed"


def main():
    url, dest = sys.argv[1], os.path.expanduser(sys.argv[2])
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    parts = dest + ".parts"
    os.makedirs(parts, exist_ok=True)

    total = head_length(url)
    if os.path.exists(dest) and os.path.getsize(dest) == total:
        print(f"already complete: {dest} ({total} bytes)")
        return

    chunk = (total + n - 1) // n
    ranges = [(i * chunk, min((i + 1) * chunk - 1, total - 1)) for i in range(n)]

    done = 0
    with ThreadPoolExecutor(max_workers=n) as ex:
        futs = [ex.submit(fetch, url, parts, i, a, b) for i, (a, b) in enumerate(ranges)]
        for fut in as_completed(futs):
            i, ok, msg = fut.result()
            done += 1
            print(f"chunk {i}: {msg}  [{done}/{n}]", flush=True)
            if not ok:
                sys.exit(f"chunk {i} failed")

    with open(dest, "wb") as out:
        for i in range(n):
            with open(os.path.join(parts, f"part{i:02d}"), "rb") as pf:
                while True:
                    buf = pf.read(1 << 22)
                    if not buf:
                        break
                    out.write(buf)

    got = os.path.getsize(dest)
    assert got == total, f"size mismatch: {got} != {total}"
    import shutil

    shutil.rmtree(parts, ignore_errors=True)
    print(f"COMPLETE {dest} {got} bytes ({got / 2**30:.2f} GiB)")


if __name__ == "__main__":
    main()
