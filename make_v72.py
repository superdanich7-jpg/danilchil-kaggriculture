"""Create v72: FULL continuous strawberry replant (no limits).

FINAL DIAGNOSIS: The "dead replant loop" is caused by ANY limit on
strawberry replanting. v70/v71 tried various limits (day cutoff, tile count)
but they ALL block replant after death surge.

vedant's secret: strawberry = 34 tiles CONSTANTLY d12-d24. Not 34->7.
The difference is that EVERY DIG'd tile gets replanted SAME DAY.

v72: ZERO limits on strawberry planting. Buy seeds every day d4-d29,
plant on every free tile d4-d29, no tile count ceiling. If we have
seeds + free tiles + hands, we plant. Continuous replant = stable field.

This will look "unbalanced" offline (straw might hit 45+ tiles) but that's
exactly what vedant does — his straw peaks at 34-37 then gradually declines.
The key is STABILITY through death surge, not peak count.
"""
import re

src = open("bots/v70.py", encoding="utf-8").read()  # v70 = herd 9 + zones + stepwise hire

# 1. Remove strawberry planting day cutoff entirely (was day <= 26)
src = src.replace(
    'if s > 0 and allow_straw and day <= 26 and counts.get("STRAWBERRY", 0) < 30:  # ITER51: continuous replant',
    'if s > 0 and allow_straw and day <= 28:  # ITER52: NO day cutoff, replant through endgame'
)

# 2. Remove strawberry planting tile count limit entirely (was < 30)
src = src.replace(
    'if s > 0 and allow_straw and day <= 28:  # ITER52: NO day cutoff, replant through endgame',
    'if s > 0 and allow_straw and day <= 28:  # ITER52: NO tile count ceiling'
)

# 3. Strawberry seed buying: no day cutoff, no tile count limit
src = src.replace(
    'if day >= 4 and day <= 26 and seeds.get("STRAWBERRY", 0) < 100:',
    'if day >= 4 and day <= 28 and seeds.get("STRAWBERRY", 0) < 500:'
)

# 4. Increase seed purchase amount
src = src.replace(
    'n_straw = min(8, int((money - FEED_RESERVE) // 100))',
    'n_straw = min(10, int((money - FEED_RESERVE) // 100))  # ITER52: buy aggressively for continuous replant'
)

# 5. Docstring
src = src.replace(
    '"""Kaggriculture v71: v70 + continuous straw replant (no d21 cutoff).',
    '"""Kaggriculture v72: v70 + FULL continuous straw replant (no limits).'
)

open("bots/v72.py", "w", encoding="utf-8").write(src)
print("v72.py created")
