"""Create v64: herd_cap 12 -> 9 (match vedant profile).

KEY INSIGHT from iter43 forensics:
- vedant: herd 9-10, 13 hands, 10 crop hands -> 34 straw tiles PULLED
  CONSTANT d12-d27
- us (v63c): herd 12-13, 13 hands, 9 crop hands -> straw 20-34 d12-d15
  then DEATH SURGE crashes to 7 d29

vedant hires 13 hands and keeps them ALL on crops. We hire 13 but
n_anim_hands=4 (herd 13) steals 4 hands -> only 9 crop hands can't
maintain 34 tiles -> death surge kills everything.

FIX: herd_cap 9 -> n_anim_hands=3 -> 10 crop hands (match vedant exactly).
This is the missing piece from v63c: we built the melon->cash->straw 34
pipeline but didn't free enough hands to operate it.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. herd_cap: 12 -> 9 (match vedant)
src = src.replace(
    'herd_cap = 8 if melon_mode else 12',
    'herd_cap = 8 if melon_mode else 9'
)

# 2. n_anim_hands: simplify — herd 9 -> 3 hands (not 4)
src = src.replace(
    '''        if herd <= 4:
            n_anim_hands = 2
        elif herd <= 9:
            n_anim_hands = 3
        else:
            n_anim_hands = 4  # ITER35: was 5 - 17-18 animals starved the crop
            # engine of labor (3 crop units for ~50 tasks = ~1 planting/day)''',
    '''        n_anim_hands = 2 if herd <= 6 else 3  # ITER44: vedant has 9-10 herd, 13 hands, only 3 animal hands'''
)

# 3. Animal buying: cap herds lower
src = src.replace(
    'if 9 <= day <= 22 and herd < herd_cap and in_shed == 0 and money > 900',
    'if 9 <= day <= 22 and herd < herd_cap and in_shed == 0 and money > 700'
)

# 4. Docstring
src = src.replace(
    '"""Kaggriculture v63c: melon wave -> cash d11 -> 13 hands -> straw 34 (vedant timing).',
    '"""Kaggriculture v64: herd 9 + 13 hands + 34 straw (vedant exact profile).'
)

open("bots/v64.py", "w", encoding="utf-8").write(src)
print("v64.py created")
