"""Create v77: full-field utilization (songxin formula).

Back-end bug confirmed from iter46 replays: after straw cutoff d19, 45+ tiles
sit EMPTY until d29 (util 44-48% vs tops 62-76%). The missing tiles are WHEAT
(s log impact 0.2 - price never collapses) - the free real estate tops use.

songxin (beat us 84.9k vs 62.5k): straw 16-21, melon 11 held to d18, herd 15,
wheat fills the rest, util 62-70%.
Farming Sols (beat us): wheat 8-9 CONSTANT, melon 3, herd 12, util 76%.
Their wheat = FREE animal feed (we buy feed!).

v77 = iter46 base + :
1. straw planting target 34 -> 20 (songxin 16-21; 34 starved wheat+melon tiles)
2. wheat quota 6 -> 15 (fill freed tiles with wheat; wheat feeds the herd FREE)
3. wheat planting window d25 -> d26
4. melon cutoff 13 -> 15 (hold the wave a bit longer, songxin holds to d18)
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. straw planting target 34 -> 20 (find v76's limit; it came through v73
#    lineage which used 34). Handle both 34 and 26/24 variants.
src, n34 = re.subn(
    r'counts\.get\("STRAWBERRY", 0\) < 34',
    'counts.get("STRAWBERRY", 0) < 20', src)
src, n26 = re.subn(
    r'counts\.get\("STRAWBERRY", 0\) < 26',
    'counts.get("STRAWBERRY", 0) < 20', src)

# 2. wheat quota: default 6 -> 15 (both melon_mode and div branches)
src, nw1 = re.subn(r'wheat_quota = 4 if melon_mode else 6',
                   'wheat_quota = 12 if melon_mode else 15', src)
src, nw2 = re.subn(r'wheat_quota=6\)', 'wheat_quota=15)', src)

# 3. wheat planting window: day <= 25 -> day <= 26
src, nd1 = re.subn(r'counts\.get\("WHEAT", 0\) < wheat_quota and day <= 25',
                   'counts.get("WHEAT", 0) < wheat_quota and day <= 26', src)

# 4. melon cutoff 13 -> 15 (v61 lineage: "day < 13" in _pick_crop)
src, nm1 = re.subn(r'counts\.get\("MELON", 0\) < melon_quota and day < 13',
                   'counts.get("MELON", 0) < melon_quota and day < 15', src)
src, nm2 = re.subn(r'counts\.get\("MELON", 0\) < melon_quota and day < 18',
                   'counts.get("MELON", 0) < melon_quota and day < 15', src)

# 5. docstring
src, nds = re.subn(
    r'"""Kaggriculture [^"]*"""',
    '"""Kaggriculture v77: full-field utilization (songxin formula). '
    'straw 20 + wheat 15 fills freed tiles (util 44% -> 65%+), '
    'wheat feeds the herd free, melon wave held to d15."""', src, count=1)

open("bots/v77.py", "w", encoding="utf-8").write(src)
print(f"v77 created: straw<20 x{n34+n26}, wheat x{nw1+nw2}, "
      f"window x{nd1}, melon x{nm1+nm2}, doc x{nds}")
