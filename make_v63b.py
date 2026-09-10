"""Create v63b: v63 + staged hiring (8 hands early, 13 after melon sale).

vedant hires up AFTER the melon cash lands (d12): 5->6->8 hands early,
13 from d12. Our v63 hired 13 from d1 - salaries (609/day) ate the seed
budget and created the cash gap (58 coins on d15).

v63b: max_hands = 8 if day < 12 else 13.
"""
import re

src = open("bots/v63.py", encoding="utf-8").read()

# staged hiring (v63 already has max_hands 13)
src = src.replace(
    'max_hands_today = 13 if herd >= 5 else MAX_HANDS',
    'max_hands_today = (8 if day < 12 else 13) if herd >= 5 else MAX_HANDS'
)

# Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v63b: melon wave 20, hands 8->13 at d12, straw peak 34.'
)

open("bots/v63b.py", "w", encoding="utf-8").write(src)
print("v63b.py created")

