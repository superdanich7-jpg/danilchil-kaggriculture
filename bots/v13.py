"""Kaggriculture v13: 2 cows + fertilizer cycle + melon (workers prioritize animals)."""

# ===== КОНСТАНТЫ =====
CROPS = {
    "MELON": {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "max_yield": 6},
}
MAX_HANDS = 6
DROP_THRESHOLD = 8
MELON_DANGER_THRESHOLD = 10
ANIMAL_PRICES = {"COW": 400}
PASTURES = [(2, 2), (3, 2)]  # 2 пастбища для 2 коров
SHED_POS = [(4, 4), (5, 4), (4, 5), (5, 5)]

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
    access = [(half-1, half-1), (half, half-1), (half-1, half), (half, half)]
    return tuple(pos) in access

def _nearest_shed(pos, board_size=10):
    half = board_size // 2
    access = [(half-1, half-1), (half, half-1), (half-1, half), (half, half)]
    return min(access, key=lambda p: _dist(pos, p))

def _scan_opponent_crops(obs):
    enemy_melons = 0
    player_id = obs["player"]
    for idx, farm_data in enumerate(obs["farms"]):
        if idx == player_id:
            continue
        for row in farm_data["tiles"]:
            for tile in row:
                if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "MELON":
                    enemy_melons += 1
    return enemy_melons

def _find_cows(tiles):
    cows = []
    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("animal") == "COW":
                cows.append(((x, y), t))
    return cows

def _find_pasture_state(tiles):
    built = []
    empty = []
    for (px, py) in PASTURES:
        tile = tiles[py][px]
        if isinstance(tile, dict) and tile.get("kind") == "PASTURE":
            built.append((px, py))
            if "animal" not in tile:
                empty.append((px, py))
    return built, empty

def _animal_tasks(f, pos, tiles, inv_w, inv_total):
    """Животноводческие задачи по приоритету: FEED, COLLECT_FERTILIZER, HARVEST."""
    for (cpos, t) in _find_cows(tiles):
        if not t.get("fed_today", False):
            if inv_w > 0:
                if tuple(cpos) == tuple(pos):
                    return ["FEED"]
                return _step(pos, cpos) or ["PASS"]
            break  # нужно пополнить WHEAT, вернёмся сюда после PICKUP
    for (cpos, t) in _find_cows(tiles):
        if t.get("fertilizer_available"):
            if tuple(cpos) == tuple(pos):
                return ["COLLECT_FERTILIZER"]
            return _step(pos, cpos) or ["PASS"]
    for (cpos, t) in _find_cows(tiles):
        if t.get("yield_units", 0) > 0:
            if tuple(cpos) == tuple(pos):
                return ["HARVEST"]
            return _step(pos, cpos) or ["PASS"]
    return None


def _melon_tasks(f, pos, day, seeds, harvest_age):
    """Melon: ближайшая WATER/HARVEST/PLANT задача к позиции."""
    tasks = []
    lazy = day < 5
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON":
                age = day - t["planted_day"]
                if age >= harvest_age and not t.get("harvested_today"):
                    tasks.append(("HARVEST", x, y))
                elif not t.get("watered_today"):
                    if not lazy or t.get("consecutive_unwatered", 0) >= 1:
                        tasks.append(("WATER", x, y))
    if seeds.get("MELON", 0) > 0:
        for y, row in enumerate(f["tiles"]):
            for x, t in enumerate(row):
                if t is None and day < 24:
                    tasks.append(("PLANT", x, y))
                    break
            else:
                continue
            break
    if not tasks:
        return None
    tasks.sort(key=lambda task: _dist(pos, (task[1], task[2])))
    tt, tx, ty = tasks[0]
    if tuple(pos) == (tx, ty):
        if tt == "HARVEST":
            return ["HARVEST"]
        if tt == "WATER":
            return ["WATER"]
        if tt == "PLANT":
            return ["PLANT", "MELON"]
    return _step(pos, (tx, ty)) or ["PASS"]

