"""Create v57: hire10 + straw limit as PEAK 20 (replant never blocked).

Architectural bug found: straw limit 12 blocks replant after DIG - tiles
freed by dead strawberries stay EMPTY because _pick_crop refuses to plant.
kirito83 keeps 33 tiles alive d12-d23 by replanting in waves (sold 400
strawberries vs our 33!).

v57: limit 20 = cap on peak size, but continuous replant keeps 12-18 alive.
Plus hire10 to service the larger field.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. max_hands: 7 -> 10
src = src.replace(
    'max_hands_today = 7 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 10 if herd >= 5 else MAX_HANDS'
)

# 2. straw limit: 12 -> 20 (peak cap, replant allowed)
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 12:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 20:'
)

# 3. Straw seeds: buy more to feed the replant cycle (inventory cap 12 -> 16)
src = src.replace(
    'if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 12:',
    'if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 16:'
)

# 4. Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v57: hire10 + straw peak 20 (replant unblocked).'
)

open("bots/v57.py", "w", encoding="utf-8").write(src)
print("v57.py created")
