"""Create v40: iter35 base + herd_cap 16 (more animals, less straw).

iter39 replay analysis shows:
- Our 50 straw tiles crash to 1-9 by d29 (total collapse)
- Winners run 16-20 animals with 0-8 straw tiles (stable high income)
- Animals give daily milk/wool; straw gives nothing when it dies

v40: revert to iter35 (max_hands 7, no zones, no straw limit) but increase
herd_cap from 12 to 16 to match winner profile.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Revert max_hands from 12 (iter39) to 7 (iter35)
src = src.replace(
    'max_hands_today = 12 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 7 if herd >= 5 else MAX_HANDS'
)

# 2. Increase herd_cap from 12 to 16 (match winners)
src = src.replace(
    'herd_cap = 8 if melon_mode else 12',
    'herd_cap = 12 if melon_mode else 16'
)

# 3. Docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v40: iter35 base + herd_cap 16 (more animals, less straw).'
)

open("bots/v40.py", "w", encoding="utf-8").write(src)
print("v40.py created")
