"""Create v60: iter42 base + wheat_quota 6 -> 14 (wheat income engine).

Fresh iter42 losses forensics (sells totals per game):
- Duc Hai Ha (108k): WHEAT 590 (32k coins!), strawberry 146
- Phu Nhan (79k): 23-45 wheat tiles on field
- Us: wheat sells 116-257 (avg ~200) - 3x less than Duc

Wheat price barely falls (log impact 0.2): volume income ~55/tile/harvest.
Wheat also self-feeds the herd. Base is iter42 (hire10, peak20, compact).
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# wheat_quota: 6 -> 14
src = src.replace(
    'wheat_quota = 4 if melon_mode else 6',
    'wheat_quota = 8 if melon_mode else 14'
)

# Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v60: iter42 + wheat quota 14 (wheat income engine).'
)

open("bots/v60.py", "w", encoding="utf-8").write(src)
print("v60.py created")
