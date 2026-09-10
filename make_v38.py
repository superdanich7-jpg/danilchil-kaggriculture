"""Create v38: zones + straw target 28 + herd 12.

v37 (26 straw) was stable but lost on peak income. v38 increases to 28
for more peak production while zones maintain stability.
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Add _assign_zone function
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

# 2. Replace hand assignment with zone-based
src = src.replace(
    '            actions[i] = _assign_nearest(u, pool, assigned) or ["PASS"]',
    '''            # ITER38 P2: zone assignment for crop hands
            if i > n_anim_hands:
                half = len(tiles) // 2
                zones = [q for q in ("NW", "NE", "SW", "SE") if q in quads] or ["NW"]
                k_crop = i - n_anim_hands - 1
                zone = zones[k_crop % len(zones)]
                actions[i] = _assign_zone(u, pool, assigned, zone, half) or ["PASS"]
            else:
                actions[i] = _assign_nearest(u, pool, assigned) or ["PASS"]'''
)

# 3. Straw planting limit: 28 tiles
src = src.replace(
    '    if s > 0 and allow_straw and day <= 19:',
    '    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 28:'
)

# 4. Straw seed buying: limit to 28 tiles
src = src.replace(
    '''            if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 12:
                n_straw = min(6, int((money - FEED_RESERVE) // 100))
                if n_straw >= 1:
                    market.append(["BUY_SEED", "STRAWBERRY", n_straw])''',
    '''            # ITER38: straw target 28 tiles.
            straw_count = sum(1 for row in tiles for t in row
                              if isinstance(t, dict) and t.get("kind") == "PLANT"
                              and t.get("crop") == "STRAWBERRY")
            if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 12 \\
                    and straw_count < 28:
                n_straw = min(6, int((money - FEED_RESERVE) // 100))
                if n_straw >= 1:
                    market.append(["BUY_SEED", "STRAWBERRY", n_straw])'''
)

# 5. Docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v38: zones + straw target 28 + herd 12.'
)

open("bots/v38.py", "w", encoding="utf-8").write(src)
print("v38.py created")
