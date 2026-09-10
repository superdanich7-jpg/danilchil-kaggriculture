"""Kaggriculture v14: 1 animal-worker + 5 crop-workers + land + opponent model."""

# ===== КОНСТАНТЫ =====
CROPS = {
    "MELON": {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "max_yield": 6},
    "WHEAT": {"seed": 10, "first_yield_day": 3, "max_yield_day": 5, "max_yield": 2},
}
ANIMAL_INFO = {
    "COW":   {"cost": 400, "structure": "PASTURE", "product": "MILK"},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "product": "WOOL"},
    "GOOSE": {"cost": 300, "structure": "COOP",    "product": "EGG"},
}
MAX_HANDS = 6
DROP_THRESHOLD = 8
ANIMAL_WORKERS = 1   # сколько батраков занимается животными
PASTURES = [(2, 2), (3, 2)]
COOP_POS = (4, 2)

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

def _scan_opponent(obs):
    enemy = obs["farms"][1 - obs["player"]]
    counts = {"COW": 0, "SHEEP": 0, "GOOSE": 0, "MELON": 0, "WHEAT": 0, "TOMATO": 0}
    for row in enemy["tiles"]:
        for t in row:
            if not isinstance(t, dict):
                continue
            if "animal" in t:
                counts[t["animal"]] = counts.get(t["animal"], 0) + 1
            if t.get("kind") == "PLANT":
                counts[t["crop"]] = counts.get(t["crop"], 0) + 1
    return counts


def _find_animals(tiles, atype=None):
    res = []
    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if isinstance(t, dict) and "animal" in t:
                if atype is None or t["animal"] == atype:
                    res.append(((x, y), t))
    return res

def _find_structure_state(tiles):
    built, empty = {}, {}
    for (px, py) in PASTURES:
        tile = tiles[py][px]
        if isinstance(tile, dict) and tile.get("kind") == "PASTURE":
            built["PASTURE"] = built.get("PASTURE", 0) + 1
            if "animal" not in tile:
                empty["PASTURE"] = (px, py)
    cx, cy = COOP_POS
    tile = tiles[cy][cx]
    if isinstance(tile, dict) and tile.get("kind") == "COOP":
        built["COOP"] = 1
        if "animal" not in tile:
            empty["COOP"] = (cx, cy)
    return built, empty

def _animal_tasks(f, pos, tiles, inv, inv_total, shed):
    """Цикл животных для одного выделенного батрака."""
    inv_w = inv.get("WHEAT", 0)
    # 0. DROP если полный
    if inv_total >= DROP_THRESHOLD - 2:
        if _shed_adjacent(pos):
            return ["DROP"]
        return _step(pos, _nearest_shed(pos)) or ["PASS"]
    anims = _find_animals(tiles)
    if not anims:
        return None
    # FEED: все животные без корма
    for (apos, t) in anims:
        if not t.get("fed_today", False):
            if inv_w > 0:
                if tuple(apos) == tuple(pos):
                    return ["FEED"]
                return _step(pos, apos) or ["PASS"]
            # нет пшеницы - взять из сарая
            if shed.get("WHEAT", 0) > 0:
                if _shed_adjacent(pos):
                    return ["PICKUP", "WHEAT", 1]
                return _step(pos, _nearest_shed(pos)) or ["PASS"]
            return None
    # COLLECT_FERTILIZER

def _crop_tasks(f, pos, day, seeds, crop):
    """Культуры: ближайшая WATER/HARVEST/PLANT для целевой культуры."""
    tasks = []
    lazy = day < 5
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == crop:
                age = day - t["planted_day"]
                if age >= CROPS[crop]["max_yield_day"] and not t.get("harvested_today"):
                    tasks.append(("HARVEST", x, y))
                elif not t.get("watered_today"):
                    if not lazy or t.get("consecutive_unwatered", 0) >= 1:
                        tasks.append(("WATER", x, y))
    if seeds.get(crop, 0) > 0:
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
            return ["PLANT", crop]
    return _step(pos, (tx, ty)) or ["PASS"]

