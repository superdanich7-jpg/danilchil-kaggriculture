"""Create v73: iter43 base + max_hands 10 -> 12.

FUNDAMENTAL ISSUE: v70-v72 (herd 9, zones, 30-34 straw) all crash because
we can't sustain 34 straw tiles with only 7 crop hands.

vedant has 13 hands (10 crop + 3 animal), we can only afford 10 (7 crop + 3 animal).

PIVOT: Return to iter43 base (stable, 502.2 LB) which has herd 12 (herd_cap=12),
max_hands=10. The proven winner pattern: small herd, moderate straw.

v73: iter43 + max_hands 10 -> 12 (from iter39). This gives us:
- 12 hands total
- herd 12 -> n_anim_hands = 4 (for herd > 9) = 8 crop hands
- vs iter43: 10 hands, herd 12 -> 3-4 animal hands = 6-7 crop hands

1 extra crop hand = 4 more actions/day = can sustain ~4 more straw tiles.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# First, revert to iter43 base (v61): herd_cap=12, max_hands=10, straw=20
# champ is currently v63c. Need to revert:

# 1. herd_cap: 9 -> 12
src = src.replace(
    'herd_cap = 8 if melon_mode else 9',
    'herd_cap = 8 if melon_mode else 12'
)

# 2. n_anim_hands: revert to standard
src = src.replace(
    '        n_anim_hands = 2 if herd <= 6 else 3  # ITER49: herd 9 -> 3 animal hands',
    '''        if herd <= 4:
            n_anim_hands = 2
        elif herd <= 9:
            n_anim_hands = 3
        else:
            n_anim_hands = 4'''
)

# 3. max_hands: 8/13 stepwise -> 10 (iter43 base)
src = src.replace(
    'max_hands_today = (13 if day >= 12 else 8) if herd >= 5 else MAX_HANDS',
    'max_hands_today = 12 if herd >= 5 else MAX_HANDS  # ITER53: 12 hands (was 10)'
)

# 4. straw target: 30 -> 26 (12 herd = 8 crop hands, 26 tiles sustainable)
src = src.replace(
    'counts.get("STRAWBERRY", 0) < 30:  # ITER50: 30 tiles with zones, herd 9',
    'counts.get("STRAWBERRY", 0) < 26:  # ITER53: 26 tiles with 8 crop hands'
)

# 5. Strawberry planting window: continuous -> d23
src = src.replace(
    'if s > 0 and allow_straw and day <= 28:  # ITER52: NO tile count ceiling',
    'if s > 0 and allow_straw and day <= 23 and counts.get("STRAWBERRY", 0) < 26:'
)

# 6. Seed buying: d28 -> d23, reduce seed cap
src = src.replace(
    'if day >= 4 and day <= 28 and seeds.get("STRAWBERRY", 0) < 500:',
    'if day >= 4 and day <= 23 and seeds.get("STRAWBERRY", 0) < 40:'
)
src = src.replace(
    'n_straw = min(10, int((money - FEED_RESERVE) // 100))  # ITER52: buy aggressively for continuous replant',
    'n_straw = min(8, int((money - FEED_RESERVE) // 100))'
)

# 7. Animal buying window: d9-d20 -> d9-d22
src = src.replace(
    'if 9 <= day <= 20 and herd < herd_cap and in_shed == 0 and money > 700',
    'if 9 <= day <= 22 and herd < herd_cap and in_shed == 0 and money > 900'
)

# 8. Seed cap: 48 -> 40
src = src.replace(
    'and seeds.get("STRAWBERRY", 0) < 60:',
    'and seeds.get("STRAWBERRY", 0) < 40:'
)

# 9. Remove zone function (revert to nearest-first)
# Actually keep zones - they help. Comment says ITER50 but it's fine.

# 10. max_hands in comment
src = src.replace(
    'max_hands_today = 12 if herd >= 5 else MAX_HANDS  # ITER53: 12 hands (was 10)',
    'max_hands_today = 12 if herd >= 5 else MAX_HANDS  # ITER53: 12 hands (iter39 proof)'
)

# 11. Docstring
src = src.replace(
    '"""Kaggriculture v70: herd 9 + straw 30 + ZONES + stepwise hire 13.',
    '"""Kaggriculture v73: iter43 base + max_hands 12 + zones + straw 26.'
)

open("bots/v73.py", "w", encoding="utf-8").write(src)
print("v73.py created")
