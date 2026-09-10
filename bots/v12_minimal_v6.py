"""Kaggriculture v12 MINIMAL v6: goose placement (test_goose_fed) + melon (v9)."""

# ===== КОНСТАНТЫ =====
CROPS = {
    "MELON": {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "max_yield": 6},
}
MAX_HANDS = 7
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

def _find_animal(tiles, animal_type):
    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("animal") == animal_type:
                return (x, y), t
    return None, None

def _collect_tasks(f, day, seeds, harvest_age_melon):
    tasks = []
    board_size = len(f["tiles"])
    
    # 1. FEED (приоритет -2)
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and "animal" in t:
                if t.get("consecutive_unfed", 0) >= 1:
                    tasks.append(("FEED", x, y, {}))
    
    # 2. COLLECT_FERTILIZER
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and "animal" in t and t.get("fertilizer_available"):
                tasks.append(("COLLECT_FERTILIZER", x, y, {}))
    
    # 3. HARVEST (яйца)
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and "animal" in t and t.get("yield_units", 0) > 0:
                tasks.append(("HARVEST", x, y, {}))
    
    # 4. WATER / HARVEST melon
    lazy_water = (day < 5)
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                crop = t.get("crop")
                if crop == "MELON":
                    age = day - t["planted_day"]
                    if age >= harvest_age_melon and not t.get("harvested_today"):
                        tasks.append(("HARVEST", x, y, {}))
                    elif not t.get("watered_today"):
                        if not lazy_water or t.get("consecutive_unwatered", 0) >= 1:
                            tasks.append(("WATER", x, y, {}))
    
    # 5. PLANT melon
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
        
        # Покупка (только день 0, hour 0)
        if day == 0 and hour == 0:
            # Покупаем гуся
            if f["money"] >= 300 and shed.get("GOOSE", 0) == 0:
                market.append(["BUY_ANIMAL", "GOOSE", 1])
            # Покупаем пшеницу для корма (10 шт)
            if f["money"] >= 100 and shed.get("WHEAT", 0) < 10:
                market.append(["BUY_PRODUCT", "WHEAT", 10])
            # Покупаем семена melon
            if seeds.get("MELON", 0) < 2 and f["money"] >= 160:
                market.append(["BUY_SEED", "MELON", 2])
        
        # Наём работников
        if hour == 0 and f.get("hires_today", 0) < MAX_HANDS and f["money"] > 33:
            market.append(["HIRE"])
        
        # === 3. КООРДИНАЦИЯ ===
        units = [tuple(f["farmer"])] + [tuple(h) for h in f.get("hands", [])]
        n_units = len(units)
        
        # Проверяем статус гуся
        goose_pos, goose_tile = _find_animal(f["tiles"], "GOOSE")
        farmer_inv = invs[0] if invs else {}
        farmer_wheat = farmer_inv.get("WHEAT", 0)
        
        # ===== ФАЗА 1: PLACEMENT (дни 0-2) =====
        if goose_pos is None and day < 3:
            # Шаг 1: PICKUP GOOSE из сарая
            if shed.get("GOOSE", 0) > 0:
                if _shed_adjacent(pos, board_size):
                    actions_f = ["PICKUP", "GOOSE", 1]
                else:
                    target = _nearest_shed(pos, board_size)
                    actions_f = _step(pos, target) or ["PASS"]
            # Шаг 2: BUILD_COOP
            else:
                # Ищем пустой тайл для COOP
                empty_coop = None
                for y, row in enumerate(f["tiles"]):
                    for x, t in enumerate(row):
                        if isinstance(t, dict) and t.get("kind") == "COOP" and "animal" not in t:
                            empty_coop = (x, y)
                            break
                    if empty_coop:
                        break
                
                if empty_coop is None:
                    # Строим COOP на (2,2)
                    target = (2, 2)
                    if pos == target:
                        actions_f = ["BUILD_COOP"]
                    else:
                        actions_f = _step(pos, target) or ["PASS"]
                else:
                    # PLACE GOOSE
                    if pos == empty_coop:
                        actions_f = ["PLACE", "GOOSE"]
                    else:
                        actions_f = _step(pos, empty_coop) or ["PASS"]
        
        # ===== ФАЗА 2: DAILY CYCLE (дни 3-29) =====
        elif goose_pos is not None:
            # Приоритет 1: PICKUP WHEAT если мало
            if farmer_wheat < 3 and shed.get("WHEAT", 0) > 0:
                if _shed_adjacent(pos, board_size):
                    actions_f = ["PICKUP", "WHEAT", 3]
                else:
                    target = _nearest_shed(pos, board_size)
                    actions_f = _step(pos, target) or ["PASS"]
            else:
                # Собираем задачи
                tasks = _collect_tasks(f, day, seeds, target_harvest_age)
                
                # Сортируем по приоритету
                prio_map = {"FEED": -2, "COLLECT_FERTILIZER": -1, "HARVEST": 0, "WATER": 1, "PLANT": 2}
                tasks.sort(key=lambda t: (prio_map.get(t[0], 99), _dist(pos, (t[1], t[2]))))
                
                # Ищем ближайшую задачу
                best_task = None
                best_dist = float('inf')
                assigned = set()
                for task in tasks:
                    t_type, tx, ty, t_data = task
                    if (tx, ty) in assigned:
                        continue
                    d = _dist(pos, (tx, ty))
                    if d < best_dist:
                        best_dist = d
                        best_task = task
                
                if best_task:
                    t_type, tx, ty, t_data = best_task
                    assigned.add((tx, ty))
                    if pos == (tx, ty):
                        if t_type == "FEED":
                            actions_f = ["FEED"]
                        elif t_type == "COLLECT_FERTILIZER":
                            actions_f = ["COLLECT_FERTILIZER"]
                        elif t_type == "HARVEST":
                            actions_f = ["HARVEST"]
                        elif t_type == "WATER":
                            actions_f = ["WATER"]
                        elif t_type == "PLANT":
                            actions_f = ["PLANT", t_data.get("crop", "MELON")]
                        else:
                            actions_f = ["PASS"]
                    else:
                        actions_f = _step(pos, (tx, ty)) or ["PASS"]
                else:
                    # Нет задач — DROP или PASS
                    if farmer_inv and sum(farmer_inv.values()) >= DROP_THRESHOLD:
                        if _shed_adjacent(pos, board_size):
                            actions_f = ["DROP"]
                        else:
                            target = _nearest_shed(pos, board_size)
                            actions_f = _step(pos, target) or ["PASS"]
                    else:
                        actions_f = ["PASS"]
        
        # Если гусь ещё не размещён и день >= 3 (placement failed)
        else:
            actions_f = ["PASS"]
        
        # Батраки: только melon логистика (v9)
        hands_actions = []
        for i in range(1, n_units):
            u_pos = units[i]
            u_inv = invs[i] if i < len(invs) else {}
            inv_total = sum(u_inv.values()) if u_inv else 0
            
            if u_inv and inv_total >= DROP_THRESHOLD:
                if _shed_adjacent(u_pos, board_size):
                    hands_actions.append(["DROP"])
                else:
                    hands_actions.append(_step(u_pos, _nearest_shed(u_pos, board_size)) or ["PASS"])
            else:
                hands_actions.append(["PASS"])
        
        return {
            "farmer": actions_f,
            "hands": hands_actions,
            "market": market,
        }
    
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}