"""Create v56: iter41 base (straw limit 12) + max_hands 7 -> 10.

Untested combination: v30 (hire10) beat champ offline wr=0.87, dCoins=+3715,
but that test was on iter35 base with unlimited straw (field too big for 10
hands to handle). With straw limit 12 the field is compact - 10 hands can
actually service it. iter37/iter39 (hire10/12 on unlimited straw) failed
because unlimited straw overwhelmed extra hands.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. max_hands: 7 -> 10
src = src.replace(
    'max_hands_today = 7 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 10 if herd >= 5 else MAX_HANDS'
)

# 2. Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v56: iter41 + hire10 (compact field + more hands).'
)

open("bots/v56.py", "w", encoding="utf-8").write(src)
print("v56.py created")
