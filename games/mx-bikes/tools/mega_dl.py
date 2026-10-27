"""Direct MEGA public-file downloader (no mega.py).

MEGA throttles per *request count*, not per byte: one big streaming GET is
fine, but hundreds of small Range requests exhaust the quota (HTTP 509).
So we issue a single GET and decrypt the response stream on the fly.

MEGA stores a file as AES-CTR encrypted chunks (128KiB, 256KiB, 1MiB, 4MiB...),
but CTR mode is a continuous keystream, so decrypting the whole stream in
order works regardless of the chunk boundaries.
"""
import base64
import json
import os
import struct
import sys
import time

import requests
from Crypto.Cipher import AES
from Crypto.Util import Counter

API = "https://g.api.mega.co.nz/cs"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def b64_to_a32(b):
    if isinstance(b, str):
        b = b.encode()
    # MEGA links use URL-safe base64 without padding
    b = b.replace(b'-', b'+').replace(b'_', b'/')
    b += b'=' * (-len(b) % 4)
    raw = base64.b64decode(b)
    return list(struct.unpack('>%dI' % (len(raw) // 4), raw))


def api_get(url, tries=8):
    """Ask the API for a download URL, retrying through throttle windows."""
    file_id = url.split('/file/')[1].split('#')[0]
    body = '[{"a":"g","g":1,"p":"%s"}]' % file_id
    last = None
    for attempt in range(tries):
        try:
            r = requests.post(API, data=body, timeout=60)
            fd = r.json()[0]
            if isinstance(fd, dict) and "g" in fd:
                return fd["g"], fd["s"]
            last = str(fd)[:120]
        except Exception as e:
            last = str(e)[:120]
        time.sleep(10 * (attempt + 1))
    return None, last


def download(url, out):
    file_id = url.split('/file/')[1].split('#')[0]
    url_g, size = api_get(url)
    if not url_g:
        return False, "api: %s" % size

    key = b64_to_a32(url.split('#')[1])
    k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])
    iv = list(key[4:6]) + [0, 0]
    ctr = Counter.new(128, initial_value=((iv[0] << 32) + iv[1]) << 64)
    aes = AES.new(struct.pack('>4I', *k), AES.MODE_CTR, counter=ctr)

    tmp = out + ".part"
    written = 0
    session = requests.Session()

    def fresh_url():
        """MEGA throttles a download URL after a short read (HTTP 509).
        Requesting a fresh URL from the API resets the quota."""
        body = '[{"a":"g","g":1,"p":"%s"}]' % file_id
        r = session.post(API, data=body, timeout=60)
        fd = r.json()[0]
        return fd["g"]

    # MEGA rejects a plain GET on large files with 509 but serves Range
    # requests fine, so always ask for a window.
    #
    # The quota attached to a freshly issued URL varies a lot: sometimes a
    # 32 MiB window is fine, sometimes only 4 KiB. So start big, shrink the
    # window on 509, and grow it back after a success.
    MAX_STEP = 32 * 1024 * 1024
    MIN_STEP = 4 * 1024
    step = MAX_STEP
    # resume a partial download: the AES-CTR keystream is positional, so
    # re-derive the cipher starting at the resume offset.
    base_counter = ((iv[0] << 32) + iv[1]) << 64
    if os.path.exists(tmp):
        written = os.path.getsize(tmp)
        if written % 16 == 0:
            ctr = Counter.new(128, initial_value=base_counter + (written // 16))
            aes = AES.new(struct.pack('>4I', *k), AES.MODE_CTR, counter=ctr)
        else:
            written = 0
    with open(tmp, "ab" if written else "wb") as f:
        pos = written
        while pos < size:
            want = min(step, size - pos)
            data = None
            last_err = None
            for attempt in range(10):
                try:
                    u = fresh_url()
                    resp = session.get(u, headers={"Range":
                                 f"bytes={pos}-{pos + want - 1}"}, timeout=300)
                    if resp.status_code in (200, 206):
                        data = resp.content
                        # MEGA may serve less than we asked for; that's fine,
                        # we just continue from where it stopped.
                        if len(data) < want:
                            want = len(data)
                        break
                    last_err = f"HTTP {resp.status_code}"
                    step = max(MIN_STEP, step // 4)   # URL quota was smaller
                    time.sleep(2 * (attempt + 1))
                except Exception as e:
                    last_err = f"{type(e).__name__}: {str(e)[:80]}"
                    time.sleep(10 * (attempt + 1))
            if not data:
                try:
                    os.remove(tmp)
                except OSError:
                    pass
                return False, f"chunk at {pos} failed ({last_err})"
            f.write(aes.decrypt(data))
            written += len(data)
            pos += len(data)
            if step < MAX_STEP:
                step = min(MAX_STEP, step * 4)

    if written != size:
        os.remove(tmp)
        return False, f"short read {written}/{size}"
    os.replace(tmp, out)
    return True, f"{size} bytes"


if __name__ == "__main__":
    ok, info = download(sys.argv[1], sys.argv[2])
    print(json.dumps({"ok": ok, "info": info}))
    sys.exit(0 if ok else 1)
