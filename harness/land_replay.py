import json
from collections import Counter

path = r'replays/i53losses/episode-109019130-replay.json'
d = json.load(open(path))
info = d.get('info', {})
names = info.get('TeamNames') or info.get('teamNames')
print('teams:', names)

NAMES = names or ['A', 'B']
buy_land = [0, 0]


def tile_stats(farm):
    kinds = Counter()
    crops = Counter()
    for row in farm.get('tiles') or []:
        for t in row:
            if t is None:
                kinds['EMPTY'] += 1
            elif t == 'LOCKED':
                kinds['LOCKED'] += 1
            elif isinstance(t, dict):
                kinds[t.get('kind')] += 1
                if t.get('kind') == 'PLANT' and t.get('crop'):
                    crops[t['crop']] += 1
            elif isinstance(t, str):
                kinds[t] += 1
    return kinds, crops


steps = d['steps']
for idx in range(0, len(steps), 24):
    st = steps[idx]
    day = idx // 24
    if day % 3 != 0 and day not in (24, 26, 28):
        continue
    line = ['d%02d' % day]
    for seat in (0, 1):
        obs = st[seat].get('observation') or {}
        farms = obs.get('farms') or []
        farm = farms[seat] if len(farms) > seat else None
        if not farm:
            line.append('%s: n/a' % NAMES[seat])
            continue
        kinds, crops = tile_stats(farm)
        line.append(
            '%s: money=%s q=%s hands=%s crops=%s locked=%s empty=%s' % (
                NAMES[seat], farm.get('money'), farm.get('unlocked_quadrants'),
                len(farm.get('hands') or []), dict(crops), kinds.get('LOCKED', 0), kinds.get('EMPTY', 0))
        )
    print(' | '.join(line))

print()
for idx, st in enumerate(steps):
    day = idx // 24
    for seat in (0, 1):
        a = st[seat].get('action')
        if isinstance(a, dict):
            for o in (a.get('market') or []):
                if o and o[0] == 'BUY_LAND':
                    buy_land[seat] += 1
                    print('  BUY_LAND by %s at step %d (day %d) #[%d]' % (NAMES[seat], idx, day, buy_land[seat]))
print('total BUY_LAND:', dict(zip(NAMES, buy_land)))
