"""Create v63: melon wave 20 -> cash -> strawberry 34 (vedant path to 91k).

vedant patnala forensics (91k vs our 49.9k):
- d1: 12 melon tiles (we do 15) -> d8: 20 melon tiles -> sold all d11-12 (+9k)
- d12: hires up to 13 hands -> 34 strawberry tiles CONSTANT d13-d25
- herd only 9-10 early, wheat 12-23 tiles, fert sells ~200+
- His money: d8 = 4 (all-in), d12 = 8960, then +4-7k/day

v63 changes on iter43 base:
1. Day-0 melon seeds 3 -> 12 (wave of 20 tiles)
2. melon_quota div 13 -> 20
3. max_hands 10 -> 13 (from d12, funded by melon sale)
4. straw peak 20 -> 34, seeds cap 16 -> 24, buying 6 -> 8/day
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Day-0 melon seeds: 3 -> 12
src = src.replace(
    '["BUY_SEED", "MELON", 3], ["BUY_SEED", "WHEAT", 4],',
    '["BUY_SEED", "MELON", 12], ["BUY_SEED", "WHEAT", 4],'
)

# 2. melon_quota: 13 -> 20 in div mode
src = src.replace(
    'melon_quota = 20 if melon_mode else 13',
    'melon_quota = 20 if melon_mode else 20'
)

# 3. max_hands: 10 -> 13
src = src.replace(
    'max_hands_today = 10 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 13 if herd >= 5 else MAX_HANDS'
)

# 4. straw peak: 20 -> 34
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 20:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 34:'
)

# 5. straw seeds: cap 16 -> 24, buy 8/day
src = src.replace(
    'if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 16:',
    'if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 24:'
)
src = src.replace(
    'n_straw = min(6, int((money - FEED_RESERVE) // 100))',
    'n_straw = min(8, int((money - FEED_RESERVE) // 100))'
)

# 6. Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v63: melon wave 20 -> cash -> straw 34 (vedant path).'
)

open("bots/v63.py", "w", encoding="utf-8").write(src)
print("v63.py created")
