#!/usr/bin/env python3
"""Patient retry pass for the MX Bikes content that is still missing.

The mirrors block per-IP for minutes, so the loop waits between rounds
instead of hammering them with long in-request backoffs.
"""
import os
import re
import sys
import time
import subprocess

sys.path.insert(0, os.path.expanduser("~/.local/share/mxb-tools"))
from mxb_dl import download, mediafire_direct, UA  # noqa

DBG = "/tmp/dbg"
os.makedirs(DBG, exist_ok=True)

TARGETS = [
    # (label, [urls in preference order], output name)
    ("MX OEM v0.19.1 (53 bikes)", [
        "https://www.mediafire.com/file/lywg8di4sudik75/MX_OEM_v0.19.1.zip/file",
        "https://mega.nz/file/TVw12Rra#Y2PjDXwFYUgo6CMGNJ3uZUqgHyVD8uyh2TbRsJpwtbI",
        "https://drive.google.com/file/d/1F0fNGPy5Jh5LB6BqkqIlQ7L-Ra-uCc6j/view?usp=sharing",
    ], "oem_mx.zip"),
    ("A-Kit bike pack", [
        "https://www.mediafire.com/file/pb6bd6tonr1v4ho/bikes.zip/file",
    ], "akit.zip"),
    ("E10 factory bikes", [
        "https://www.mediafire.com/file/8jdwxy5mva3n7n7/E10_Update_Dec-13-23_Release.zip/file",
        "https://mega.nz/file/FHpSSIRR#TT8DnBP_aWx7Dwl0KqEYbsokISqpF6DlAWGyZDGsRSc",
    ], "e10.zip"),
    ("Compound 637 (track)", [
        "https://www.mediafire.com/file/ur1oqtt4ocj7qvv/Compound_637.rar/file",
        "https://drive.google.com/file/d/1xTtkD33zVnJygBHnmkfKKYtlLkmajPpd/view?usp=share_link",
        "https://mega.nz/file/takEwAAR#iNXkmJ9iz0NM-lXFTFLmbSCnqFvEZpowXry-6Y6OfD0",
    ], "compound637.zip"),
    ("MOUSE Motopark (track)", [
        "https://drive.google.com/drive/folders/12KAGl7h7Yf0gIHe58Z6lkFxtwFTRHvAF?usp=sharing",
        "https://mega.nz/file/Zv8SgQ7a#enJGW0onW4ru9jBjVXzULkmXmjDJhcNkFjAVCUy7e9k",
    ], "mousemotopark"),
    ("BigSendMX (track)", [
        "https://mega.nz/file/wyFzgagK#vsW-DbxwmZJVkxpfBzvDJYtfWxnRjimpPAFThSw1sw0",
    ], "bigsendmx"),
    ("Poor Boyz MX (track)", [
        "https://mega.nz/file/lm8j3YwZ#tsIG03XL6hpSsaUSh6vAiQ7aKOe-IbdhCMbM7Lo9Vw0",
        "https://mega.nz/file/l6lGFahZ#EXvSsor9Znqx6HGvoE1QfUR6hQx6WxLjJN7IF4_i2QM",
    ], "poorboyzmx"),
    ("Dreamland MX (track)", [
        "https://mega.nz/file/VUJ1QahJ#KIG4OcBlZ9j6JFfYUymgHnc0j-zYrKMq5bt-67lW7ww",
    ], "dreamlandmx"),
    ("MNSR Raceway (track)", [
        "https://mega.nz/file/JhVwADAI#5DXrd2E4BjdO1yiFtJ70RPVMDlW7vtadk97Y2XMfjgo",
    ], "mnsrraceway"),
]

ROUNDS = int(os.environ.get("ROUNDS", "12"))
SLEEP = int(os.environ.get("SLEEP", "180"))


def blocked(url):
    """Cheap probe: is this mirror currently serving us?"""
    if "mediafire.com" in url.lower():
        p = subprocess.run(["curl", "-sL", "--max-time", "40", "-A", UA, url],
                           capture_output=True, text=True)
        h = p.stdout
        if "Just a moment" in h or "Enable JavaScript and cookies" in h:
            # blocked directly; the proxy route may still work
            from mxb_dl import mediafire_direct_via_proxy
            return mediafire_direct_via_proxy(url) is None
        return mediafire_direct(url) is None
    if "mega.nz" in url.lower():
        import requests
        fid = url.split('/file/')[1].split('#')[0]
        body = '[{"a":"g","g":1,"p":"%s"}]' % fid
        try:
            r = requests.post("https://g.api.mega.co.nz/cs", data=body, timeout=60)
            fd = r.json()[0]
            if not isinstance(fd, dict) or "g" not in fd:
                return True
            u = fd["g"]
            rr = requests.get(u, headers={"Range": "bytes=0-4095"}, timeout=90)
            return rr.status_code not in (200, 206)
        except Exception:
            return True
    if "drive.google.com" in url.lower():
        import requests
        fid = re.search(r"/file/d/([A-Za-z0-9_-]+)", url)
        if not fid:
            return True
        try:
            r = requests.get(
                f"https://drive.usercontent.google.com/download?id={fid.group(1)}"
                "&export=download", timeout=90, headers={"User-Agent": UA})
            head = r.content[:4000]
            if b"Error 404" in head:
                return True   # dead mirror, never coming back
            if b"Quota exceeded" in head or b"Too many users" in head:
                return True
            if head[:1] == b"<":
                return True   # still an interstitial we would have to follow
            return False
        except Exception:
            return True
    return False


done = set()
for rnd in range(ROUNDS):
    for label, urls, name in TARGETS:
        if name in done:
            continue
        out = os.path.join(DBG, name)
        if os.path.exists(out) and os.path.getsize(out) > 0:
            done.add(name)
            continue
        for u in urls:
            if blocked(u):
                print(f"[round {rnd}] {label}: {u.split('/')[2]} blocked, skip",
                      flush=True)
                continue
            print(f"[round {rnd}] {label}: downloading from {u.split('/')[2]} ...",
                  flush=True)
            ok, info = download(u, out)
            sz = os.path.getsize(out) if os.path.exists(out) else 0
            # a throttled/CAPTCHA-gated host can return an HTML page with a
            # 200 status -- only accept a real archive
            real = False
            if sz > 100000:
                with open(out, "rb") as f:
                    magic = f.read(8)
                real = (magic[:4] == b"PK\x03\x04" or magic[:4] == b"Rar!"
                        or magic[:6] == b"7z\xbc\xaf\x27\x1c")
            if ok and sz > 100000 and real:
                done.add(name)
                break
            if ok and not real:
                print(f"    -> rejected {sz} bytes (not an archive)", flush=True)
                try:
                    os.remove(out)
                except OSError:
                    pass
    if len(done) == len(TARGETS):
        break
    print(f"[round {rnd}] got {len(done)}/{len(TARGETS)}, sleeping {SLEEP}s",
          flush=True)
    time.sleep(SLEEP)

print("DONE:", sorted(done), flush=True)
