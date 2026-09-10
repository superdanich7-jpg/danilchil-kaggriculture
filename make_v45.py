"""Create v45: iter35 + zones + straw limit 18 + herd_cap 16.

Combine the best ideas:
- iter35 base (max_hands 7, proven 556.0)
- Zones (P2) for hand efficiency
- Straw limit 18 (prevent over-planting crash)
- herd_cap 16 (more animals = more stable income)
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Revert max_hands from 12 (iter39) to 7 (iter35)
src = src.replace(
    'max_hands_today = 12 if herd >= 5 else MAX_HANDS',
    'max_hands_today = 7 if herd >= 5 else MAX_HANDS'
)

# 2. Increase herd_cap from 12 to 16
src = src.replace(
    'herd_cap = 8 if melon_mode else 12',
    'herd_cap = 12 if melon_mode else 16'
)

# 3. Add _assign_zone function
assign_zone_func = '''

def _assign_zone(u, pool, assigned, zone, half):
    """P2: unit serves its own quadrant first."""
    if zone == "NW":
        x_range, y_range = range(0, half), range(0, half)
    elif zone == "NE":
        x_range, y_range = range(half, half * 2), range(0, half)
    elif zone == "SW":
        x_range, y_range = range(0, half), range(half, half * 2)
    elif zone == "SE":
        x_range, y_range = range(half, half * 2), range(half, half * 2)
    else:
        x_range, y_range = range(0, half * 2), range(0, half * 2)

    def _do_task(pos, tk):
        verb, x, y, arg = tk
        if tuple(pos) == (x, y):
            if verb == "PLANT":
                return ["PLANT", arg]
            return [verb]
        return _step(pos, (x, y)) or ["PASS"]

    # Emergency (unwatered plants) in zone
    best = None
    bd = 1 << 30
    for tk in pool:
        if tk[0] != "WATER":
            continue
        x, y = tk[1], tk[2]
        if (x, y) in assigned:
            continue
        if x not in x_range or y not in y_range:
            continue
        d = abs(u[0] - x) + abs(u[1] - y)
        if d < bd:
            bd = d
            best = tk
    if best:
        assigned.add((best[1], best[2]))
        return _do_task(u, best)

    # Any task in zone (nearest)
    best = None
    bd = 1 << 30
    for tk in pool:
        x, y = tk[1], tk[2]
        if (x, y) in assigned:
            continue
        if x not in x_range or y not in y_range:
            continue
        d = abs(u[0] - x) + abs(u[1] - y)
        if d < bd:
            bd = d
            best = tk
    if best:
        assigned.add((best[1], best[2]))
        return _do_task(u, best)

    # Fallback: nearest anywhere
    return _assign_nearest(u, pool, assigned)

'''

src = src.replace(
    'def _assign_nearest(pos, tasks, assigned):',
    assign_zone_func + 'def _assign_nearest(pos, tasks, assigned):'
)

# 4. Replace hand assignment with zone-based
src = src.replace(
    '            actions[i] = _assign_nearest(u, pool, assigned) or ["PASS"]',
    '''            # ITER45 P2: zone assignment for crop hands
            if i > n_anim_hands:
                half = len(tiles) // 2
                zones = [q for q in ("NW", "NE", "SW", "SE") if q in quads] or ["NW"]
                k_crop = i - n_anim_hands - 1
                zone = zones[k_crop % len(zones)]
                actions[i] = _assign_zone(u, pool, assigned, zone, half) or ["PASS"]
            else:
                actions[i] = _assign_nearest(u, pool, assigned) or ["PASS"]'''
)

# 5. Straw planting limit: 18 tiles
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 18:'
)

# 6. Docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v45: iter35 + zones + straw limit 18 + herd_cap 16.'
)

open("bots/v45.py", "w", encoding="utf-8").write(src)
print("v45.py created")
