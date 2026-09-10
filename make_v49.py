"""Create v49: iter35 + straw limit 15 (compromise between 18 and 8).

Testing different limits:
- v43 (limit 18): money 51-55k, straw 18→6
- v48 (limit 8): money 33-35k, straw 8→2

v49: limit 15 for balance between straw income and maintenance capacity.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Revert max_hands from 12 (iter39) to 7 (iter35)
src = src.replace(
    'max_hands_today = 12 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 7 if herd >= 5 else MAX_HANDS'
)

# 2. Straw planting limit: 15 tiles
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 15:'
)

# 3. Docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v49: iter35 + straw limit 15 (compromise).'
)

open("bots/v49.py", "w", encoding="utf-8").write(src)
print("v49.py created")
