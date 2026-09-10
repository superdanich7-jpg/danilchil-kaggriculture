"""Create v68: iter43 base + herd 9 (no straw target cap).

DIAGNOSIS: v67 crashes because even with zones, 10+ crop hands can't
maintain 34 straw tiles through the d18-d24 death surge. The math:
34 tiles need 34 water/day but only get 10×4=40 actions (minus DIG/HARVEST/PLANT).

VEDANT'S SECRET (from iter43 replay d12-d29): his straw STAYS at 22-34
because ALL deaths are REPLANTED THE SAME DAY. Our dig@16 releases tiles,
but replant is BLOCKED by seed shortages (we sell straw too early, no seeds).

APPROACH: Start from iter43 (stable base, 502.2 LB) and make ONLY:
1. herd_cap 9 (3 animal hands, 10+ crop hands)
2. straw target 30 (manageable for 10 crop hands)
3. straw seed buying: buy EVERY day d4-d23, no tile limit
4. straw planting: no day cutoff, no tile count cutoff beyond 30

This ensures freed tiles are replanted same-day, keeping straw stable.
"""
import re

# Read iter43 (champ = iter43/v61) as base
src = open("champ/main.py", encoding="utf-8").read()

# 1. herd_cap: 12 -> 9
src = src.replace(
    'herd_cap = 8 if melon_mode else 12',
    'herd_cap = 8 if melon_mode else 9'
)

# 2. n_anim_hands: simplify for herd 9
src = src.replace(
    '''        if herd <= 4:
            n_anim_hands = 2
        elif herd <= 9:
            n_anim_hands = 3
        else:
            n_anim_hands = 4  # ITER35: was 5 - 17-18 animals starved the crop
            # engine of labor (3 crop units for ~50 tasks = ~1 planting/day)''',
    '''        n_anim_hands = 2 if herd <= 6 else 3  # ITER48: herd 9 -> 3 animal hands, 10+ crop hands'''
)

# 3. straw target: 20 -> 30
src = src.replace(
    'counts.get("STRAWBERRY", 0) < 20:',
    'counts.get("STRAWBERRY", 0) < 30:  # ITER48: 30 tiles manageable with 10 crop hands'
)

# 4. straw seed buying: extend to d23, increase seed cap
src = src.replace(
    'if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 24:',
    'if day >= 4 and day <= 23 and seeds.get("STRAWBERRY", 0) < 40:'
)
src = src.replace(
    'n_straw = min(6, int((money - FEED_RESERVE) // 100))',
    'n_straw = min(8, int((money - FEED_RESERVE) // 100))'
)

# 5. straw planting: remove day cutoff, set tile target to 30
src = src.replace(
    'if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 20:',
    'if s > 0 and allow_straw and day <= 23 and counts.get("STRAWBERRY", 0) < 30:'
)

# 6. Animal buying: start earlier, cap lower
src = src.replace(
    'if 9 <= day <= 22 and herd < herd_cap and in_shed == 0 and money > 900',
    'if 9 <= day <= 20 and herd < herd_cap and in_shed == 0 and money > 700'
)

# 7. Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v68: herd 9 + 30 straw (iter43 base, stable replant).'
)

open("bots/v68.py", "w", encoding="utf-8").write(src)
print("v68.py created")
