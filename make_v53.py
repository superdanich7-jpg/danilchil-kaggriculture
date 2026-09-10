"""Create v53: kirito83 profile (winner of 127k vs our 19k).

kirito83 replay analysis: 12 hands, 17 animals, 33 straw, 25 wheat, util=100%.
Our iter41: 7 hands, 12 animals, 12 straw, feed gap covered by PURCHASES.

Key leak: wheat_quota=6 feeds only 6/day, herd needs 12/day -> we BUY wheat
(45*qty) losing ~280 coins/day. kirito83 grows his own feed.

v53 changes (synergistic kirito83 profile):
1. wheat_quota 6 -> 12 (self-feeding herd, kill the purchase leak)
2. max_hands 7 -> 9 (labor for larger field ops; salaries ~50/day cheap)
3. straw limit 12 -> 16 (more crop income, hands can service it)
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. wheat_quota: 6 -> 12 (self-feeding herd)
src = src.replace(
    'wheat_quota = 4 if melon_mode else 6',
    'wheat_quota = 6 if melon_mode else 12'
)

# 2. max_hands: 7 -> 9
src = src.replace(
    'max_hands_today = 7 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 9 if herd >= 5 else MAX_HANDS'
)

# 3. straw limit: 12 -> 16
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 12:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 16:'
)

# 4. Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v53: kirito83 profile (wheat12 hands9 straw16).'
)

open("bots/v53.py", "w", encoding="utf-8").write(src)
print("v53.py created")
