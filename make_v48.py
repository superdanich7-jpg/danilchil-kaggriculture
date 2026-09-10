"""Create v48: iter35 + herd_cap 20 + straw limit 8 (animal focus).

From replay analysis: some winners run 16-20 animals with 0-8 straw.
iter35 runs 12 animals + 50 straw (trying to do both, doing neither well).
v48: focus on animals, minimize straw.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Revert max_hands from 12 (iter39) to 7 (iter35)
src = src.replace(
    'max_hands_today = 12 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 7 if herd >= 5 else MAX_HANDS'
)

# 2. Increase herd_cap from 12 to 20
src = src.replace(
    'herd_cap = 8 if melon_mode else 12',
    'herd_cap = 12 if melon_mode else 20'
)

# 3. Straw planting limit: 8 tiles (minimal)
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 8:'
)

# 4. Docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v48: iter35 + herd_cap 20 + straw limit 8 (animal focus).'
)

open("bots/v48.py", "w", encoding="utf-8").write(src)
print("v48.py created")