def _placement_action(f, pos, farmer_inv, shed):
    """Фермер: размещение коров в день 0-2 (BUILD -> PICKUP -> PLACE)."""
    tiles = f["tiles"]
    built, empty = _find_pasture_state(tiles)
    cows = _find_cows(tiles)
    if len(cows) >= 2:
        return None

    cow_in_inv = farmer_inv.get("COW", 0) > 0
    cow_in_shed = shed.get("COW", 0) > 0

    # 1. Построить недостающие пастбища
    if len(built) < 2:
        for (px, py) in PASTURES:
            tile = tiles[py][px]
            if not (isinstance(tile, dict) and tile.get("kind") == "PASTURE"):
                target = (px, py)
                if tuple(pos) == target:
                    return ["BUILD_PASTURE"]
                return _step(pos, target) or ["PASS"]
        return None

    # 2. Взять корову из сарая
    if cow_in_shed and not cow_in_inv:
        if _shed_adjacent(pos):
            return ["PICKUP", "COW", 1]
        return _step(pos, _nearest_shed(pos)) or ["PASS"]

    # 3. Разместить корову на пустом пастбище
    if cow_in_inv and empty:
        target = empty[0]
        if tuple(pos) == target:
            return ["PLACE", "COW"]
        return _step(pos, target) or ["PASS"]

    return None


def _unit_action(obs, pos, inv, inv_total, is_farmer, day, seeds, shed, harvest_age, placement_in_progress):
    """Определить действие одного юнита (farmer или hand) от его позиции."""
    f = _farm(obs)
    tiles = f["tiles"]
    inv_w = inv.get("WHEAT", 0)

    # DROP приоритет при полном инвентаре
    if inv_total >= DROP_THRESHOLD - 2:
        if _shed_adjacent(pos):
            return ["DROP"]
        return _step(pos, _nearest_shed(pos)) or ["PASS"]

    # Фермер: размещение коров в начале
    if is_farmer and placement_in_progress:
        a = _placement_action(f, pos, inv, shed)
        if a is not None:
            return a

    # Нужно пополнить WHEAT для корма
    cows = _find_cows(tiles)
    needs_feed = cows and any(not c[1].get("fed_today", False) for c in cows)
    if needs_feed and inv_w == 0 and shed.get("WHEAT", 0) > 0:
        if _shed_adjacent(pos):
            return ["PICKUP", "WHEAT", 1]
        return _step(pos, _nearest_shed(pos)) or ["PASS"]

    # Животноводческие задачи
    a = _animal_tasks(f, pos, tiles, inv_w, inv_total)
    if a is not None:
        return a

    # Melon
    a = _melon_tasks(f, pos, day, seeds, harvest_age)
    if a is not None:
        return a

    return ["PASS"]

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

        # === 1. РАЗВЕДКА ===
        enemy_melons = _scan_opponent_crops(obs)
        harvest_age = CROPS["MELON"]["max_yield_day"]
        if enemy_melons >= MELON_DANGER_THRESHOLD:
            harvest_age = CROPS["MELON"]["first_yield_day"] + 1

        # === 2. РЫНОК ===
        market = []
        if hour in (0, 12):
            fq = shed.get("FERTILIZER", 0)
            if fq > 0:
                market.append(["SELL", "FERTILIZER", min(10, fq)])
            mq = shed.get("MILK", 0)
            if mq > 0:
                market.append(["SELL", "MILK", min(5, mq)])
            melq = shed.get("MELON", 0)
            if melq > 0:
                tr = 3 if day >= 25 else 2
                maxo = 10 if day >= 26 else 9
                while melq > 0 and len(market) < maxo:
                    market.append(["SELL", "MELON", min(tr, melq)])
                    melq -= tr

        if hour == 0 and shed.get("WHEAT", 0) < 3 and money >= 30:
            market.append(["BUY_PRODUCT", "WHEAT", 3])
        if hour == 0 and day < 3 and len(_find_cows(f["tiles"])) < 2 and money > 500:
            market.append(["BUY_ANIMAL", "COW", 1])
        if seeds.get("MELON", 0) < 2 and money >= CROPS["MELON"]["seed"] * 2:
            market.append(["BUY_SEED", "MELON", 2 - seeds.get("MELON", 0)])
        if hour == 0 and f.get("hires_today", 0) < MAX_HANDS and money > 33:
            market.append(["HIRE"])

        # === 3. КООРДИНАЦИЯ ЮНИТОВ ===
        units = [tuple(f["farmer"])] + [tuple(h) for h in f.get("hands", [])]
        n_units = len(units)
        placement_in_progress = day < 3 and len(_find_cows(f["tiles"])) < 2

        actions = [["PASS"] for _ in range(n_units)]
        for i, u_pos in enumerate(units):
            inv = invs[i] if i < len(invs) else {}
            inv_total = sum(inv.values()) if inv else 0
            a = _unit_action(obs, u_pos, inv, inv_total, (i == 0), day, seeds, shed,
                             harvest_age, placement_in_progress)
            actions[i] = a

        return {
            "farmer": actions[0],
            "hands": actions[1:],
            "market": market,
        }
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
