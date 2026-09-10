"""Kaggriculture v16: farmer melon-only + front-run + immediate market."""

CROPS = {
    "MELON": {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "max_yield": 6},
}
MELON_DANGER_THRESHOLD = 10
MAX_HANDS = 6
DROP_THRESHOLD = 8
PASTURES = [(2, 2)]


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
    return tuple(pos) in [(half-1, half-1), (half, half-1), (half-1, half), (half, half)]


def _nearest_shed(pos, board_size=10):
    half = board_size // 2
    access = [(half-1, half-1), (half, half-1), (half-1, half), (half, half)]
    return min(access, key=lambda p: _dist(pos, p))


def _empty_tiles(f):
    tiles = f["tiles"]
    return [(x, y) for y, row in enumerate(tiles) for x, t in enumerate(row) if t is None]


def _find_animals(tiles):
    res = []
    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if isinstance(t, dict) and "animal" in t:
                res.append(((x, y), t))
    return res


def _scan_opponent_crops(obs):
    pid = obs["player"]
    mel = 0
    for idx, fd in enumerate(obs["farms"]):
        if idx == pid:
            continue
        for row in fd["tiles"]:
            for t in row:
                if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON":
                    mel += 1
    return mel


def _crop_pool(f, day, seeds, harvest_age=12):
    """WATER > HARVEST > PLANT — always plant & water."""
    tasks = []
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON":
                age = day - t["planted_day"]
                if age >= harvest_age and not t.get("harvested_today"):
                    tasks.append(("HARVEST", x, y))
                elif not t.get("watered_today"):
                    tasks.append(("WATER", x, y))
            elif t is None and seeds.get("MELON", 0) > 0 and day < 24:
                tasks.append(("PLANT", x, y))
    return tasks


def _assign_nearest(pos, tasks, assigned):
    best = None
    bd = 1 << 30
    for tk in tasks:
        if (tk[1], tk[2]) in assigned:
            continue
        d = _dist(pos, (tk[1], tk[2]))
        if d < bd:
            bd = d
            best = tk
    if best is None:
        return None
    tt, tx, ty = best
    assigned.add((tx, ty))
    if tuple(pos) == (tx, ty):
        if tt == "HARVEST": return ["HARVEST"]
        if tt == "WATER": return ["WATER"]
        if tt == "PLANT": return ["PLANT", "MELON"]
    return _step(pos, (tx, ty)) or ["PASS"]


def _drop_or_move(pos, inv_total):
    if inv_total >= DROP_THRESHOLD:
        return ["DROP"] if _shed_adjacent(pos) else (_step(pos, _nearest_shed(pos)) or ["PASS"])
    return None


def _animal_tasks(f, pos, inv, inv_total, shed):
    if inv_total >= DROP_THRESHOLD:
        return ["DROP"] if _shed_adjacent(pos) else (_step(pos, _nearest_shed(pos)) or ["PASS"])
    anims = _find_animals(f["tiles"])
    if not anims:
        return None
    inv_w = inv.get("WHEAT", 0)
    for (apos, t) in anims:
        if not t.get("fed_today", False):
            if inv_w > 0:
                if tuple(apos) == tuple(pos): return ["FEED"]
                return _step(pos, apos) or ["PASS"]
            if shed.get("WHEAT", 0) > 0:
                if _shed_adjacent(pos): return ["PICKUP", "WHEAT", 1]
                return _step(pos, _nearest_shed(pos)) or ["PASS"]
            return None
    for (apos, t) in anims:
        if t.get("fertilizer_available"):
            if tuple(apos) == tuple(pos): return ["COLLECT_FERTILIZER"]
            return _step(pos, apos) or ["PASS"]
    for (apos, t) in anims:
        if t.get("yield_units", 0) > 0:
            if tuple(apos) == tuple(pos): return ["HARVEST"]
            return _step(pos, apos) or ["PASS"]
    return None


