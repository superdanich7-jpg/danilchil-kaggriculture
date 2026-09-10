"""Kaggriculture v12 MINIMAL: 1 goose + wheat for FEED + melon on v9 base."""

CROPS = {
    "MELON": {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "max_yield": 6},
}

MAX_HANDS = 7
MIN_MONEY_FOR_HIRE = 500
DROP_THRESHOLD = 8
MELON_DANGER_THRESHOLD = 10

ANIMAL_PRICES = {"GOOSE": 300}

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

def _find_goose(tiles):
    """Найти гуся на поле (животные в tiles, НЕ в priv.animals)."""
    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("animal") == "GOOSE":
                return (x, y), t
    return None, None

def _find_empty_coop(tiles):
    """Найти пустой COOP."""
    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("kind") == "COOP" and "animal" not in t:
                return (x, y)
    return None

def _collect_tasks(f, day, seeds, harvest_age_melon):
    """Сбор задач: только для фермера (животноводство) + стандартные для батраков."""
    tasks = []
    board_size = len(f["tiles"])
    
    # 1. FEED животных (сканируем tiles, НЕ priv.animals)
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and "animal" in t:
                # Животное найдено
                if t.get("consecutive_unfed", 0) >= 1:
                    tasks.append(("FEED", x, y, {"animal_id": id(t), "crop": "WHEAT"}))
    
    # 2. COLLECT_FERTILIZER
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and "animal" in t and t.get("fertilizer_available"):
                tasks.append(("COLLECT_FERTILIZER", x, y, {"animal_id": id(t)}))
    
    # 3. HARVEST (яйца/молоко/шерсть)
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and "animal" in t and t.get("yield_units", 0) > 0:
                tasks.append(("HARVEST", x, y, {}))
    
    # 4. WATER / HARVEST растений
    lazy_water = (day < 5)
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                crop = t.get("crop")
                if crop == "MELON":
                    age = day - t["planted_day"]
                    if age >= harvest_age_melon and not t.get("harvested_today"):
                        tasks.append(("HARVEST", x, y, {"crop": crop}))
                    elif not t.get("watered_today"):
                        if not lazy_water or t.get("consecutive_unwatered", 0) >= 1:
                            tasks.append(("WATER", x, y, {"crop": crop}))
    
    # 5. PLANT
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if t is None and day < 24:
                if seeds.get("MELON", 0) > 0:
                    tasks.append(("PLANT", x, y, {"crop": "MELON"}))
    
    return tasks

def agent(obs):
    try:
        f = _farm(obs)
        priv = _priv(obs)
        pos = tuple(f["farmer"])
        day = obs["day"]
        hour = obs.get("hour", 0)
        seeds = priv.get("seeds", {}) or {}
        shed = priv.get("shed", {}) or {}
        invs = priv.get("inventories") or [{}]
        
        board_size = len(f["tiles"])
        
        # === 1. РАЗВЕДКА ===
        enemy_melons = _scan_opponent_crops(obs)
        target_harvest_age = CROPS["MELON"]["max_yield_day"]
        if enemy_melons >= MELON_DANGER_THRESHOLD:
            target_harvest_age = CROPS["MELON"]["first_yield_day"] + 1
        
        # === 2. РЫНОК И ОРДЕРА ===
        market = []
        
        if hour in (0, 12):
            # Продажи
            egg_qty = shed.get("EGG", 0)
            if egg_qty > 0:
                n = min(10, egg_qty)
                market.append(["SELL", "EGG", n])
            
            melon_qty = shed.get("MELON", 0)
            if melon_qty > 0:
                tr = 3 if day >= 25 else 2
                max_orders = 10 if day >= 26 else 9
                while melon_qty > 0 and len(market) < max_orders:
                    n = min(tr, melon_qty)
                    market.append(["SELL", "MELON", n])
                    melon_qty -= n
        
        # Покупка
        if day == 0 and hour == 0:
            # GUY день 0: покупаем гуся + пшеницу + семена
            if f["money"] >= ANIMAL_PRICES["GOOSE"] and shed.get("GOOSE", 0) == 0:
                market.append(["BUY_ANIMAL", "GOOSE", 1])
            if f["money"] >= 30 and shed.get("WHEAT", 0) < 10:
                market.append(["BUY_PRODUCT", "WHEAT", 10])
            if seeds.get("MELON", 0) < 2 and f["money"] >= CROPS["MELON"]["seed"] * 2:
                market.append(["BUY_SEED", "MELON", 2])
        
        if hour == 0 and f.get("hires_today", 0) < MAX_HANDS and f["money"] > 33:
            market.append(["HIRE"])
        
        # === 3. КООРДИНАЦИЯ ===
        units = [tuple(f["farmer"])] + [tuple(h) for h in f.get("hands", [])]
        n_units = len(units)
        
        tasks = _collect_tasks(f, day, seeds, target_harvest_age)
        
        # Приоритеты: FEED > COLLECT_FERT > HARVEST > WATER > PLANT
        prio_map = {"FEED": 0, "COLLECT_FERTILIZER": 1, "HARVEST": 2, "WATER": 3, "PLANT": 4}
        tasks.sort(key=lambda t: (prio_map.get(t[0], 99), _dist(units[0], (t[1], t[2]))))
        
        assigned = set()
        actions = [["PASS"] for _ in range(n_units)]
        
        for i, u_pos in enumerate(units):
            u_inv = invs[i] if i < len(invs) else {}
            inv_total = sum(u_inv.values()) if u_inv else 0
            
            # BATCH DROP
            if u_inv and inv_total >= DROP_THRESHOLD:
                if _shed_adjacent(u_pos, board_size):
                    actions[i] = ["DROP"]
                else:
                    actions[i] = _step(u_pos, _nearest_shed(u_pos, board_size)) or ["PASS"]
                continue
            
            # Ищем ближайшую свободную задачу
            best_task = None
            best_dist = float('inf')
            for task in tasks:
                t_type, tx, ty, t_data = task
                if (tx, ty) in assigned:
                    continue
                d = _dist(u_pos, (tx, ty))
                if d < best_dist:
                    best_dist = d
                    best_task = task
            
            if best_task:
                t_type, tx, ty, t_data = best_task
                assigned.add((tx, ty))
                if u_pos == (tx, ty):
                    if t_type == "FEED":
                        actions[i] = ["FEED"]
                    elif t_type == "COLLECT_FERTILIZER":
                        actions[i] = ["COLLECT_FERTILIZER"]
                    elif t_type == "HARVEST":
                        actions[i] = ["HARVEST"]
                    elif t_type == "WATER":
                        actions[i] = ["WATER"]
                    elif t_type == "PLANT":
                        actions[i] = ["PLANT", t_data.get("crop", "MELON")]
                else:
                    actions[i] = _step(u_pos, (tx, ty)) or ["PASS"]
            else:
                # Нет задач - DROP или PASS
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