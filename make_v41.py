"""Create v41: exact iter35 (max_hands 7, herd_cap 12, no zones, no straw limit).

iter35 was the best submission (556.0). Every change after it made things worse.
v41 = iter39 with max_hands reverted from 12 to 7 (exact iter35 restore).
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Revert max_hands from 12 (iter39) to 7 (iter35)
src = src.replace(
    'max_hands_today = 12 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 7 if herd >= 5 else MAX_HANDS'
)

# 2. Docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v41: exact iter35 restore (max_hands 7, herd_cap 12).'
)

open("bots/v41.py", "w", encoding="utf-8").write(src)
print("v41.py created")
