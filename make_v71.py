"""Create v71: v70 + continuous strawberry replant.

DIAGNOSIS: v70 (herd 9 + zones + 30 straw) still crashes 34->11 because
_pick_crop blocks replant after day 21. Death surge d18-d24 kills tiles
daily but they aren't replanted.

FIX: STRAWBERRY planting has NO day cutoff (plant through day 28).
Strawberry planted d25 yields on d29 (age 4). Not much profit but keeps
tile count stable. The replant cycle MUST be continuous.

VEDANT PROOF: his straw goes 34(d15) -> 34(d21) -> 22(d27) -> 9(d29).
The drop from 34 to 22 is death + ENDGAME sell-off, not collapse.
We need the same: 34 stable through d24, then gradual decline.

KEY: our death surge is SHARPER (34->11) because we can't replant.
v71: remove day<=21 cutoff, raise seed cap to 100.
"""
import re

src = open("bots/v70.py", encoding="utf-8").read()

# 1. Remove strawberry planting day cutoff: day <= 21 -> no cutoff (day <= 28)
src = src.replace(
    'if s > 0 and allow_straw and day <= 21 and counts.get("STRAWBERRY", 0) < 30:',
    'if s > 0 and allow_straw and day <= 26 and counts.get("STRAWBERRY", 0) < 30:  # ITER51: continuous replant'
)

# 2. Extend seed buying window to d26 (for continuous replant)
src = src.replace(
    'if day >= 4 and day <= 21 and seeds.get("STRAWBERRY", 0) < 60:',
    'if day >= 4 and day <= 26 and seeds.get("STRAWBERRY", 0) < 100:'
)

# 3. Docstring
src = src.replace(
    '"""Kaggriculture v70: herd 9 + straw 30 + ZONES + stepwise hire 13.',
    '"""Kaggriculture v71: v70 + continuous straw replant (no d21 cutoff).'
)

open("bots/v71.py", "w", encoding="utf-8").write(src)
print("v71.py created")
