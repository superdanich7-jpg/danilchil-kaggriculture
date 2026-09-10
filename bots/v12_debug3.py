"""Kaggriculture v12 debug v3: animals + wheat + melon on v9 base (front-running)."""

# ===== КОНСТАНТЫ =====
CROPS = {
    "MELON": {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "max_yield": 6},
    "WHEAT": {"seed": 10, "first_yield_day": 3, "max_yield_day": 5, "max_yield": 2},
}

MAX_HANDS = 7
MIN_MONEY_FOR_HIRE = 500
DROP_THRESHOLD = 8
MELON_DANGER_THRESHOLD = 10

# Животные
ANIMAL_PRICES = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
BUILDING_PRICES = {"COOP": 300, "PASTURE": 400}

# ===== УТИЛИТЫ =====
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

# ===== ЗАДАЧИ =====
def _collect_tasks(f, day, seeds, animals, buildings_info, harvest_age_melon, desired_animals):
    """Сбор задач с приоритетом: FEED > DIG > WATER > HARVEST > CARE > COLLECT_FERT > PLANT > BUILD/PLACE."""
    tasks = []
    board_size = len(f["tiles"])
    
    # 1. FEED животных (если есть голодные)
    for aid, animal in animals.items():
        if animal.get("consecutive_unfed", 0) >= 1:
            bx, by = animal["pos"]
            tasks.append(("FEED", bx, by, {"animal_id": aid, "crop": "WHEAT"}))
    
    # 2. DIG сорняков
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("kind") == "WEED":
                tasks.append(("DIG", x, y, {}))
    
    # 3. WATER растений (ленивый полив первые 5 дней)
    lazy_water = (day < 5)
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                crop = t.get("crop")
                if crop in ["MELON", "WHEAT"]:
                    age = day - t["planted_day"]
                    if crop == "MELON" and age >= harvest_age_melon and not t.get("harvested_today"):
                        tasks.append(("HARVEST", x, y, {"crop": crop}))
                    elif crop == "WHEAT" and age >= 4 and not t.get("harvested_today"):
                        tasks.append(("HARVEST", x, y, {"crop": crop}))
                    elif not t.get("watered_today"):
                        if not lazy_water or t.get("consecutive_unwatered", 0) >= 1:
                            tasks.append(("WATER", x, y, {"crop": crop}))
    
    # 4. CARE животных (+1 продукт)
    for aid, animal in animals.items():
        if not animal.get("cared_today"):
            bx, by = animal["pos"]
            tasks.append(("CARE", bx, by, {"animal_id": aid}))
    
    # 5. COLLECT_FERTILIZER из животных (1/день)
    for aid, animal in animals.items():
        if not animal.get("fertilizer_collected_today"):
            bx, by = animal["pos"]
            tasks.append(("COLLECT_FERTILIZER", bx, by, {"animal_id": aid}))
    
    # 6. PLANT пустых тайлов (если есть семена)
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if t is None and day < 24:
                if seeds.get("WHEAT", 0) > 0:
                    tasks.append(("PLANT", x, y, {"crop": "WHEAT"}))
                elif seeds.get("MELON", 0) > 0:
                    tasks.append(("PLANT", x, y, {"crop": "MELON"}))
    
    # 7. BUILD/PLACE построек и размещение животных (только первые дни)
    if day < 5:
        # Строим постройки (если нет в buildings_info)
        for btype, bpos in buildings_info.items():
            # Проверяем есть ли уже эта постройка на поле
            tx, ty = bpos
            tile = f["tiles"][ty][tx]
            if tile is None or (isinstance(tile, dict) and tile.get("kind") != "STRUCTURE"):
                tasks.append(("BUILD_" + btype, tx, ty, {"type": btype}))
        
        # Размещаем животных (если они в инвентаре, а постройка есть)
        for da in desired_animals:
            aid = da["aid"]
            atype = da["type"]
            if aid in animals and not animals[aid].get("placed"):
                ax, ay = animals[aid]["pos"]
                # Проверяем что постройка существует
                struct_type = "COOP" if atype == "GOOSE" else "PASTURE"
                sx, sy = buildings_info.get(struct_type, (None, None))
                if sx is not None:
                    # Проверяем что на позиции есть постройка
                    struct_tile = f["tiles"][sy][sx]
                    if isinstance(struct_tile, dict) and struct_tile.get("kind") == "STRUCTURE":
                        tasks.append(("PLACE_ANIMAL", ax, ay, {"animal_id": aid, "type": atype}))
    
    return tasks

