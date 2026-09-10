"""Create v55: iter36 base (dig@16, best confirmed LB 533.8) + safe kirito83 picks.

Conservative changes for 7 hands (kirito83 needs 12, we can't afford that):
1. wheat_quota 6 -> 10 (reduce wheat purchase leak ~100/day, self-feed most)
2. FERT reserve 8 -> 2 (sell more fertilizer: kirito83 sells 390 vs our 178)
3. Straw unlimited (iter36 behavior - no limit)
4. dig@16 kept from iter36
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# Base = iter36: revert max_hands if changed (ensure 7) and remove straw limit
src = src.replace(
    'max_hands_today = 7 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 7 if herd >= 5 else MAX_HANDS'
)
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 12:',
    '    if s > 0 and allow_straw and day <= 19:'
)

# dig@16 (iter36 signature)
src = src.replace(
    '                    elif age >= 18:\n                        tasks.append(("DIG", x, y, None))',
    '                    elif age >= 16:\n                        tasks.append(("DIG", x, y, None))'
)

# 1. wheat_quota: 6 -> 10
src = src.replace(
    'wheat_quota = 4 if melon_mode else 6',
    'wheat_quota = 6 if melon_mode else 10'
)

# 2. FERT reserve 8 -> 2
src = src.replace(
    '        fert_res = 0 if (day < 10 or melon_mode or day >= 27) else FERT_RESERVE',
    '        fert_res = 0 if (day < 10 or melon_mode or day >= 27) else 2'
)

# 3. Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v55: iter36 + safe kirito83 picks (wheat10 fert2).'
)

open("bots/v55.py", "w", encoding="utf-8").write(src)
print("v55.py created")
