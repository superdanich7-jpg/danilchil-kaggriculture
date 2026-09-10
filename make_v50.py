"""Create v50: iter40 + straw limit 12 (was 15) for better field utilization.

iter40 (limit 15) got 559.4 (new record!) but field utilization drops to 15-22% by d29.
v50: reduce limit to 12 so 7 hands can maintain the field better.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Change straw limit from 15 to 12
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 15:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 12:'
)

# 2. Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v50: iter40 + straw limit 12 (better field utilization).'
)

open("bots/v50.py", "w", encoding="utf-8").write(src)
print("v50.py created")
