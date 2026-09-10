"""Create v52: iter40 (limit 15) + wheat quota 6->10 for better field utilization.

iter40 got 559.4 but field utilization drops to 15-22% by d29 (empty tiles).
v52: increase wheat quota from 6 to 10 to fill more tiles.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Change straw limit from 12 (iter41) to 15 (iter40)
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 12:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 15:'
)

# 2. Increase wheat quota from 6 to 10
src = src.replace(
    'wheat_quota = 4 if melon_mode else 6',
    'wheat_quota = 6 if melon_mode else 10'
)

# 3. Docstring
src = src.replace(
    '"""Kaggriculture v51: iter41 + straw limit 13 (more income).',
    '"""Kaggriculture v52: iter40 + wheat quota 10 (better field utilization).'
)

open("bots/v52.py", "w", encoding="utf-8").write(src)
print("v52.py created")
