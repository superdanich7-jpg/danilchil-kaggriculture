"""Fresh iter46 replay forensics: strongest opponents' crop mix + utilization."""
import json
import glob
from collections import Counter

for path in sorted(glob.glob('replays/iter46/episode-107*.json')):
    d = json.load(open(path))
    steps = d['steps']
    teams = d.get('info', {}).get('TeamNames', d.get('TeamNames', ['?', '?']))
    last = steps[-1]
    # rewards structure varies: list of per-seat dicts with observation.farms
    mon = []
    for i in (0, 1):
        entry = last[i] if isinstance(last, list) else last
        obs = entry.get('observation', {})
        farms = obs.get('farms', [])
        mon.append(int(farms[i]['money']) if farms else 0)
    print('===', path.split('/')[-1].split('-replay')[0], teams, 'final money:', mon)
    if min(mon) == 0 and max(mon) == 0:
        continue
    seat = mon.index(max(mon))
    for day in (9, 15, 19, 21, 24, 29):
        st = steps[day * 24]
        entry = st[seat] if isinstance(st, list) else st
        obs = entry.get('observation', {})
        farms = obs.get('farms', [])
        if not farms:
            continue
        tiles = farms[seat]['tiles']
        c = Counter()
        herd = 0
        for row in tiles:
            for t in row:
                if isinstance(t, dict):
                    if t.get('animal'):
                        herd += 1
                    elif t.get('kind') == 'PLANT':
                        c[t.get('crop')] += 1
                    elif t.get('kind') == 'WEED':
                        c['WEED'] += 1
        planted = sum(v for k, v in c.items() if k != 'WEED')
        util = planted / max(1, 100 - c.get('WEED', 0)) * 100
        print('  d%2d: straw=%3d melon=%3d wheat=%2d weeds=%3d util=%4.0f%% herd=%d' % (
            day, c.get('STRAWBERRY', 0), c.get('MELON', 0), c.get('WHEAT', 0),
            c.get('WEED', 0), util, herd))
