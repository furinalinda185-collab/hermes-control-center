"""Add a 'category' field to each plan item, using the site's own track-type
classification (motocross / supercross / supermoto / enduro / ...)."""
import json
import re
import urllib.request
import concurrent.futures

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
CAT_IDS = json.load(open('/tmp/cat_ids.json'))
ID_TO_SLUG = {v: k for k, v in CAT_IDS.items()}

# the site's own track-type categories, in priority order
TYPE_SLUGS = ['motocross', 'supercross', 'supermoto', 'enduro', 'endurocross',
              'arenacross', 'straight-rhythm', 'freeride', 'bikelife',
              'replicas', 'tracks-beginner', 'tracks-intermediate', 'tracks-pro']


def categories_for(slug):
    """Return the track-type categories the site assigns to this post."""
    u = (f"https://mxb-mods.com/wp-json/wp/v2/posts?slug={slug}&_fields="
         "categories")
    try:
        r = urllib.request.Request(u, headers=UA)
        d = json.load(urllib.request.urlopen(r, timeout=60))
    except Exception:
        return []
    if not d:
        return []
    out = []
    for cid in d[0].get('categories', []):
        s = ID_TO_SLUG.get(cid)
        if s:
            out.append(s)
    return out


def pick_category(cats):
    """Map site categories to the game's mods/tracks/<category> folder."""
    # game folders: motocross, supercross, supermoto, enduro, straight rhythm
    if 'straight-rhythm' in cats:
        return 'straight rhythm'
    for pref in ('motocross', 'supercross', 'supermoto', 'enduro'):
        if pref in cats:
            return pref
    if 'endurocross' in cats:
        return 'enduro'
    if 'freeride' in cats:
        return 'motocross'
    if 'bikelife' in cats:
        return 'motocross'
    return 'motocross'


if __name__ == '__main__':
    plan = json.load(open('/tmp/plan_tracks.json'))
    slugs = [p['slug'] for p in plan]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        cats = list(ex.map(categories_for, slugs))
    for p, c in zip(plan, cats):
        p['site_categories'] = c
        p['category'] = pick_category(c)
    json.dump(plan, open('/tmp/plan_tracks.json', 'w'), indent=1)
    for p in plan:
        print(f"  {p['category']:16s} {p['title'][:46]:48s} {p.get('site_categories')}")
