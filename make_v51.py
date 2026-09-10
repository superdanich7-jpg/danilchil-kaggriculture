"""Create v42: iter41 + straw limit 13 (was 12) for more income.

iter41 (limit 12): 4 wins, 0 losses, but money 40k-56k (less than iter40's 44k-59k).
v42: increase limit to 13 for slightly more income while keeping stability.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Change straw limit from 12 to 13
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 12:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 13:'
)

# 2. Docstring
src = src.replace(
    '"""Kaggriculture v50: iter40 + straw limit 12 (better field utilization).',
    '"""Kaggriculture v51: iter41 + straw limit 13 (more income).'
)

open("bots/v51.py", "w", encoding="utf-8").write(src)
print("v51.py created")
