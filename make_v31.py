"""Create v31: iter35 (v22) + hire 10 + unlimited strawberry replant window.
Changes:
1. max_hands_today = 10 (was 7) - match top opponents' 8-12 hands
2. _pick_crop strawberry: day <= 19 -> day <= 29 (replant dying tiles)
3. Seed buying: window d4-d22 (was d4-d19), cap < 20 (was < 12), batch 8 (was 6)
NO dig@16 (that was the iter36 regression - lost the 4th strawberry yield)."""
with open("bots/v22.py", encoding="utf-8") as f:
    a = f.read()

# 1) hire 10
old1 = "        max_hands_today = 7 if herd >= 5 else MAX_HANDS\n"
new1 = "        max_hands_today = 10 if herd >= 5 else MAX_HANDS\n"
assert old1 in a, "max_hands line not found"
a = a.replace(old1, new1, 1)

# 2) remove day limit for strawberry planting
old2 = "    if s > 0 and allow_straw and day <= 19:\n"
new2 = (
    "    # ITER38: remove day limit - dying straw tiles (age 16-18) must be\n"
    "    # replanted immediately, otherwise the field collapses to 0-2 tiles\n"
    "    # by d29 while winners maintain 67-75 via continuous replanting\n"
    "    if s > 0 and allow_straw and day <= 29:\n"
)
assert old2 in a, "_pick_crop day limit not found"
a = a.replace(old2, new2, 1)

# 3) extend seed buying window and cap
old3 = (
    "            if day >= 4 and day <= 19 and seeds.get(\"STRAWBERRY\", 0) < 12:\n"
    "                n_straw = min(6, int((money - FEED_RESERVE) // 100))\n"
)
new3 = (
    "            if day >= 4 and day <= 22 and seeds.get(\"STRAWBERRY\", 0) < 20:\n"
    "                n_straw = min(8, int((money - FEED_RESERVE) // 100))\n"
)
assert old3 in a, "seed buying block not found"
a = a.replace(old3, new3, 1)

with open("bots/v31.py", "w", encoding="utf-8") as f:
    f.write(a)

import ast
try:
    ast.parse(a)
    print("v31 syntax OK")
except SyntaxError as e:
    print(f"v31 syntax ERROR: {e}")
print("Changes applied: hire10 + replant window d29 + seeds d22/cap20/batch8")