"""Create v70: v69 + zones for crop hands.

v69 (herd 9, target 24) beats champ offline wr=0.47 but not consistently.
Need zones to reduce walking (40%→16% transit) so 10 crop hands can
maintain 34 straw tiles like vedant.

This combines:
- P0 fix (DIG, already in champ)
- P1 fix (continuous replant, already in champ)  
- P2 fix (ZONES — NEW, the missing piece)
- iter44 fix (stepwise hiring)
- iter48 fix (straw target 30)
"""
import re

src = open("bots/v69.py", encoding="utf-8").read()

# 1. Add _assign_zone function with quadrant-based assignment
zone_func = '''

def _zone_of(x, y, half):
    """Map tile to quadrant: NW/NE/SW/SE"""
    if x < half and y < half:
        return "NW"
    elif x >= half and y < half:
        return "NE"
    elif x < half and y >= half:
        return "SW"
    else:
        return "SE"

def _assign_zone(u, pool, assigned, zone, half):
    """P2: unit serves its own quadrant first; emergency watering overrides."""
    def _do_task(pos, tk):
        verb, x, y, arg = tk
        if tuple(pos) == (x, y):
            if verb == "PLANT":
                return ["PLANT", arg]
            return [verb]
        return _step(pos, (x, y)) or ["PASS"]

    # Emergency: unwatered plants in zone that die tonight
    best = None
    bd = 1 << 30
    for tk in pool:
        if tk[0] != "WATER":
            continue
        x, y = tk[1], tk[2]
        if (x, y) in assigned:
            continue
        z = _zone_of(x, y, half)
        if z != zone:
            continue
        d = abs(u[0] - x) + abs(u[1] - y)
        if d < bd:
            bd = d
            best = tk
    if best:
        assigned.add((best[1], best[2]))
        return _do_task(u, best)

    # Any task in zone (nearest first)
    best = None
    bd = 1 << 30
    for tk in pool:
        x, y = tk[1], tk[2]
        if (x, y) in assigned:
            continue
        z = _zone_of(x, y, half)
        if z != zone:
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

# Insert after _assign_nearest
src = src.replace(
    'def _assign_nearest(pos, tasks, assigned):',
    zone_func + 'def _assign_nearest(pos, tasks, assigned):'
)

# 2. Replace hand assignment with zone-based
src = src.replace(
    '            actions[i] = _assign_nearest(u, pool, assigned) or ["PASS"]',
    '''            # ITER50 P2: zone assignment reduces walking by ~70%
            if i > n_anim_hands:
                half = len(tiles) // 2
                zones_list = [q for q in ("NW", "NE", "SW", "SE") if q in quads] or ["NW"]
                k_crop = i - n_anim_hands - 1
                zone = zones_list[k_crop % len(zones_list)]
                actions[i] = _assign_zone(u, pool, assigned, zone, half) or ["PASS"]
            else:
                actions[i] = _assign_nearest(u, pool, assigned) or ["PASS"]'''
)

# 3. Restore straw target to 30 (zones make it sustainable)
src = src.replace(
    'counts.get("STRAWBERRY", 0) < 24:  # ITER49: 24 tiles sustainable with 10 crop hands',
    'counts.get("STRAWBERRY", 0) < 30:  # ITER50: 30 tiles with zones, herd 9'
)
src = src.replace(
    'if day >= 4 and day <= 21 and seeds.get("STRAWBERRY", 0) < 48:',
    'if day >= 4 and day <= 21 and seeds.get("STRAWBERRY", 0) < 60:'
)

# 4. Docstring
src = src.replace(
    '"""Kaggriculture v69: herd 9 + straw 24 (death-surge sustainable).',
    '"""Kaggriculture v70: herd 9 + straw 30 + ZONES + stepwise hire 13.'
)

open("bots/v70.py", "w", encoding="utf-8").write(src)
print("v70.py created")
