import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

files = [
    ('makishis   ', 'replays/i48losses/episode-108604290-replay.json'),
    ('Kundan     ', 'replays/i48losses/episode-108556198-replay.json'),
    ('IvanShkurak', 'replays/i48losses/episode-108653628-replay.json'),
    ('dp23334    ', 'replays/i48losses/episode-108573290-replay.json'),
    ('latentb    ', 'replays/i48losses/episode-108576630-replay.json'),
]

goods = ['WHEAT', 'EGG', 'MILK', 'WOOL', 'FERTILIZER', 'STRAWBERRY', 'CARROT', 'MELON', 'TOMATO']

print(f"{'good':11s} | " + ' | '.join(f'{n} me/op' for n, _ in files))
totals = defaultdict(int)
for idx, (name, path) in enumerate(files):
    d = json.load(open(path))
    names = d['info']['TeamNames']
    me = names.index('DanilChil') if 'DanilChil' in names else 0
    opp = 1 - me
    vol = [defaultdict(int), defaultdict(int)]
    for st in d['steps']:
        for seat in (me, opp):
            a = st[seat]['action']
            if isinstance(a, dict):
                for o in (a.get('market') or []):
                    if o and o[0] == 'SELL' and len(o) >= 3:
                        vol[0 if seat == me else 1][o[1]] += int(o[2])
    for g in goods:
        m, p = vol[0][g], vol[1][g]
        totals[g] += m - p
        print(f'{g:11s} | {name} {m:5d}/{p:5d} diff={m-p:+6d}')
print('\nTOTAL diff (me - opp) per good:', dict(totals))
