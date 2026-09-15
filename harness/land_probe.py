import inspect
import re

import kaggle_environments.envs.kaggriculture.kaggriculture as m

src = inspect.getsource(m)

print('=== BUY_LAND occurrences ===')
for mo in re.finditer(r'BUY_LAND', src):
    s = max(0, mo.start() - 300)
    e = min(len(src), mo.end() + 300)
    print('--- @', mo.start())
    print(src[s:e])
    print()

print('=== land cost ===')
for mo in re.finditer(r'(?i)land', src):
    s = max(0, mo.start() - 120)
    e = min(len(src), mo.end() + 200)
    snippet = src[s:e]
    if 'cost' in snippet.lower() or 'price' in snippet.lower():
        print('--- @', mo.start())
        print(snippet)
        print()

print('=== quadrant / unlock ===')
for kw in ('unlocked', 'quadrant', 'LOCKED', 'buy_land'):
    for mo in re.finditer(kw, src):
        s = max(0, mo.start() - 200)
        e = min(len(src), mo.end() + 300)
        print('--- ', kw, '@', mo.start())
        print(src[s:e])
        print()
        break