"""Create v66: strawberry dig age 18 -> 16 (pre-death-surge cleanup).

DIAGNOSIS from iter43/iter44 replays: strawberry death surge d18-d24
kills 20-28 tiles in 4 days. With 10 crop hands:
- watering ALL live tiles: ~14 actions/day (14 tiles × 1 water)
- handling deaths: ~7 actions/day (7 dead tile digs + 7 plants)
- planting new: ~7 actions/day
TOTAL: 28 actions vs 40 available (10 hands × 4 actions) — OVERLOADED

ROOT CAUSE: the 18-age dig is TOO LATE. Tiles age 18 on d18, but
harvest age is 18 (yield at ages 10,12,14,16) — so they die age 18
right when death surge hits. Can't replant dead tiles in time.

FIX: dig at age 16 (right after the last yield). This moves 16 tile-deaths
from d18-d21 (overloaded) to d16-D17 (when death surge hasn't peaked),
giving 10+ days to replant before d29. We lose 0 yield (age 16 is
the last harvestable age anyway).

Math check: with dig@16, deaths spread over d16-d19 = ~7/day instead of
~12/day at d18. Now death surge fits comfortably in the action budget.
"""
import re

src = open("bots/v63c.py", encoding="utf-8").read()  # Use v63c as base (proven 34 straw)

# 1. Strawberry dig age: 18 -> 16
src = src.replace(
    '                    elif age >= 18:',
    '                    elif age >= 16:  # ITER44 D+0.5: pre-death-surge, after last yield (age 16)'
)

# 2. Straw target: 34 -> 26 (more sustainable with early dig)
src = src.replace(
    'counts.get("STRAWBERRY", 0) < 34:',
    'counts.get("STRAWBERRY", 0) < 26:'
)
src = src.replace(
    'straw_count < 24:',
    'straw_count < 26:'
)

# 3. Docstring
src = src.replace(
    '"""Kaggriculture v63c: melon wave -> cash d11 -> 13 hands -> straw 34 (vedant timing).',
    '"""Kaggriculture v66: dig@16 + target 26 straw (death surge spread).'
)

open("bots/v66.py", "w", encoding="utf-8").write(src)
print("v66.py created")
