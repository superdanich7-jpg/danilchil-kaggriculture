"""Kaggriculture v5: carrot loop with farm hands + batch DROP."""

CROPS = {
    "MELON": {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "max_yield": 6},
}

MAX_HANDS = 4
MIN_MONEY_FOR_HIRE = 500
DROP_THRESHOLD = 8

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
            if isinstance(t, dict) and t.get("kind") == "PLANT" and t["crop"] == "MELON":
                age = day - t["planted_day"]
                if age >= CROPS["MELON"]["max_yield_day"]:
                    tasks.append(("HARVEST", x, y))
                elif not t.get("watered_today"):
                    tasks.append(("WATER", x, y))
            elif t is None and seeds.get("MELON", 0) > 0 and day < 24:
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

        # === MARKET ORDERS ===
        market = []

        # Sell melon in tranches (sq impact), every market window
        if hour in (0, 12) and shed.get("MELON", 0) > 0:
            q = shed["MELON"]
            tr = 3 if day >= 25 else 2
            max_orders = 10 if day >= 26 else 9
            while q > 0 and len(market) < max_orders:
                n = min(tr, q)
                market.append(["SELL", "MELON", n])
                q -= n

        # Buy melon seeds to maintain stock >= 2 (80 coins each)
        if seeds.get("MELON", 0) < 2 and f["money"] >= CROPS["MELON"]["seed"] * 2:
            market.append(["BUY_SEED", "MELON", 2 - seeds.get("MELON", 0)])

        # Hire hands at start of day
        if hour == 0 and f.get("hires_today", 0) < MAX_HANDS and f["money"] > MIN_MONEY_FOR_HIRE:
            market.append(["HIRE"])

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
            inv_total = sum(u_inv.values()) if u_inv else 0

            # BATCH DROP: go to shed only when inventory >= threshold OR no tasks left
            if u_inv and inv_total >= DROP_THRESHOLD:
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
                        actions[i] = ["PLANT", "MELON"]
                else:
                    actions[i] = _step(u_pos, (tx, ty)) or ["PASS"]
            else:
                # No tasks left - if have inventory, go DROP; else idle
                if u_inv:
                    if _shed_adjacent(u_pos, board_size):
                        actions[i] = ["DROP"]
                    else:
                        actions[i] = _step(u_pos, _nearest_shed(u_pos, board_size)) or ["PASS"]
                else:
                    actions[i] = ["PASS"]

        return {
            "farmer": actions[0],
            "hands": actions[1:],
            "market": market,
        }

    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}