"""Build the install plan from the ranked community content.

Selection rules for "popular online servers":
  * tracks: high download count, has a SERVER version published (strong signal
    the track is used on dedicated servers), beta >= 18, default (player) file
  * bikes: OEM + A-Kit + E10 packs, which are what servers broadcast
"""
import json
import sys

allp = json.load(open('/tmp/all.json'))
ok = [p for p in allp if p.get('ok')]


def has_kind(p, kind):
    return any(f['kind'] == kind for f in p.get('files', []))


def default_files(p):
    return [f for f in p['files'] if f['kind'] == 'default']


def beta_ok(p, min_beta):
    b = p.get('beta', '')
    if not b:
        return True
    try:
        return int(b[1:]) >= min_beta
    except ValueError:
        return True


tracks = [p for p in ok
          if p['slug'] in TRACK_SLUGS] if False else []

TRACK_SLUGS = {
    # beta19-era, server-version published => runs on dedicated servers
    'across-the-sea', 'temecula-creek', 'quarry-basin-ish-from-mx-vs-atv-alive',
    'forest-hills-mx', 'kmx-mesquite-mx', 'mnsr-raceway', 'fury-mx-facility',
    'kellz-washougal', 'earthurx-x-feulatracks-2025-rd16-denver', 'havoc-raceway',
    'silver-valley-mx-park', 'into-the-wild', 'arcola-mx', 'redline-valley-by-ps',
    'iron-ridge-by-musket', 'raska-mx', 'the-island', 'glen-helen-raceway-2018',
    'norwood-mx', 'swampland-mx-2', 'cappadocia-hills', 'sleepy-hollow-mx',
    'lake-elsinore-by-ps', 'impact-designs-raceway', 'cjsx-round-1',
    'senderville-snowcross-showdown', 'highside-motocross-2', 'northwest-map',
    'outpost-nevada', 'cw-unadilla-24', 'ponca-city-rd-x-kmx',
    'kmx-spring-a-ding', 'the-hideout',
    # highest-download classics that servers still rotate
    'swedish-midsummer-carnage-2', 'shmeezeville', 'country-side',
    'mouse-motopark', 'kellz-fox-raceway-2023', 'kellz-redbud-2023',
    'bigsendmx', 'poor-boyz-mx', '2023-dreamland-mx', 'compound-637',
    'cairo-gp',
}

BIKE_SLUGS = {
    'oem-bike-pack', 'a-kit-bike-pack-production-build',
    'eleven10-mods-factory-bike-open-test', 'enduro-bike-pack',
    'freeride-oem-bike-pack', 'sm-oem-bike-pack',
}

if __name__ == '__main__':
    mode = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    if mode == 'tracks':
        slugs = TRACK_SLUGS
        minb = 18
    else:
        slugs = BIKE_SLUGS
        minb = 0

    picked = []
    for p in ok:
        if p['slug'] not in slugs:
            continue
        if not default_files(p):
            continue
        if not beta_ok(p, minb):
            continue
        picked.append(p)

    # rank: server-version presence first, then downloads
    picked.sort(key=lambda p: (has_kind(p, 'server'), p.get('downloads', 0)),
                reverse=True)
    picked = picked[:limit]
    json.dump(picked, open(f'/tmp/plan_{mode}.json', 'w'), indent=1)
    print(f"plan_{mode}: {len(picked)} items")
    for p in picked:
        print(f"  {p.get('downloads',0):>7} {p.get('beta',''):>4} "
              f"server={has_kind(p,'server')} {p['title'][:50]}")
