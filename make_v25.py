"""Create v25: v23_h10 but more strawberry seed stock (target 20, keep window d4-d19)."""
with open("bots/v23_h10.py", encoding="utf-8") as f:
    a = f.read()

old = (
    "            if day >= 4 and day <= 19 and seeds.get(\"STRAWBERRY\", 0) < 12:\n"
    "                # keep a 600 coin floor: pre-income (d4-11) there is no harvest\n"
    "                # money yet - overbuying seeds here starves animal feed\n"
    "                n_straw = min(5, int((money - 600) // 100))\n"
)
new = (
    "            if day >= 4 and day <= 19 and seeds.get(\"STRAWBERRY\", 0) < 20:\n"
    "                # ITER36 P1: raise seed target so d13-d19 replants never stall;\n"
    "                # window stays d19 - later planting never matures and the extra\n"
    "                # immature tiles turn into weeds (v24 lesson: d25 window hurt)\n"
    "                n_straw = min(6, int((money - 600) // 100))\n"
)

if old in a:
    a = a.replace(old, new, 1)
    print("seed target 12->20")
else:
    print("seed block NOT found")

with open("bots/v25.py", "w", encoding="utf-8") as f:
    f.write(a)

import ast
try:
    ast.parse(a)
    print("v25 syntax OK")
except SyntaxError as e:
    print(f"v25 syntax ERROR: {e}")