# ===== ОСНОВНОЙ АГЕНТ =====
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
        
        # Извлекаем животных и постройки
        animals = priv.get("animals", {}) or {}
        
        # Desired animals - hardcoded список
        desired_animals = [
            {"aid": "goose1", "type": "GOOSE"},
            {"aid": "cow1", "type": "COW"},
            {"aid": "cow2", "type": "COW"},
            {"aid": "sheep1", "type": "SHEEP"},
            {"aid": "sheep2", "type": "SHEEP"},
        ]
        
        # Buildings - ищем свободные позиции
        buildings_info = {}
        if day < 5:
            # Ищем свободные позиции для построек
            for y, row in enumerate(f["tiles"]):
                for x, t in enumerate(row):
                    if t is None:
                        buildings_info["COOP"] = (x, y)
                        break
                if "COOP" in buildings_info:
                    break
            if "COOP" not in buildings_info:
                for y, row in enumerate(f["tiles"]):
                    for x, t in enumerate(row):
                        if t is None:
                            buildings_info["PASTURE"] = (x, y)
                            break
                    if "PASTURE" in buildings_info:
                        break
        
        # === 1. РАЗВЕДКА И ТАЙМИНГ MELON ===
        enemy_melons = _scan_opponent_crops(obs)
        target_harvest_age = CROPS["MELON"]["max_yield_day"]
        if enemy_melons >= MELON_DANGER_THRESHOLD:
            target_harvest_age = CROPS["MELON"]["first_yield_day"] + 1
        
        # === 2. РЫНОК И ОРДЕРА ===
        market = []
        
        if hour in (0, 12):
            # Продажи (как в v9)
            melon_qty = shed.get("MELON", 0)
            if melon_qty > 0:
                tr = 3 if day >= 25 else 2
                max_orders = 10 if day >= 26 else 9
                while melon_qty > 0 and len(market) < max_orders:
                    n = min(tr, melon_qty)
                    market.append(["SELL", "MELON", n])
                    melon_qty -= n
        
        # Покупка семян
        if seeds.get("MELON", 0) < 2 and f["money"] >= CROPS["MELON"]["seed"] * 2:
            market.append(["BUY_SEED", "MELON", 2 - seeds.get("MELON", 0)])
        if seeds.get("WHEAT", 0) < 12 and f["money"] >= CROPS["WHEAT"]["seed"] * 12:
            market.append(["BUY_SEED", "WHEAT", 12 - seeds.get("WHEAT", 0)])
        
        # Наём работников
        if hour == 0 and f.get("hires_today", 0) < MAX_HANDS and f["money"] > 33:
            market.append(["HIRE"])
        
        # Покупка животных (ШАГ A: только 1 GOOSE)
        if day < 5 and hour == 0:
            # Проверяем куплен ли уже гусь
            goose_in_shed = shed.get("GOOSE", 0)
            if goose_in_shed == 0 and f["money"] >= ANIMAL_PRICES["GOOSE"]:
                market.append(["BUY_ANIMAL", "GOOSE", 1])
        
        # === 3. КООРДИНАЦИЯ ===
        units = [tuple(f["farmer"])] + [tuple(h) for h in f.get("hands", [])]
        n_units = len(units)
        
        tasks = _collect_tasks(f, day, seeds, animals, buildings_info, target_harvest_age, desired_animals)
        
        prio_map = {"FEED": -2, "DIG": -1, "WATER": 0, "HARVEST": 1, "CARE": 2, 
                    "COLLECT_FERTILIZER": 3, "PLANT": 4, "BUILD_COOP": 5, "BUILD_PASTURE": 5, "PLACE_ANIMAL": 5}
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
                        actions[i] = ["FEED", t_data.get("animal_id"), t_data.get("crop", "WHEAT")]
                    elif t_type == "DIG":
                        actions[i] = ["DIG"]
                    elif t_type == "WATER":
                        actions[i] = ["WATER"]
                    elif t_type == "HARVEST":
                        actions[i] = ["HARVEST"]
                    elif t_type == "CARE":
                        actions[i] = ["CARE", t_data.get("animal_id")]
                    elif t_type == "COLLECT_FERTILIZER":
                        actions[i] = ["COLLECT_FERTILIZER", t_data.get("animal_id")]
                    elif t_type == "PLANT":
                        actions[i] = ["PLANT", t_data.get("crop", "WHEAT")]
                    elif t_type == "BUILD_COOP":
                        actions[i] = ["BUILD_COOP"]
                    elif t_type == "BUILD_PASTURE":
                        actions[i] = ["BUILD_PASTURE"]
                    elif t_type == "PLACE_ANIMAL":
                        actions[i] = ["PLACE_ANIMAL", t_data.get("animal_id"), t_data.get("type")]
                else:
                    actions[i] = _step(u_pos, (tx, ty)) or ["PASS"]
            else:
                # Нет задач - идём сбрасывать инвентарь
                if u_inv:
                    if _shed_adjacent(u_pos, board_size):
                        actions[i] = ["DROP"]
                    else:
                        actions[i] = _step(u_pos, _nearest_shed(u_pos, board_size)) or ["PASS"]
                else:
                    actions[i] = ["PASS"]
        
        # === 4. DEBUG ЛОГ ===
        if hour == 0:
            animal_count = len(animals)
            consec_unfed = sum(animal.get("consecutive_unfed", 0) for animal in animals.values())
            wheat_shed = shed.get("WHEAT", 0)
            wheat_inv = sum(u_inv.get("WHEAT", 0) for u_inv in invs if u_inv)
            feeds_done = sum(1 for act in actions if act and act[0] == "FEED")
            shed_total = sum(v for v in shed.values() if isinstance(v, (int, float)))
            
            # Market orders
            buy_animal_orders = [m for m in market if m[0] == "BUY_ANIMAL"]
            build_actions = [act for act in actions if act and act[0] in ["BUILD_COOP", "BUILD_PASTURE"]]
            place_actions = [act for act in actions if act and act[0] == "PLACE_ANIMAL"]
            hire_orders = [m for m in market if m[0] == "HIRE"]
            
            log_line = (day, f["money"], animal_count, consec_unfed, wheat_shed, 
                       wheat_inv, feeds_done, shed_total, buy_animal_orders, build_actions, place_actions, hire_orders)
            debug_log.append(log_line)
        
        return {
            "farmer": actions[0],
            "hands": actions[1:],
            "market": market,
        }
    
    except Exception as e:
        return {"farmer": ["PASS"], "hands": [], "market": []}

# Глобальный лог для диагностики
debug_log = []