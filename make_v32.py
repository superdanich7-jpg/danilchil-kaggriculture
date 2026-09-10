"""Create v32: iter38 + increase weed DIG cap from 5 to 15/day.
Root cause: 40+ straw tiles all reach age 16 in d20-d30, creating 10-20 weeds/day.
DIG cap of 5/day can't keep up -> weeds pile up -> no space for replanting ->
field collapses (straw 43->2 by d29 in the Shel Horta replay)."""
with open("champ/main.py", encoding="utf-8") as f:
    a = f.read()

old = "                if digs < 5:  # ITER34 P0: cap weed clearing per day\n"
new = (
    "                if digs < 15:  # ITER39: 40+ straw tiles dying d20-d30 create\n"
    "                    # 10-20 weeds/day; cap 5 left weeds piled up blocking\n"
    "                    # replanting (straw 43->2 collapse in Shel Horta replay)\n"
)

if old in a:
    a = a.replace(old, new, 1)
    print("DIG cap 5->15")
else:
    print("DIG cap line NOT found")
    for i, l in enumerate(a.split("\n")):
        if "digs <" in l:
            print(f"  line {i+1}: {l}")

with open("bots/v32.py", "w", encoding="utf-8") as f:
    f.write(a)

import ast
try:
    ast.parse(a)
    print("v32 syntax OK")
except SyntaxError as e:
    print(f"v32 syntax ERROR: {e}")