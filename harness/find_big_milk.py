import json
from collections import Counter

path = 'replays/i53losses/episode-109015958-replay.json'
d = json.load(open(path))
names = d['info']['TeamNames']
me = names.index('DanilChil') if 'DanilChil' in names else 0
big = []
for si, st in enumerate(d['steps']):
    a = st[me].get('action') if isinstance(st[me], dict) else None
    if isinstance(a, dict):
        for o in (a.get('market') or []):
            if isinstance(o, list) and len(o) >= 3 and o[1] == 'MILK' and int(o[2]) > 3000:
                big.append((si, o[0], int(o[2])))
print('big milk orders (step, type, qty):', big[:10], 'total', len(big))
