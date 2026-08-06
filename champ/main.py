"""Kaggriculture v5: carrot loop with farm hands + land expansion v2."""

CROPS = {
    "CARROT": {"seed": 20, "first_yield_day": 2, "max_yield_day": 3, "max_yield": 4},
}

MAX_HANDS_BASE = 4
MAX_HANDS_EXPANDED = 6
MIN_MONEY_FOR_HIRE = 500
MIN_MONEY_FOR_LAND = 3000
LAND_DAY_MIN = 8
LAND_DAY_MAX = 20

def _farm(o): return o["farms"][o["player"]]
def _priv(o): return o.get("private", {}) or {}
def _dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
def _step(p, t):
    if p[0] < t[0]: return ["EAST"]
    if p[0] > t[0]: return ["WEST"]
    if p[1] < t[1]: return ["SOUTH"]
    if p[1] > t[1]: return ["NORTH"]
    return None

def _shed_adjacent(pos, board_size=10):
    half = board_size // 2
    access = [(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)]
    return tuple(pos) in access

def _nearest_shed(pos, board_size=10):
    half = board_size // 2
    access = [(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)]
    return min(access, key=lambda p: _dist(pos, p))

def _find_nearest(f, pos, condition):
    best = None
    best_dist = float('inf')
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if condition(t):
                d = _dist(pos, (x, y))
                if d < best_dist:
                    best_dist = d
                    best = (x, y)
    return best

def _collect_tasks(f, day, seeds):
    """Collect tasks: (type, x, y). Priority: WATER > HARVEST > PLANT."""
    tasks = []
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("kind") == "PLANT" and t["crop"] == "CARROT":
                age = day - t["planted_day"]
                if age >= CROPS["CARROT"]["max_yield_day"]:
                    tasks.append(("HARVEST", x, y))
                elif not t.get("watered_today"):
                    tasks.append(("WATER", x, y))
            elif t is None and seeds.get("CARROT", 0) > 0:
                tasks.append(("PLANT", x, y))
    return tasks

def agent(obs):
    try:
        f = _farm(obs)
        priv = _priv(obs)
        pos = tuple(f["farmer"])
        tile = f["tiles"][pos[1]][pos[0]]
        day = obs["day"]
        hour = obs.get("hour", 0)
        seeds = priv.get("seeds", {}) or {}
        shed = priv.get("shed", {}) or {}
        invs = priv.get("inventories") or [{}]
        inv0 = invs[0] if invs else {}

        board_size = len(f["tiles"])
        shed_adj = _shed_adjacent(pos, board_size)

        # Determine max hands based on unlocked quadrants
        n_unlocked = len(f.get("unlocked_quadrants", []))
        max_hands = MAX_HANDS_EXPANDED if n_unlocked > 1 else MAX_HANDS_BASE

        # === MARKET ORDERS ===
        market = []

        # Sell all carrots
        if shed.get("CARROT", 0) > 0:
            market.append(["SELL", "CARROT", shed["CARROT"]])

        # Buy carrot seeds to maintain stock >= 2
        if seeds.get("CARROT", 0) < 2 and f["money"] >= CROPS["CARROT"]["seed"]:
            market.append(["BUY_SEED", "CARROT", 2 - seeds.get("CARROT", 0)])

        # Hire hands at start of day
        if hour == 0 and f.get("hires_today", 0) < max_hands and f["money"] > MIN_MONEY_FOR_HIRE:
            market.append(["HIRE"])

        # Buy land: only when money > 3000 and day in [8, 20]
        n_extra = n_unlocked - 1  # NW always there
        if LAND_DAY_MIN <= day <= LAND_DAY_MAX and n_extra < 3 and f["money"] > MIN_MONEY_FOR_LAND:
            market.append(["BUY_LAND"])

        # === COORDINATION ===
        # Units: [main farmer] + [hands]
        units = [tuple(f["farmer"])] + [tuple(h) for h in f.get("hands", [])]
        n_units = len(units)

        # Collect tasks
        tasks = _collect_tasks(f, day, seeds)
        # Sort by priority: WATER(0) > HARVEST(1) > PLANT(2)
        prio = {"WATER": 0, "HARVEST": 1, "PLANT": 2}
        tasks.sort(key=lambda t: (prio[t[0]], _dist(units[0], (t[1], t[2]))))

        assigned = set()
        actions = [["PASS"] for _ in range(n_units)]

        for i, u_pos in enumerate(units):
            u_inv = invs[i] if i < len(invs) else {}

            # HIGH PRIORITY: unit with inventory -> go to shed and DROP
            if u_inv:
                if _shed_adjacent(u_pos, board_size):
                    actions[i] = ["DROP"]
                else:
                    actions[i] = _step(u_pos, _nearest_shed(u_pos, board_size)) or ["PASS"]
                continue

            # Find nearest unassigned task
            best_task = None
            best_dist = float('inf')
            for task in tasks:
                t_type, tx, ty = task
                if (tx, ty) in assigned:
                    continue
                d = _dist(u_pos, (tx, ty))
                if d < best_dist:
                    best_dist = d
                    best_task = task

            if best_task:
                t_type, tx, ty = best_task
                assigned.add((tx, ty))
                if u_pos == (tx, ty):
                    if t_type == "WATER":
                        actions[i] = ["WATER"]
                    elif t_type == "HARVEST":
                        actions[i] = ["HARVEST"]
                    elif t_type == "PLANT":
                        actions[i] = ["PLANT", "CARROT"]
                else:
                    actions[i] = _step(u_pos, (tx, ty)) or ["PASS"]
            else:
                # No tasks left - idle
                actions[i] = ["PASS"]

        return {
            "farmer": actions[0],
            "hands": actions[1:],
            "market": market,
        }

    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}