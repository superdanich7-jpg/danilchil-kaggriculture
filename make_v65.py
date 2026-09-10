"""Create v65: herd 9 + straw target 28 (compromise).

v64 crashes because 34 straw tiles die in d18-d24 death surge (10 crop hands
can't water 34 tiles + handle harvest). vedant survives because his
hand ASSIGNMENT is better (zones + dedicated waterers).

v65: keep herd 9 (frees crop hands) but reduce straw target 34 -> 28.
This matches the math: 10 crop hands can sustain 28 tiles through death surge
(28 dead tiles / 4 days = 7 death-actions/day, + 7 waterings = 14 actions < 40 available).
"""
import re

src = open("bots/v64.py", encoding="utf-8").read()

# 1. straw peak: 34 -> 28
src = src.replace(
    'counts.get("STRAWBERRY", 0) < 34:',
    'counts.get("STRAWBERRY", 0) < 28:'
)

# 2. Docstring
src = src.replace(
    '"""Kaggriculture v64: herd 9 + 13 hands + 34 straw (vedant exact profile).',
    '"""Kaggriculture v65: herd 9 + straw target 28 (sustainable death surge).'
)

open("bots/v65.py", "w", encoding="utf-8").write(src)
print("v65.py created")
