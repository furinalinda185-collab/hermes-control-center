# Preserving a game install that is too big for git

For content trees in the tens of GB (modded games, emulator libraries, asset
packs). Git is for the knowledge; the bulk comes back by re-download.

## 1. Decide by measuring

    du -sh <data dir>/*        | sort -h     # what is big
    du -sh <data dir>          # total — >5G means content cannot be committed
    find <data dir> -type f -size +50M       # anything near the 100MB/file cap

Split the tree into three buckets:

- **commit** — configs, settings, profiles, presets, custom/user-created content,
  tooling scripts;
- **describe** — bulk packs: an install-unit inventory (what to download) and a
  per-file manifest (how to prove it came back intact);
- **ignore** — regenerable caches and large per-object telemetry.

## 2. Copy the small bucket, excluding the bulk

`rsync` may not be installed; a tar pipe needs nothing extra and keeps the
relative layout:

    mkdir -p "$DST/config"
    tar -C "$SRC/profiles" --exclude='*.dfm' -cf - . | tar -C "$DST/config/profiles" -xf -

Same shape for any exclusion: `tar -C src --exclude='cache/**' --exclude='*.log'
-cf - . | tar -C dst -xf -`. Verify with `du -sh` and a file count afterwards;
`cp -aL` where symlinks exist.

## 3. Manifest (verification)

    find "$DATA" -type f -printf '%s\t%TY-%Tm-%TdT%TH:%TM\t%P\n' | sort -t$'\t' -k3 \
      > manifest.txt

Header a few `#` lines saying the content itself is not in the repo and telling
the reader to diff path + byte size after restoring. Assert completeness before
committing: manifest data lines must equal `find "$DATA" -type f | wc -l`.
Skip hashing multi-GB trees — size + mtime is enough to catch a truncated or
wrong download, and hashing 29G costs minutes the user does not have mid-swap.

## 4. Inventory (reinstall list)

One row per **install unit**, not per file: `kind, category, name, form, bytes,
relative path, source hint`. Group members of a pack by filename prefix so a
148-item install becomes 5 rows. Include a short `## How to reinstall` section
with the tool order, the paths on the new machine, and the verification counts.

Warn in the file when sources were never recorded ("no download URLs were
captured; re-find each item by name on the site") — a future session must not
discover that after wiping.

## 5. Commit and prove it landed remotely

    gh api repos/<owner>/<repo>/contents/<dir> --jq '.[] | .name'
    gh api repos/<owner>/<repo>/contents/<dir>/<file> --jq '.size'   # vs local stat -c %s
    gh api repos/<owner>/<repo>/commits/<sha> --jq '.files | length' # vs git show --name-only

Add a line to the control-center `MANIFEST.txt` for the new top-level directory
(file count + size + one-line description). A backup counts only once the file
is readable from the remote.