def _placement_action(f, pos, farmer_inv, shed, target_animal):
    """Размещение животных: BUILD структуры -> PICKUP -> PLACE."""
    tiles = f["tiles"]
    built, empty = _find_structure_state(tiles)
    anims = _find_animals(tiles, target_animal)
    if target_animal == "COW" and len(anims) >= 2:
        return None
    if target_animal in ("SHEEP", "GOOSE") and anims:
        return None
    struct = ANIMAL_INFO[target_animal]["structure"]
    # 1. построить структуру
    if built.get(struct, 0) == 0:
        if struct == "COOP":
            target = COOP_POS
        else:
            target = PASTURES[0]
        if tuple(pos) == target:
            return ["BUILD_COOP"] if struct == "COOP" else ["BUILD_PASTURE"]
        return _step(pos, target) or ["PASS"]
    # 2. PICKUP из сарая
    a_in_inv = farmer_inv.get(target_animal, 0) > 0
    a_in_shed = shed.get(target_animal, 0) > 0
    if a_in_shed and not a_in_inv:
        if _shed_adjacent(pos):
            return ["PICKUP", target_animal, 1]
        return _step(pos, _nearest_shed(pos)) or ["PASS"]
    # 3. PLACE на пустой структуре
    if a_in_inv and struct in empty:
        target = empty[struct]
        if tuple(pos) == target:
            return ["PLACE", target_animal]

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

        # === 1. МОДЕЛЬ ОПОНЕНТА ===
        enemy = _scan_opponent(obs)
        target_animal = "SHEEP" if enemy["COW"] >= 2 else "COW"
        target_crop = "WHEAT" if enemy["MELON"] >= 15 else "MELON"
        harvest_age = CROPS["MELON"]["max_yield_day"]
        if target_crop == "MELON" and enemy["MELON"] >= 10:
            harvest_age = CROPS["MELON"]["first_yield_day"] + 1  # front-run

        # === 2. РЫНОК ===
        market = []
        if hour in (0, 12):
            # Антикорреляция: если оппонент тоже в этом продукте — продавать сразу
            opp_milk = enemy["COW"] >= 1
            opp_melon = enemy["MELON"] >= 10
            opp_wool = enemy["SHEEP"] >= 1
            opp_egg = enemy["GOOSE"] >= 1
            prod = ANIMAL_INFO[target_animal]["product"]
            if prod == "MILK" and shed.get("MILK", 0) > 0:
                market.append(["SELL", "MILK", min(5, shed.get("MILK", 0))])
            if prod == "WOOL" and shed.get("WOOL", 0) > 0:
                market.append(["SELL", "WOOL", min(3, shed.get("WOOL", 0))])
            if prod == "EGG" and shed.get("EGG", 0) > 0:
                market.append(["SELL", "EGG", min(10, shed.get("EGG", 0))])
            fq = shed.get("FERTILIZER", 0)
            if fq > 0:
                market.append(["SELL", "FERTILIZER", min(10, fq)])
            melq = shed.get("MELON", 0)
            if melq > 0:
                tr = 3 if day >= 25 else 2
                maxo = 10 if day >= 26 else 9
                while melq > 0 and len(market) < maxo:
                    market.append(["SELL", "MELON", min(tr, melq)])
                    melq -= tr
            wq = shed.get("WHEAT", 0)
            if wq > 0 and shed.get("WHEAT", 0) > 10:
                market.append(["SELL", "WHEAT", min(10, shed.get("WHEAT", 0) - 10)])

        # Покупки
        if hour == 0:
            # Земля NE на day 1
            if day == 1 and money > 1500:
                market.append(["BUY_LAND"])
            # семена под целевую культуру
            if target_crop == "MELON" and seeds.get("MELON", 0) < 3 and money >= 160:
                market.append(["BUY_SEED", "MELON", 3 - seeds.get("MELON", 0)])
            if target_crop == "WHEAT" and shed.get("WHEAT", 0) < 12 and money >= 120:
                market.append(["BUY_PRODUCT", "WHEAT", 12])
            # корм для животного
            if shed.get("WHEAT", 0) < 3 and money >= 30:
                market.append(["BUY_PRODUCT", "WHEAT", 3])
            # животное
            if day < 3 and money > 500:
                need = 1 - len(_find_animals(f["tiles"], target_animal))
                if need > 0 and shed.get(target_animal, 0) + 0 == 0:
                    market.append(["BUY_ANIMAL", target_animal, need])
            # найм
            if f.get("hires_today", 0) < MAX_HANDS and money > 33:
                market.append(["HIRE"])

        # === 3. КООРДИНАЦИЯ ===
        units = [tuple(f["farmer"])] + [tuple(h) for h in f.get("hands", [])]
        n_units = len(units)
        anims = _find_animals(f["tiles"])
        placement_in_progress = day < 3 and len(anims) == 0

        actions = [["PASS"] for _ in range(n_units)]
        for i, u_pos in enumerate(units):
            inv = invs[i] if i < len(invs) else {}
            inv_total = sum(inv.values()) if inv else 0
            if i == 0:
                actions[i] = _unit_action(obs, u_pos, inv, inv_total, True, day, seeds, shed,
                                          target_crop, target_animal, placement_in_progress)
            else:
                # Батрак 1: животные (если есть), остальные культуры
                if i <= ANIMAL_WORKERS and anims:
                    a = _animal_tasks(f, u_pos, f["tiles"], inv, inv_total, shed)
                    actions[i] = a if a is not None else _unit_action(obs, u_pos, inv, inv_total, False,
                                                                      day, seeds, shed, target_crop, target_animal, False)
                else:
                    actions[i] = _unit_action(obs, u_pos, inv, inv_total, False, day, seeds, shed,
                                              target_crop, target_animal, False)

        return {"farmer": actions[0], "hands": actions[1:], "market": market}
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}

        return _step(pos, target) or ["PASS"]
    return None


def _unit_action(obs, pos, inv, inv_total, is_farmer, day, seeds, shed, target_crop, target_animal, placement_in_progress):
    f = _farm(obs)
    tiles = f["tiles"]
    # DROP приоритет
    if inv_total >= DROP_THRESHOLD:
        if _shed_adjacent(pos):
            return ["DROP"]
        return _step(pos, _nearest_shed(pos)) or ["PASS"]
    if is_farmer and placement_in_progress:
        a = _placement_action(f, pos, inv, shed, target_animal)
        if a is not None:
            return a
    a = _crop_tasks(f, pos, day, seeds, target_crop)
    if a is not None:
        return a
    return ["PASS"]

    for (apos, t) in anims:
        if t.get("fertilizer_available"):
            if tuple(apos) == tuple(pos):
                return ["COLLECT_FERTILIZER"]
            return _step(pos, apos) or ["PASS"]
    # HARVEST
    for (apos, t) in anims:
        if t.get("yield_units", 0) > 0:
            if tuple(apos) == tuple(pos):
                return ["HARVEST"]
            return _step(pos, apos) or ["PASS"]
    return None
