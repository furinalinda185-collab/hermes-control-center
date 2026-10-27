"""Parse MX Bikes mod pages into structured download entries."""
import re
import html
import json
import urllib.request
import concurrent.futures

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
BASE = "https://mxb-mods.com"


def fetch(url, timeout=60):
    r = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(r, timeout=timeout).read().decode('utf-8', 'ignore')


def strip_tags(t):
    return html.unescape(re.sub(r'<[^>]+>', '', t)).strip()


def parse_downloads(h):
    """Return list of {name, url, kind} where kind in default/optional/server."""
    out = []
    # each download container
    for m in re.finditer(
            r'<div id="link\d+" class="download-container ([^"]*)"(.*?)(?=<div id="link\d+"|<div id="instructions"|$)',
            h, re.S):
        cls, body = m.group(1), m.group(2)
        fm = re.search(r'<div class="filename">(.*?)</div>', body, re.S)
        name = strip_tags(fm.group(1)) if fm else ''
        am = re.search(r'<a href="([^"]+)"[^>]*class="\s*count', body)
        if not am:
            am = re.search(r'<a href="([^"]+)"', body)
        if not am:
            continue
        url = html.unescape(am.group(1))
        low = name.lower()
        if 'server' in low:
            kind = 'server'
        elif 'optional' in low or 'container-opt' in cls:
            kind = 'optional'
        else:
            kind = 'default'
        out.append(dict(name=name, url=url, kind=kind))
    if out:
        return out
    # fallback: raw downloadlink divs
    for link in re.findall(r'<div class="downloadlink">([^<]+)</div>', h):
        u = html.unescape(link).strip()
        if u:
            out.append(dict(name='', url=u, kind='default'))
    return out


def parse_page(slug):
    try:
        h = fetch(f"{BASE}/{slug}/")
    except Exception as e:
        return dict(slug=slug, error=str(e), ok=False)
    d = dict(slug=slug, ok=True)
    m = re.search(r'Total downloads:\s*([\d,]+)', h)
    d['downloads'] = int(m.group(1).replace(',', '')) if m else 0
    bm = re.search(r'Made for\s*<b>Beta\s*(\d+)</b>', h)
    d['beta'] = 'b' + bm.group(1) if bm else ''
    tm = re.search(r'<h1 class="post-title"[^>]*>(.*?)</h1>', h, re.S)
    d['title'] = strip_tags(tm.group(1)) if tm else slug
    d['files'] = parse_downloads(h)
    # track id mentioned in page (Track ID: xxx)
    tim = re.search(r'Track ID:</b>\s*([^<]+)', h)
    if tim:
        d['track_id'] = tim.group(1).strip()
    return d


def bulk(slugs, workers=8):
    res = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for d in ex.map(parse_page, slugs):
            res.append(d)
    return res


if __name__ == '__main__':
    import sys
    slugs = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    res = bulk(slugs)
    json.dump(res, open(sys.argv[2], 'w'), indent=1)
    for d in res:
        if not d.get('ok'):
            print(f"ERR {d['slug']}: {d.get('error')}")
            continue
        kinds = {}
        for f in d['files']:
            kinds[f['kind']] = kinds.get(f['kind'], 0) + 1
        print(f"{d['downloads']:>7} {d.get('beta',''):>4} {d['title'][:44]:46s} {kinds}")
