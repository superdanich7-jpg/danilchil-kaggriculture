"""Kaggriculture v8: adaptive mixed-crop (MELON + WHEAT) + opponent scanner."""

CROPS = {
    "MELON": {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "max_yield": 6},
    # ЗАМЕНИ НА ТОЧНЫЕ ЗНАЧЕНИЯ ИЗ ТВОЕГО constants.py ЕСЛИ ОНИ ДРУГИЕ:
    "WHEAT": {"seed": 10, "first_yield_day": 4, "max_yield_day": 5, "max_yield": 2}, 
}

MAX_HANDS = 4
MIN_MONEY_FOR_HIRE = 500
DROP_THRESHOLD = 8
MELON_DANGER_THRESHOLD = 15  # Порог перехода на резервную культуру

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
    """Считает количество посаженных культур у оппонентов."""
    enemy_crops = {}
    player_id = obs["player"]
    for idx, farm_data in enumerate(obs["farms"]):
        if idx == player_id:
            continue
        for row in farm_data["tiles"]:
            for tile in row:
                if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                    crop = tile.get("crop")
                    if crop:
                        enemy_crops[crop] = enemy_crops.get(crop, 0) + 1
    return enemy_crops

def _collect_tasks(f, day, seeds, target_crop):
    """Collect tasks: (type, x, y, crop_type). Priority: WATER > HARVEST > PLANT."""
    tasks = []
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                crop_type = t["crop"]
                age = day - t["planted_day"]
                # Собираем любую культуру, если она достигла макс. урожая
                if crop_type in CROPS and age >= CROPS[crop_type]["max_yield_day"]:
                    tasks.append(("HARVEST", x, y, crop_type))
                elif not t.get("watered_today"):
                    tasks.append(("WATER", x, y, crop_type))
            # Сажаем только выбранную target_crop
            elif t is None and seeds.get(target_crop, 0) > 0 and day < 24:
                tasks.append(("PLANT", x, y, target_crop))
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

        # === 1. РАЗВЕДКА И ВЫБОР СТРАТЕГИИ ===
        enemy_crops = _scan_opponent_crops(obs)
        enemy_melons = enemy_crops.get("MELON", 0)
        
        # Если враг засадил много дынь — уходим в пшеницу
        target_crop = "WHEAT" if enemy_melons >= MELON_DANGER_THRESHOLD else "MELON"

        # === 2. РЫНОК И ОРДЕРА ===
        market = []

        # Продажа Дыни (sq рынок - мелкими траншами)
        if hour in (0, 12) and shed.get("MELON", 0) > 0:
            q = shed["MELON"]
            tr = 3 if day >= 25 else 2
            max_orders_melon = 7  # Оставляем слоты под пшеницу
            orders_done = 0
            while q > 0 and orders_done < max_orders_melon:
                n = min(tr, q)
                market.append(["SELL", "MELON", n])
                q -= n
                orders_done += 1
                
        # Продажа Пшеницы (log рынок - сливаем большими батчами)
        if hour in (0, 12) and shed.get("WHEAT", 0) > 0:
            market.append(["SELL", "WHEAT", shed["WHEAT"]])

        # Покупка семян целевой культуры (поддерживаем запас >= 2)
        if seeds.get(target_crop, 0) < 2 and f["money"] >= CROPS[target_crop]["seed"] * 2:
            market.append(["BUY_SEED", target_crop, 2 - seeds.get(target_crop, 0)])

        # Найм батраков
        if hour == 0 and f.get("hires_today", 0) < MAX_HANDS and f["money"] > MIN_MONEY_FOR_HIRE:
            market.append(["HIRE"])

        # === 3. КООРДИНАЦИЯ (РАЗДАЧА ЗАДАЧ) ===
        units = [tuple(f["farmer"])] + [tuple(h) for h in f.get("hands", [])]
        n_units = len(units)

        tasks = _collect_tasks(f, day, seeds, target_crop)
        prio = {"WATER": 0, "HARVEST": 1, "PLANT": 2}
        tasks.sort(key=lambda t: (prio[t[0]], _dist(units[0], (t[1], t[2]))))

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

            best_task = None
            best_dist = float('inf')
            for task in tasks:
                t_type, tx, ty, t_crop = task
                if (tx, ty) in assigned:
                    continue
                d = _dist(u_pos, (tx, ty))
                if d < best_dist:
                    best_dist = d
                    best_task = task

            if best_task:
                t_type, tx, ty, t_crop = best_task
                assigned.add((tx, ty))
                if u_pos == (tx, ty):
                    if t_type == "WATER":
                        actions[i] = ["WATER"]
                    elif t_type == "HARVEST":
                        actions[i] = ["HARVEST"]
                    elif t_type == "PLANT":
                        actions[i] = ["PLANT", t_crop] # Сажаем конкретную культуру
                else:
                    actions[i] = _step(u_pos, (tx, ty)) or ["PASS"]
            else:
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