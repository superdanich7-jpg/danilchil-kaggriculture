"""Create v61: iter42 base + melon planting cutoff 18 -> 13.

All fresh losers (Santiago 37.9k, Duc 108k, Phu 79k) drop melon after the
first harvest: melon=0 from d12, full field under strawberry (18-37 tiles).
We keep replanting melon to d18 - those tiles+labor yield 50-130/tile while
strawberry yields 220-300/tile with the same service cost.

v61: stop planting melon after day 13; freed tiles go to strawberry engine
(replant already unblocked by iter42).
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# melon planting cutoff: day < 18 -> day < 13
src = src.replace(
    '    if m > 0 and counts.get("MELON", 0) < melon_quota and day < 18:',
    '    if m > 0 and counts.get("MELON", 0) < melon_quota and day < 13:'
)

# Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v61: iter42 + melon cutoff d13 (straw takes over).'
)

open("bots/v61.py", "w", encoding="utf-8").write(src)
print("v61.py created")