def _placement_action(f, pos, inv, shed):
    tiles = f["tiles"]
    if _find_animals(tiles):
        return None
    px, py = PASTURES[0]
    tile = tiles[py][px]
    built = isinstance(tile, dict) and tile.get("kind") == "PASTURE"
    empty = built and "animal" not in tile
    cow_in_inv = inv.get("COW", 0) > 0
    cow_in_shed = shed.get("COW", 0) > 0
    if not built:
        if tuple(pos) == (px, py): return ["BUILD_PASTURE"]
        return _step(pos, (px, py)) or ["PASS"]
    if cow_in_shed and not cow_in_inv:
        if _shed_adjacent(pos): return ["PICKUP", "COW", 1]
        return _step(pos, _nearest_shed(pos)) or ["PASS"]
    if cow_in_inv and empty:
        if tuple(pos) == (px, py): return ["PLACE", "COW"]
        return _step(pos, (px, py)) or ["PASS"]
    return None


# ===== AGENT =====
def agent(obs):
    try:
        f = _farm(obs)
        priv = _priv(obs)
        day = obs["day"]
        hour = obs.get("hour", 0)
        seeds = priv.get("seeds", {}) or {}
        shed = priv.get("shed", {}) or {}
        invs = priv.get("inventories") or [{}]
        money = f["money"]
        units = [tuple(f["farmer"])] + [tuple(h) for h in f.get("hands", [])]
        n = len(units)
        anims = _find_animals(f["tiles"])
        phase = "plant" if day <= 5 else ("setup" if day <= 10 else "harvest")
        farmer_only = len(f.get("hands", [])) == 0

        market = []
        if hour == 0:
            if f.get("hires_today", 0) < MAX_HANDS and money > 33:
                market.append(["HIRE"])
            if seeds.get("MELON", 0) < 2 and money >= 160:
                market.append(["BUY_SEED", "MELON", 2 - seeds.get("MELON", 0)])
        # ---- РЫНОК: SELL немедленно, без ценового шлюза ----
        if hour in (0, 12):
            mel = shed.get("MELON", 0)
            tr = 3 if day >= 25 else 2
            while mel > 0 and len(market) < 10:
                market.append(["SELL", "MELON", min(tr, mel)])
                mel -= tr
            if shed.get("FERTILIZER", 0) > 0:
                market.append(["SELL", "FERTILIZER", min(10, shed["FERTILIZER"])])
            if shed.get("MILK", 0) > 0:
                market.append(["SELL", "MILK", min(5, shed["MILK"])])

        # ---- FRONT-RUN: если оппонент сажает мелон — собирать раньше ----
        enemy_melons = _scan_opponent_crops(obs)
        harvest_age = 11 if enemy_melons >= MELON_DANGER_THRESHOLD else 12
        assigned = set()
        pool = _crop_pool(f, day, seeds, harvest_age)
        actions = [["PASS"] for _ in range(n)]
        animal_active = (not farmer_only) and (phase != "plant") and bool(anims)

        for i, u in enumerate(units):
            inv = invs[i] if i < len(invs) else {}
            it = sum(inv.values()) if inv else 0
            d = _drop_or_move(u, it)
            if d:
                actions[i] = d
                continue
            if i == 0:
                # ФЕРМЕР: melon only
                actions[i] = _assign_nearest(u, pool, assigned) or ["PASS"]
            elif i <= 2 and animal_active:
                a = _animal_tasks(f, u, inv, it, shed)
                if a is None:
                    a = _assign_nearest(u, pool, assigned) or ["PASS"]
                actions[i] = a
            else:
                if phase == "setup" and not anims and money >= 2500:
                    a = _placement_action(f, u, inv, shed)
                    if a is None:
                        a = _assign_nearest(u, pool, assigned) or ["PASS"]
                    actions[i] = a
                else:
                    actions[i] = _assign_nearest(u, pool, assigned) or ["PASS"]

        return {"farmer": actions[0], "hands": actions[1:], "market": market}
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
