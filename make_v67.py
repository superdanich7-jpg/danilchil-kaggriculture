"""Create v67: remove strawberry planting cutoff (continuous replant).

DIAGNOSIS: v66 (dig@16, target 26) crashes 26->22->16->2 because after DIG
releases 26 tiles, _pick_crop won't replant them (counts[STRAWBERRY]=26 blocks
the < 26 check). The "dead replant loop" — tiles freed but never replanted.

FIX: remove the counts quota entirely from _pick_crop. The quota should only
limit SEED purchases, not actual planting. If we have seeds and free tiles,
we MUST plant. Otherwise freed tiles stay empty and straw dies.

Also: strawberry planting window d4-d19 is too early cutoff. vedant plants
strawberry through d21+ (his d9 straw=20 grows to 34 by d12-d15). We need
planted-day 21 strawberries to yield at day 29 (age 8).
Window: d4-d21 (21+8=29 = last harvest on d29).

NOTE: this means we replant into d26+, but that's fine — strawberries planted
d21 yield ages 4,6,8,10... d25 gives final harvest (age 4). It's marginal
income, not 0.
"""
import re

src = open("bots/v66.py", encoding="utf-8").read()

# 1. Remove strawberry planting cutoff: day <= 19 -> day <= 21 (yields on d29)
src = src.replace(
    'if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 26:',
    'if s > 0 and allow_straw and day <= 21:  # ITER47: extended to d21 (age 8 yield on d29)'
)

# 2. Remove strawberry seed buying window: day <= 19 -> day <= 23 (supports replant)
src = src.replace(
    'if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 24 \\',
    'if day >= 4 and day <= 23 and seeds.get("STRAWBERRY", 0) < 40 \\'
)

# 3. Remove seed purchase cap: 24 -> 80 (effectively no limit, seeds are cheap)
src = src.replace(
    'and straw_count < 24:',
    'and straw_count < 80:'
)

# 4. Docstring
src = src.replace(
    '"""Kaggriculture v66: dig@16 + target 26 straw (death surge spread).',
    '"""Kaggriculture v67: continuous straw replant (no quota blocks planting).'
)

open("bots/v67.py", "w", encoding="utf-8").write(src)
print("v67.py created")
