"""Verify installed MX Bikes mods against the game's own loading rules.

The game reads:
  tracks/<cat>/<name>/   a folder holding <name>.trh + <name>.amb (+ .ini/.rdf)
  tracks/<cat>/<name>.pkz a PiBoSo-locked archive it decrypts itself
  bikes/<name>.pkz       a locked bike archive (model + physics)
  bikes/<name>/          a folder used for paints
  tyres/<name>.pkz

So a track is loadable if it is either a valid folder (the .trh/.amb pair) or
a non-empty .pkz file. We check the real on-disk layout.

`--run` additionally launches the game under Proton; note that a standalone
Proton run has no display and never reaches the UI, so it writes no logs.
Launch through Steam for a real in-game check.
"""
import os
import subprocess
import sys

GAME = os.path.expanduser("~/.local/share/Steam/steamapps/common/MX Bikes")
USER_MX = os.path.expanduser(
    "~/.local/share/Steam/steamapps/compatdata/655500/pfx/"
    "drive_c/users/steamuser/Documents/PiBoSo/MX Bikes")
MODS = os.path.join(USER_MX, "mods")
PROTON = os.path.expanduser(
    "~/.local/share/Steam/steamapps/common/Proton - Experimental/proton")
TRACK_EXTS = ('.trh', '.amb')
GAME_CATS = ('motocross', 'supercross', 'supermoto', 'enduro', 'straight rhythm')


def track_report():
    good_folders, bad_folders, locked = [], [], []
    tdir = os.path.join(MODS, "tracks")
    if not os.path.isdir(tdir):
        return good_folders, bad_folders, locked
    for cat in sorted(os.listdir(tdir)):
        p = os.path.join(tdir, cat)
        if not os.path.isdir(p):
            continue
        for name in sorted(os.listdir(p)):
            f = os.path.join(p, name)
            if os.path.isdir(f):
                names = {n.lower() for n in os.listdir(f)}
                if all(any(n.endswith(e) for n in names) for e in TRACK_EXTS):
                    good_folders.append((cat, name))
                else:
                    bad_folders.append((cat, name, sorted(os.listdir(f))[:5]))
            elif name.lower().endswith('.pkz'):
                locked.append((cat, name, os.path.getsize(f)))
    return good_folders, bad_folders, locked


def bike_report():
    bdir = os.path.join(MODS, "bikes")
    pkz, folders, odd = [], [], []
    if not os.path.isdir(bdir):
        return pkz, folders, odd
    for name in sorted(os.listdir(bdir)):
        f = os.path.join(bdir, name)
        if os.path.isdir(f):
            folders.append(name)
        elif name.lower().endswith('.pkz'):
            pkz.append((name, os.path.getsize(f)))
        else:
            odd.append(name)
    return pkz, folders, odd


def run_game(seconds=70):
    env = dict(os.environ)
    env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = os.path.expanduser(
        "~/.local/share/Steam")
    env["STEAM_COMPAT_DATA_PATH"] = os.path.expanduser(
        "~/.local/share/Steam/steamapps/compatdata/655500")
    try:
        subprocess.run([PROTON, "run", "mxbikes.exe"], cwd=GAME, env=env,
                       timeout=seconds, capture_output=True)
    except subprocess.TimeoutExpired:
        pass


def main():
    gf, bf, lk = track_report()
    print("TRACKS")
    print(f"  loadable folders (have .trh+.amb): {len(gf)}")
    for c, n in gf:
        print(f"      tracks/{c}/{n}")
    print(f"  locked .pkz (game decrypts)      : {len(lk)}")
    for c, n, s in lk:
        print(f"      tracks/{c}/{n}  ({s:,} bytes)")
    if bf:
        print(f"  INCOMPLETE folders               : {len(bf)}")
        for c, n, f in bf:
            print(f"      tracks/{c}/{n}  has={f}")

    pkz, folders, odd = bike_report()
    print("BIKES")
    print(f"  .pkz bike archives : {len(pkz)}")
    print(f"  paint/aux folders  : {len(folders)}")
    if odd:
        print(f"  other files        : {len(odd)} -> {odd[:8]}")
    print("TYRES")
    tdir = os.path.join(MODS, "tyres")
    for t in sorted(os.listdir(tdir) if os.path.isdir(tdir) else []):
        print(f"      tyres/{t}")

    if '--run' in sys.argv:
        secs = int(sys.argv[sys.argv.index('--run') + 1])
        print(f"\nlaunching game under Proton for {secs}s (no display -> no logs) ...")
        run_game(secs)


if __name__ == '__main__':
    main()
