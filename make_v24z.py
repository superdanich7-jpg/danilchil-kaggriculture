"""Create v24z: v24x but max_hands_today=12 (match top-player labor)."""
with open("bots/v24x.py", encoding="utf-8") as f:
    a = f.read()

old = "        max_hands_today = 10 if day >= 11 else 8\n"
new = "        max_hands_today = 12 if day >= 11 else 8\n"

if old in a:
    a = a.replace(old, new, 1)
    print("max_hands 10->12")
else:
    print("max_hands line NOT found")

with open("bots/v24z.py", "w", encoding="utf-8") as f:
    f.write(a)

import ast
try:
    ast.parse(a)
    print("v24z syntax OK")
except SyntaxError as e:
    print(f"v24z syntax ERROR: {e}")