"""Create v34: straw-heavy specialization (yatakeuc profile).

Key insight from iter39 replays: our straw PEAKS at 42-49 tiles (d15-d18) then
CRASHES to 3-12 by d29. Winners (yatakeuc) maintain 25-32 tiles with 7-8 hands
and 5 animals. Our 13 animals + 12 hands = 5 animal hands + 7 crop hands =
impossible to maintain 42-49 straw tiles.

Fix: specialize. herd_cap 6, max_hands 8, n_anim_hands 2, straw target 24.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. herd_cap: 12 -> 6 (match yatakeuc)
src = src.replace(
    'herd_cap = 8 if melon_mode else 12',
    'herd_cap = 5 if melon_mode else 6'
)

# 2. max_hands_today: 12 -> 8 (match yatakeuc)
src = src.replace(
    'max_hands_today = 12 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 8 if herd >= 5 else MAX_HANDS'
)

# 3. n_anim_hands: simplify to 2 for herd <= 6
src = src.replace(
    '''        if herd <= 4:
            n_anim_hands = 2
        elif herd <= 9:
            n_anim_hands = 3
        else:
            n_anim_hands = 4  # ITER35: was 5 - 17-18 animals starved the crop
            # engine of labor (3 crop units for ~50 tasks = ~1 planting/day)''',
    '''        n_anim_hands = 2  # ITER34: 6 animals serviced by 2 hands (enough)'''
)

# 4. Straw seed buying: limit to 24 tiles total (prevent over-planting)
src = src.replace(
    '''            if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 12:
                n_straw = min(6, int((money - FEED_RESERVE) // 100))
                if n_straw >= 1:
                    market.append(["BUY_SEED", "STRAWBERRY", n_straw])''',
    '''            # ITER34: straw target 24 tiles (sustainable with 6 crop hands).
            # Don't buy seeds if we already have 24+ straw tiles planted.
            straw_count = sum(1 for row in tiles for t in row
                              if isinstance(t, dict) and t.get("kind") == "PLANT"
                              and t.get("crop") == "STRAWBERRY")
            if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 12 \\
                    and straw_count < 24:
                n_straw = min(6, int((money - FEED_RESERVE) // 100))
                if n_straw >= 1:
                    market.append(["BUY_SEED", "STRAWBERRY", n_straw])'''
)

# 4b. Straw PLANTING limit: _pick_crop must not return STRAWBERRY if >= 24 tiles
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 24:'
)

# 5. Update docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v34: straw-heavy specialization (yatakeuc profile).'
)

open("bots/v34.py", "w", encoding="utf-8").write(src)
print("v34.py created")
