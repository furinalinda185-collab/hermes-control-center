"""Install a zip pack that contains a `mods/` tree straight into the MX Bikes
mods folder, without staging it in /tmp (the tmpfs is too small for 1.4 GB)."""
import os
import shutil
import sys
import zipfile

USER_MX = os.path.expanduser(
    "~/.local/share/Steam/steamapps/compatdata/655500/pfx/"
    "drive_c/users/steamuser/Documents/PiBoSo/MX Bikes")


def install(zip_path, only_sub=None):
    z = zipfile.ZipFile(zip_path)
    n = 0
    for info in z.infolist():
        parts = info.filename.split('/')
        # expect mods/<sub>/<rel>
        if len(parts) < 3 or parts[0] != 'mods':
            continue
        sub = parts[1]
        if only_sub and sub != only_sub:
            continue
        rel = '/'.join(parts[2:])
        dest = os.path.join(USER_MX, 'mods', sub, rel)
        if info.is_dir():
            os.makedirs(dest, exist_ok=True)
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with z.open(info) as src, open(dest, 'wb') as f:
            shutil.copyfileobj(src, f, 1 << 20)
        n += 1
    return n


if __name__ == '__main__':
    path = sys.argv[1]
    sub = sys.argv[2] if len(sys.argv) > 2 else None
    print('installed', install(path, sub), 'files')
