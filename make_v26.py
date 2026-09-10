"""Create v26: current champ/main.py + DIG@16 for strawberry (minimal change)."""
with open("champ/main.py", encoding="utf-8") as f:
    a = f.read()

old = "                    elif age >= 18:\n                        tasks.append((\"DIG\", x, y, None))\n"
new = "                    elif age >= 16:\n                        # ITER36: dig strawberry at age 16, right after the 4th\n                        # harvest. max_lifespan ends on day P+17 - by 18 the\n                        # spent tile has already been a weed for a full day.\n                        tasks.append((\"DIG\", x, y, None))\n"

if old in a:
    a = a.replace(old, new, 1)
    print("DIG age 18->16 applied")
else:
    print("DIG block NOT found")
    for i, l in enumerate(a.split("\n")):
        if "age >= 18" in l:
            print(f"  line {i+1}: {repr(l)}")

with open("bots/v26.py", "w", encoding="utf-8") as f:
    f.write(a)

import ast
try:
    ast.parse(a)
    print("v26 syntax OK")
except SyntaxError as e:
    print(f"v26 syntax ERROR: {e}")