"""Create v27: v26 + watering urgency priority (champ-only, no hire changes)."""
with open("bots/v26.py", encoding="utf-8") as f:
    a = f.read()

# 1) mark WATER tasks with urgency flag in the crop pool
old_water = 'tasks.append(("WATER", x, y, None))'
new_water = (
    'tasks.append(("WATER", x, y,\n'
    '                               1 if t.get("consecutive_unwatered", 0) >= 1 else 0))'
)
if old_water in a:
    a = a.replace(old_water, new_water)
    print("WATER tasks marked with urgency (x3)")
else:
    print("WATER task block NOT found")

# 2) prioritize urgent tasks in _assign_nearest
old_assign = """def _assign_nearest(pos, tasks, assigned):
    best = None
    bd = 1 << 30
    for tk in tasks:
        key = (tk[1], tk[2])
        if key in assigned:
            continue
        d = _dist(pos, key)
        if d < bd:
            bd = d
            best = tk"""
new_assign = """def _assign_nearest(pos, tasks, assigned):
    best = None
    bd = 1 << 30
    urg = 0
    for tk in tasks:
        key = (tk[1], tk[2])
        if key in assigned:
            continue
        d = _dist(pos, key)
        u = 1 if tk[3] == 1 else 0
        if u > urg or (u == urg and d < bd):
            urg = u
            bd = d
            best = tk"""

if old_assign in a:
    a = a.replace(old_assign, new_assign, 1)
    print("_assign_nearest now urgency-aware")
else:
    print("_assign_nearest block NOT found")

with open("bots/v27.py", "w", encoding="utf-8") as f:
    f.write(a)

import ast
try:
    ast.parse(a)
    print("v27 syntax OK")
except SyntaxError as e:
    print(f"v27 syntax ERROR: {e}")