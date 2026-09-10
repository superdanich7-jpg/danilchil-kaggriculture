"""Kaggriculture v10: EV Market Engine & Front-runner."""

# ТОЧНЫЕ ДАННЫЕ ИЗ ДАМПА СРЕДЫ
CROPS = {
    "WHEAT":      {"seed": 10,  "first_yield_day": 2,  "max_yield_day": 4,  "interval": 0, "max_yield": 6, "ongoing": False},
    "CARROT":     {"seed": 20,  "first_yield_day": 2,  "max_yield_day": 3,  "interval": 0, "max_yield": 4, "ongoing": False},
    "TOMATO":     {"seed": 50,  "first_yield_day": 8,  "max_yield_day": 8,  "interval": 1, "max_yield": 4, "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True},
    "MELON":      {"seed": 80,  "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False}
}

MAX_HANDS = 4
MIN_MONEY_FOR_HIRE = 500
DROP_THRESHOLD = 8
MELON_DANGER_THRESHOLD = 10 

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
        if idx == player_id: continue
        for row in farm_data["tiles"]:
            for tile in row:
                if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "MELON":
                    enemy_melons += 1
    return enemy_melons

def _collect_tasks(f, day, seeds, harvest_age, target_crop):
    tasks = []
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                crop = t.get("crop", "MELON")
                age = day - t["planted_day"]
                # Для ongoing культур (клубника/томат) логика сбора может отличаться, 
                # но пока опираемся на стандартный max_yield_day
                target_age = harvest_age if crop == "MELON" else CROPS.get(crop, {}).get("max_yield_day", 10)
                
                if age >= target_age:
                    tasks.append(("HARVEST", x, y, crop))
                elif not t.get("watered_today"):
                    tasks.append(("WATER", x, y, crop))
            elif t is None and seeds.get(target_crop, 0) > 0 and day < 24:
                tasks.append(("PLANT", x, y, target_crop))
    return tasks

def _simulate_ev(crop, amount):
    """
    Математическая симуляция выручки (Expected Value) на основе твоих эмпирических данных.
    Возвращает ожидаемую сумму монет за транш.
    """
    if amount <= 0: return 0
    
    # Базовые цены (эвристика, так как точные скрыты в движке)
    base_prices = {"MELON": 1500, "STRAWBERRY": 500, "WHEAT": 120, "CARROT": 150, "TOMATO": 300}
    p = base_prices.get(crop, 100)
    
    revenue = 0
    for i in range(amount):
        revenue += p
        if crop == "MELON":
            # SQ impact: цена падает агрессивно с каждой штукой в батче
            p = max(1, p - 200 * (i + 1)) 
        elif crop in ("STRAWBERRY", "TOMATO"):
            # LINEAR impact
            p = max(1, p - 30)
        else:
            # LOG/SQRT impact
            p = max(1, p * 0.85)
            
    return revenue

def _build_optimal_sell_orders(shed, max_slots):
    """Жадный алгоритм аллокации слотов ордеров."""
    orders = []
    local_shed = dict(shed)
    
    for _ in range(max_slots):
        best_crop, best_amount, best_ev = None, 0, -1
        
        for crop, qty in local_shed.items():
            if qty <= 0: continue
            
            # Проверяем батчи от 1 до 10 штук
            max_test = min(qty, 10)
            for test_amount in range(1, max_test + 1):
                ev = _simulate_ev(crop, test_amount)
                if ev > best_ev:
                    best_ev = ev
                    best_crop = crop
                    best_amount = test_amount
                    
        if best_crop and best_ev > 0:
            orders.append(["SELL", best_crop, best_amount])
            local_shed[best_crop] -= best_amount
        else:
            break
            
    return orders

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

        # === 1. РАЗВЕДКА И ТАЙМИНГ ===
        enemy_melons = _scan_opponent_crops(obs)
        target_harvest_age = CROPS["MELON"]["max_yield_day"]
        target_crop = "MELON"
        
        # Фронтраннинг
        if enemy_melons >= MELON_DANGER_THRESHOLD:
            target_harvest_age = CROPS["MELON"]["first_yield_day"] + 1

        # === 2. РЫНОК (EV Engine) ===
        market = []
        
        # Продажа по EV-модели в часы обновления Town Center
        if hour in (0, 12) and any(qty > 0 for qty in shed.values()):
            # Оставляем слоты под HIRE и BUY_SEED (из 10 доступных)
            slots_for_sales = 8 if day < 26 else 10
            market.extend(_build_optimal_sell_orders(shed, slots_for_sales))

        if seeds.get(target_crop, 0) < 2 and f["money"] >= CROPS[target_crop]["seed"] * 2:
            market.append(["BUY_SEED", target_crop, 2 - seeds.get(target_crop, 0)])

        if hour == 0 and f.get("hires_today", 0) < MAX_HANDS and f["money"] > MIN_MONEY_FOR_HIRE:
            market.append(["HIRE"])

        # === 3. КООРДИНАЦИЯ ===
        units = [tuple(f["farmer"])] + [tuple(h) for h in f.get("hands", [])]
        n_units = len(units)

        tasks = _collect_tasks(f, day, seeds, target_harvest_age, target_crop)
        prio = {"WATER": 0, "HARVEST": 1, "PLANT": 2}
        tasks.sort(key=lambda t: (prio[t[0]], _dist(units[0], (t[1], t[2]))))

        assigned = set()
        actions = [["PASS"] for _ in range(n_units)]

        for i, u_pos in enumerate(units):
            u_inv = invs[i] if i < len(invs) else {}
            inv_total = sum(u_inv.values()) if u_inv else 0

            if u_inv and inv_total >= DROP_THRESHOLD:
                if _shed_adjacent(u_pos, board_size): actions[i] = ["DROP"]
                else: actions[i] = _step(u_pos, _nearest_shed(u_pos, board_size)) or ["PASS"]
                continue

            best_task, best_dist = None, float('inf')
            for task in tasks:
                t_type, tx, ty, t_crop = task
                if (tx, ty) in assigned: continue
                d = _dist(u_pos, (tx, ty))
                if d < best_dist:
                    best_dist = d
                    best_task = task

            if best_task:
                t_type, tx, ty, t_crop = best_task
                assigned.add((tx, ty))
                if u_pos == (tx, ty):
                    if t_type == "WATER": actions[i] = ["WATER"]
                    elif t_type == "HARVEST": actions[i] = ["HARVEST"]
                    elif t_type == "PLANT": actions[i] = ["PLANT", t_crop]
                else: actions[i] = _step(u_pos, (tx, ty)) or ["PASS"]
            else:
                if u_inv:
                    if _shed_adjacent(u_pos, board_size): actions[i] = ["DROP"]
                    else: actions[i] = _step(u_pos, _nearest_shed(u_pos, board_size)) or ["PASS"]
                else: actions[i] = ["PASS"]

        return {"farmer": actions[0], "hands": actions[1:], "market": market}

    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}