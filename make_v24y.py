"""Create v24y: v23_h10 but n_anim_hands=3 for herd>9 (isolate the variable)."""
with open("bots/v23_h10.py", encoding="utf-8") as f:
    a = f.read()

old = (
    '            n_anim_hands = 4  # ITER35: was 5 - 17-18 animals starved the crop\n'
    '            # engine of labor (3 crop units for ~50 tasks = ~1 planting/day)\n'
)
new = (
    '            n_anim_hands = 3  # ITER36 test: 3 hands for herd>9\n'
    '            # engine of labor comparo vs base h10\n'
)

if old in a:
    a = a.replace(old, new, 1)
    print("replaced n_anim_hands block")
else:
    print("n_anim_hands block NOT found")

with open("bots/v24y.py", "w", encoding="utf-8") as f:
    f.write(a)

import ast
try:
    ast.parse(a)
    print("v24y syntax OK")
except SyntaxError as e:
    print(f"v24y syntax ERROR: {e}")