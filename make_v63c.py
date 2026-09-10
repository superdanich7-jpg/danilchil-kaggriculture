"""Create v63c: v63 + stepwise hiring (8 hands until d11, then 13 hands).

CRITICAL: v63 hires 13 hands from d1 = cash death. vedant hires AFTER
selling the melon crop (d11-12 = +9k cash). We replicate the exact pattern:
d1-d11: max 8 hands (survive on straw revenue), d12+: 13 hands (funded by melon sale).

This is the difference between "copy top layout" (v63 fails: 55 on d15) and
"copy top timing" (v63c targets: d12=8960, then 13 hands sustain 34 straw tiles).
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Day-0 melon seeds: 3 -> 12
src = src.replace(
    '["BUY_SEED", "MELON", 3], ["BUY_SEED", "WHEAT", 4],',
    '["BUY_SEED", "MELON", 12], ["BUY_SEED", "WHEAT", 4],'
)

# 2. melon_quota: 13 -> 20 in both modes (melon wave for cash)
src = src.replace(
    'melon_quota = 20 if melon_mode else 13',
    'melon_quota = 20 if melon_mode else 20'
)

# 3. STEPWISE hiring: 8 hands until d11, then 13 hands from d12
src = src.replace(
    'max_hands_today = 10 if herd >= 5 else MAX_HANDS',
    'max_hands_today = (13 if day >= 12 else 8) if herd >= 5 else MAX_HANDS'
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
    '"""Kaggriculture v63c: melon wave -> cash d11 -> 13 hands -> straw 34 (vedant timing).'
)

open("bots/v63c.py", "w", encoding="utf-8").write(src)
print("v63c.py created")
