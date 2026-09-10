"""Create v24x: v24 but n_anim_hands back to 4 for herd>9."""
with open("bots/v24.py", encoding="utf-8") as f:
    a = f.read()

old = (
    '            n_anim_hands = 3  # ITER35: was 5 - 17-18 animals starved the\n'
    '            # engine of labor. ITER36: kept 3 - 4 crop workers couldn\'t\n'
    "            # water 30+ strawberry tiles (33 weeds in offline test)\n"
)
new = (
    '            n_anim_hands = 4  # ITER35 base: enough labor for 12-14 herd\n'
    '            # engine of labor. ITER36: keeping 4 - animals>crops in herd\n'
)

if old in a:
    a = a.replace(old, new, 1)
    print("replaced n_anim_hands block")
else:
    print("n_anim_hands block NOT found, searching...")
    for i, l in enumerate(a.split("\n")):
        if "n_anim_hands" in l and i > 360:
            print(f"  line {i+1}: {repr(l)}")

with open("bots/v24x.py", "w", encoding="utf-8") as f:
    f.write(a)

import ast
try:
    ast.parse(a)
    print("v24x syntax OK")
except SyntaxError as e:
    print(f"v24x syntax ERROR: {e}")