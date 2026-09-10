"""Create v58: iter42 base + hire13 + straw peak 24 (winner profile).

Fresh iter42 losses analysis:
- Duc Hai Ha (108k): 13 hands, straw 21-26 tiles ALIVE d12-d24, herd 14-15
- Phu Nhan (79k): 13 hands, straw 10-15 + wheat 23-45 tiles, herd 12
- Both util 60-90% vs our 30-42%; winners drop melon after first harvest

iter42 (hire10, peak20) beat iter41 (+2.7 LB). Continue the direction:
13 hands + peak 24 = closer to winner profile. Melon planting cutoff stays
(day<18) so late melons don't waste tiles.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. max_hands: 10 -> 13
src = src.replace(
    'max_hands_today = 10 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 13 if herd >= 5 else MAX_HANDS'
)

# 2. straw peak: 20 -> 24
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 20:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 24:'
)

# 3. seeds cap: 16 -> 20 (replant reserve for 24-tile field)
src = src.replace(
    'if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 16:',
    'if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 20:'
)

# 4. Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v58: hire13 + straw peak 24 (winner profile).'
)

open("bots/v58.py", "w", encoding="utf-8").write(src)
print("v58.py created")
