"""Create v69: iter43 base + herd 9 + straw target 24 + hire 10.

DIAGNOSIS: v68 (straw 30) and v67 (straw unlimited) both crash 34->10
because death surge d18-d24 kills 20-28 tiles in 6 days. With 10 crop
hands (3 for animals), we can water ~40 tiles/day max — but DIG@16 +
replant creates 14+ death actions/day, leaving only 26 for watering.

VEDANT DIFFERENCE: his straw stays stable at 22-34 because ALL deaths
are replanted the SAME DAY. His hand ASSIGNMENT is zone-based, reducing
walking. Our nearest-first assignment wastes 40% on transit.

v69 approach: TARGET 24 tiles (not 30). Math:
- 24 tiles need 24 water/day
- death surge: ~7 tiles/day die (d16-d21) = 7 DIG + 7 PLANT = 14 actions
- available: 10 hands × 4 = 40 actions > 38 (24+14). TIGHT BUT OK.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()  # iter43/v61 base

# 1. herd_cap: 12 -> 9
src = src.replace(
    'herd_cap = 8 if melon_mode else 12',
    'herd_cap = 8 if melon_mode else 9'
)

# 2. n_anim_hands: 4 -> 3 for herd <= 9 (frees crop hands)
src = src.replace(
    '''        if herd <= 4:
            n_anim_hands = 2
        elif herd <= 9:
            n_anim_hands = 3
        else:
            n_anim_hands = 4  # ITER35: was 5 - 17-18 animals starved the crop
            # engine of labor (3 crop units for ~50 tasks = ~1 planting/day)''',
    '        n_anim_hands = 2 if herd <= 6 else 3  # ITER49: herd 9 -> 3 animal hands'
)

# 3. max_hands: 10 -> 10 (from iter44, not 13 — vedant hires 13 but only 10-11 are crop)
# Actually keep iter43's hire 10 for stability

# 4. straw target: 20 -> 24
src = src.replace(
    'counts.get("STRAWBERRY", 0) < 20:',
    'counts.get("STRAWBERRY", 0) < 24:  # ITER49: 24 tiles sustainable with 10 crop hands'
)

# 5. straw seeds: cap 24, buy up to 8/day through d21
src = src.replace(
    'if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 24:',
    'if day >= 4 and day <= 21 and seeds.get("STRAWBERRY", 0) < 48:'
)
src = src.replace(
    'n_straw = min(6, int((money - FEED_RESERVE) // 100))',
    'n_straw = min(8, int((money - FEED_RESERVE) // 100))'
)

# 6. straw planting: day <= 21 (yield age 8 on d29)
src = src.replace(
    'if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 20:',
    'if s > 0 and allow_straw and day <= 21 and counts.get("STRAWBERRY", 0) < 24:'
)

# 7. Animal buying: d9-d20 window, earlier start money threshold
src = src.replace(
    'if 9 <= day <= 22 and herd < herd_cap and in_shed == 0 and money > 900',
    'if 9 <= day <= 20 and herd < herd_cap and in_shed == 0 and money > 700'
)

# 8. Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v69: herd 9 + straw 24 (death-surge sustainable).'
)

open("bots/v69.py", "w", encoding="utf-8").write(src)
print("v69.py created")
