"""Create v43: iter35 + straw planting limit 18 tiles.

Problem: iter35 plants 50 straw tiles (all die by d29).
Fix: allow buying 6 seeds/day (buffer), but only plant if straw count < 18.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Revert max_hands from 12 (iter39) to 7 (iter35)
src = src.replace(
    'max_hands_today = 12 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 7 if herd >= 5 else MAX_HANDS'
)

# 2. Add straw planting limit in _pick_crop
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 18:'
)

# 3. Docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v43: iter35 + straw planting limit 18 (prevent crash).'
)

open("bots/v43.py", "w", encoding="utf-8").write(src)
print("v43.py created")
