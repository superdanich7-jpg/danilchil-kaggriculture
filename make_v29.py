"""Create v29: champ(iter36) + max_hands_today 9."""
with open("champ/main.py", encoding="utf-8") as f:
    a = f.read()

old = "        max_hands_today = 7 if herd >= 5 else MAX_HANDS\n"
new = "        max_hands_today = 9 if herd >= 5 else MAX_HANDS\n"

if old in a:
    a = a.replace(old, new, 1)
    print("max_hands 7->9")
else:
    print("max_hands line NOT found")

with open("bots/v29.py", "w", encoding="utf-8") as f:
    f.write(a)

import ast
try:
    ast.parse(a)
    print("v29 syntax OK")
except SyntaxError as e:
    print(f"v29 syntax ERROR: {e}")