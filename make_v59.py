"""Create v59a/v59b: moderate hand/peak combos.
v59a: hire11 + peak 20
v59b: hire11 + peak 22
"""
import re
import sys

src = open("champ/main.py", encoding="utf-8").read()

variant = sys.argv[1] if len(sys.argv) > 1 else "v59a"
hands = 11
peak = 20 if variant == "v59a" else 22

out = src.replace(
    'max_hands_today = 10 if herd >= 5 else MAX_HANDS',
    f'max_hands_today = {hands} if herd >= 5 else MAX_HANDS'
)
out = out.replace(
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 20:',
    f'    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < {peak}:'
)
out = out.replace(
    'if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 16:',
    f'if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < {peak + 2}:'
)
out = out.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    f'"""Kaggriculture {variant}: hire{hands} + straw peak {peak}.'
)

open(f"bots/{variant}.py", "w", encoding="utf-8").write(out)
print(f"{variant}.py created (hands={hands}, peak={peak})")
