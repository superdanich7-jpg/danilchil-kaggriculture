"""Create v28: current champ (iter36) + max_hands_today 8 vs 7."""
with open("champ/main.py", encoding="utf-8") as f:
    a = f.read()

old = "        max_hands_today = 7 if herd >= 5 else MAX_HANDS\n"
new = "        max_hands_today = 8 if herd >= 5 else MAX_HANDS\n"

if old in a:
    a = a.replace(old, new, 1)
    print("max_hands 7->8")
else:
    print("max_hands line NOT found")
    for i, l in enumerate(a.split("\n")):
        if "max_hands" in l:
            print(f"  line {i+1}: {l}")

with open("bots/v28.py", "w", encoding="utf-8") as f:
    f.write(a)

import ast
try:
    ast.parse(a)
    print("v28 syntax OK")
except SyntaxError as e:
    print(f"v28 syntax ERROR: {e}")