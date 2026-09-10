"""Create v46: iter35 + straw limit 18 only (no zones, no herd_cap change).

Simplest possible change to iter35: just prevent the strawberry crash.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Revert max_hands from 12 (iter39) to 7 (iter35)
src = src.replace(
    'max_hands_today = 12 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 7 if herd >= 5 else MAX_HANDS'
)

# 2. Straw planting limit: 18 tiles
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 18:'
)

# 3. Docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v46: iter35 + straw limit 18 only.'
)

open("bots/v46.py", "w", encoding="utf-8").write(src)
print("v46.py created")
