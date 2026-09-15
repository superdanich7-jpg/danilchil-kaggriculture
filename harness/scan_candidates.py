"""Scan downloaded public notebooks/agents for self-contained agent candidates."""
import glob
import os
import re

TARGETS = [
    'public/lime2710/score2710-t23-kaggriculture-smart-harvest.py',
    'public/prvsiyan_moon/kaggriculture-frontier-the-moon-counts-melons_normal.py',
    'public/aurax7_v5/kaggriculture-shop-router-reactive-v5_normal.py',
    'public/prvsiyan_clock/kaggriculture-field-clock-action-budget_normal.py',
    'public/prvsiyan_rain/prvsiyan_agent.py',
    'public/tschinkel_router/kaggriculture-public-state-router-74-5-win-rate__main.py',
    'public/yhay81_shop0909/shop-router-0909__main.py',
    'public/boatlee_v16rc5/v16-rc5-high-score-8c-4s-premium-market-lead__main.py',
]

STDLIB = {'__future__', 'base64', 'copy', 'itertools', 'json', 'math', 'zlib',
          'collections', 'os', 'sys', 'random', 'time', 'functools', 'bisect',
          'heapq', 're', 'typing', 'dataclasses', 'enum', 'abc', 'string'}

for p in TARGETS:
    if not os.path.exists(p):
        print('MISSING', p)
        continue
    s = open(p, encoding='utf-8').read()
    imports = sorted(set(re.findall(r'^(?:import|from)\s+([A-Za-z_][\w.]*)', s, re.M)))
    ext = [m for m in imports if m.split('.')[0] not in STDLIB]
    print('%-72s %7d chars  agent=%s  ext=%s' % (
        p.split('/')[-1], len(s), 'def agent(' in s, ext or 'none'))
