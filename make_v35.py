"""Create v35: straw target 18 (not 24) for sustainable maintenance.

v34 with 24 straw tiles still crashes because the death surge (d20-d24)
overwhelms 6 crop hands. Math: 24 dead tiles / 4 days = 6 tiles/day =
18 actions (DIG+PLANT+WATER) + 12 waterings = 30 actions, but only
6 hands × 4 = 24 available. OVERLOAD.

v35: 18 straw tiles → death surge = 4.5 tiles/day = 13.5 actions +
9 waterings = 22.5 actions < 24 available. COMFORTABLE.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. herd_cap: 12 -> 6
src = src.replace(
    'herd_cap = 8 if melon_mode else 12',
    'herd_cap = 5 if melon_mode else 6'
)

# 2. max_hands_today: 12 -> 8
src = src.replace(
    'max_hands_today = 12 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 8 if herd >= 5 else MAX_HANDS'
)

# 3. n_anim_hands: simplify to 2
src = src.replace(
    '''        if herd <= 4:
            n_anim_hands = 2
        elif herd <= 9:
            n_anim_hands = 3
        else:
            n_anim_hands = 4  # ITER35: was 5 - 17-18 animals starved the crop
            # engine of labor (3 crop units for ~50 tasks = ~1 planting/day)''',
    '''        n_anim_hands = 2  # ITER35: 6 animals serviced by 2 hands'''
)

# 4. Straw seed buying: limit to 18 tiles
src = src.replace(
    '''            if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 12:
                n_straw = min(6, int((money - FEED_RESERVE) // 100))
                if n_straw >= 1:
                    market.append(["BUY_SEED", "STRAWBERRY", n_straw])''',
    '''            # ITER35: straw target 18 tiles (sustainable with 6 crop hands).
            straw_count = sum(1 for row in tiles for t in row
                              if isinstance(t, dict) and t.get("kind") == "PLANT"
                              and t.get("crop") == "STRAWBERRY")
            if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 12 \\
                    and straw_count < 18:
                n_straw = min(6, int((money - FEED_RESERVE) // 100))
                if n_straw >= 1:
                    market.append(["BUY_SEED", "STRAWBERRY", n_straw])'''
)

# 5. Straw PLANTING limit: _pick_crop must not return STRAWBERRY if >= 18
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 18:'
)

# 6. Docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v35: straw target 18 (sustainable maintenance).'
)

open("bots/v35.py", "w", encoding="utf-8").write(src)
print("v35.py created")
