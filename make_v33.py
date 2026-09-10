"""Create v33: clean iter35 base (v22) + hire 12 hands. No other changes."""
with open("bots/v22.py", encoding="utf-8") as f:
    a = f.read()

old = "        max_hands_today = 7 if herd >= 5 else MAX_HANDS\n"
new = "        max_hands_today = 12 if herd >= 5 else MAX_HANDS\n"

if old in a:
    a = a.replace(old, new, 1)
    print("max_hands 7->12")
else:
    print("max_hands line NOT found")

with open("bots/v33.py", "w", encoding="utf-8") as f:
    f.write(a)

import ast
try:
    ast.parse(a)
    print("v33 syntax OK")
except SyntaxError as e:
    print(f"v33 syntax ERROR: {e}")