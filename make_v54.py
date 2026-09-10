"""Create v54: iter35 base (unlimited straw) + kirito83 economics.

Forensics of kirito83 (127k vs our 19k):
- Sells ~400 strawberries (we sold 33!) - 33 straw tiles maintained d12-d23
- Sells ~390 fertilizer (we sold 178) - all animal fert goes to market
- 17 animals, 25 wheat tiles (self-feeding herd, no wheat purchases)
- Melon mode d0-d10 (sold 60 melons at d10 before price collapse)

Changes on iter35 base (= champ minus straw-limit):
1. Remove straw limit (iter35 behavior: plant all seeds, replant to d19)
2. wheat_quota 6 -> 14 (self-feeding herd: 16 herd needs 16 wheat/day)
3. herd_cap 12 -> 16 (more animals = more fert + milk + wool)
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Remove straw planting limit (revert to iter35: unlimited)
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 12:',
    '    if s > 0 and allow_straw and day <= 19:'
)

# 2. wheat_quota: 6 -> 14 (self-feeding herd)
src = src.replace(
    'wheat_quota = 4 if melon_mode else 6',
    'wheat_quota = 6 if melon_mode else 14'
)

# 3. herd_cap: 12 -> 16
src = src.replace(
    'herd_cap = 8 if melon_mode else 12',
    'herd_cap = 8 if melon_mode else 16'
)

# 4. Sell ALL fertilizer (kirito83 keeps zero stock; keep small reserve 2)
src = src.replace(
    '        fert_res = 0 if (day < 10 or melon_mode or day >= 27) else FERT_RESERVE',
    '        fert_res = 0 if (day < 10 or melon_mode or day >= 27) else 2'
)

# 5. Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v54: iter35 + kirito83 economics (wheat14 herd16).'
)

open("bots/v54.py", "w", encoding="utf-8").write(src)
print("v54.py created")
