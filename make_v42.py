"""Create v42: iter35 + straw seeds limited to 2/day (not 6).

Problem: iter35 buys up to 6 straw seeds/day -> 50 tiles at peak -> ALL die by d29.
Fix: limit to 2/day -> ~16 tiles at peak -> spread over time -> no death surge.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Revert max_hands from 12 (iter39) to 7 (iter35)
src = src.replace(
    'max_hands_today = 12 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 7 if herd >= 5 else MAX_HANDS'
)

# 2. Limit straw seeds to 2/day (not 6)
src = src.replace(
    'n_straw = min(6, int((money - FEED_RESERVE) // 100))',
    'n_straw = min(2, int((money - FEED_RESERVE) // 100))'
)

# 3. Docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v42: iter35 + straw seeds 2/day (prevent over-planting).'
)

open("bots/v42.py", "w", encoding="utf-8").write(src)
print("v42.py created")
