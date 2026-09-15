import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

path = sys.argv[1]
import json

d = json.load(open(path))
names = d['info']['TeamNames']
me = names.index('DanilChil') if 'DanilChil' in names else 0
prices_by_step = []
for st in d['steps']:
    pr = (st[0].get('observation') or {}).get('market', {}).get('prices', {}) if isinstance(st[0], dict) else {}
    prices_by_step.append(pr)

stats = [defaultdict(lambda: [0, 0.0]) for _ in range(2)]  # good -> [qty, qty*price]
for si, st in enumerate(d['steps']):
    for seat in (0, 1):
        a = st[seat].get('action') if isinstance(st[seat], dict) else None
        if not isinstance(a, dict):
            continue
        pr = prices_by_step[si] if si < len(prices_by_step) else {}
        for o in (a.get('market') or []):
            if isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL':
                g, q = o[1], int(o[2])
                p = int(pr.get(g, 0))
                stats[seat][g][0] += q
                stats[seat][g][1] += q * p

print(f'episode {path} | {names}')
for g in ('MELON', 'STRAWBERRY', 'WHEAT', 'MILK', 'WOOL', 'EGG', 'FERTILIZER', 'CARROT', 'TOMATO'):
    mq, mp = stats[me][g]
    oq, op = stats[1 - me][g]
    ma = mp / mq if mq else 0
    oa = op / oq if oq else 0
    print(f'{g:11s} me: q={mq:6d} avg_p={ma:6.1f} | opp: q={oq:6d} avg_p={oa:6.1f} | price_edge={ma-oa:+6.1f}')
