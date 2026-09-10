"""Kaggriculture v12-working: гусь + melon фронтраннинг."""

def _step(p, t):
    if p[0] < t[0]: return ["EAST"]
    if p[0] > t[0]: return ["WEST"]
    if p[1] < t[1]: return ["SOUTH"]
    if p[1] > t[1]: return ["NORTH"]
    return ["PASS"]

def _dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

def _shed_adjacent(pos):
    return tuple(pos) in [(4,4),(5,4),(4,5),(5,5)]

CROPS = {
    "MELON": {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "max_yield": 6},
}
MELON_DANGER_THRESHOLD = 10

def _scan_opponent_melons(obs):
    count = 0
    player_id = obs["player"]
    for idx, farm_data in enumerate(obs["farms"]):
        if idx == player_id: continue
        for row in farm_data["tiles"]:
            for t in row:
                if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON":
                    count += 1
    return count

def agent(obs):
    try:
        f = obs["farms"][obs["player"]]
        priv = obs.get("private", {}) or {}
        shed = priv.get("shed", {}) or {}
        seeds = priv.get("seeds", {}) or {}
        invs = priv.get("inventories") or [{}]
        inv = invs[0] if invs else {}
        pos = tuple(f["farmer"])
        tiles = f["tiles"]
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        money = f["money"]
        board_size = len(tiles)
        market = []

        # === НАХОДИМ ГУСЯ ===
        goose_pos = None
        goose_tile = None
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("animal") == "GOOSE":
                    goose_pos = (x, y)
                    goose_tile = t
                    break
            if goose_pos: break

        # === НАХОДИМ COOP ===
        coop_pos = None
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("kind") == "COOP":
                    coop_pos = (x, y)
                    break
            if coop_pos: break

        # === РАЗВЕДКА MELON (фронтраннинг) ===
        enemy_melons = _scan_opponent_melons(obs)
        target_harvest_age = CROPS["MELON"]["max_yield_day"]
        if enemy_melons >= MELON_DANGER_THRESHOLD:
            target_harvest_age = CROPS["MELON"]["first_yield_day"] + 1

        # === MARKET ORDERS ===
        if hour in (0, 12):
            # Продажи
            egg_qty = shed.get("EGG", 0)
            if egg_qty > 0:
                market.append(["SELL", "EGG", min(10, egg_qty)])
            
            melon_qty = shed.get("MELON", 0)
            if melon_qty > 0:
                tr = 3 if day >= 25 else 2
                max_orders = 10 if day >= 26 else 8
                while melon_qty > 0 and len(market) < max_orders:
                    n = min(tr, melon_qty)
                    market.append(["SELL", "MELON", n])
                    melon_qty -= n
            
            # Покупка семян melon
            if seeds.get("MELON", 0) < 2 and money >= 160:
                market.append(["BUY_SEED", "MELON", 2 - seeds.get("MELON", 0)])
            
            # Покупка пшеницы для корма гуся
            if shed.get("WHEAT", 0) < 2 and money > 30:
                market.append(["BUY_PRODUCT", "WHEAT", 2])
            
            # Найм батраков для melon
            if hour == 0 and len(f.get("hands", [])) < 4 and money > 100:
                market.append(["HIRE"])

        # === ФЕРМЕР: ОБСЛУЖИВАНИЕ ГУСЯ ===
        if goose_pos is None:
            # Гусь не размещён — размещаем
            if day == 0 and hour == 0 and money >= 300:
                market.append(["BUY_ANIMAL", "GOOSE", 1])
                return {"farmer": ["PASS"], "hands": [["PASS"]]*len(f.get("hands",[])), "market": market}
            
            if shed.get("GOOSE", 0) > 0 and _shed_adjacent(pos):
                return {"farmer": ["PICKUP", "GOOSE", 1], "hands": [["PASS"]]*len(f.get("hands",[])), "market": market}
            
            if coop_pos is None:
                target = (2, 2)
                farmer = ["BUILD_COOP"] if pos == target else _step(pos, target)
            else:
                farmer = ["PLACE", "GOOSE"] if pos == coop_pos else _step(pos, coop_pos)
            
            return {"farmer": farmer, "hands": [["PASS"]]*len(f.get("hands",[])), "market": market}

        # Гусь размещён — кормим и собираем
        needs_feed = not goose_tile.get("fed_today", False)
        
        if needs_feed:
            if inv.get("WHEAT", 0) == 0:
                if shed.get("WHEAT", 0) > 0 and _shed_adjacent(pos):
                    farmer = ["PICKUP", "WHEAT", 3]
                else:
                    farmer = _step(pos, (4,4)) if not _shed_adjacent(pos) else ["PASS"]
            else:
                farmer = _step(pos, goose_pos) if pos != goose_pos else ["FEED"]
        elif goose_tile.get("yield_units", 0) > 0:
            farmer = _step(pos, goose_pos) if pos != goose_pos else ["HARVEST"]
        else:
            farmer = ["PASS"]

        # === БАТРАКИ: MELON ===
        hands = f.get("hands", [])
        hands_actions = [["PASS"] for _ in hands]
        
        if hands:
            # Собираем задачи для melon
            water_tasks = []
            harvest_tasks = []
            plant_tasks = []
            
            for y, row in enumerate(tiles):
                for x, t in enumerate(row):
                    if not isinstance(t, dict): continue
                    if t.get("kind") == "PLANT" and t.get("crop") == "MELON":
                        age = day - t["planted_day"]
                        if age >= target_harvest_age:
                            harvest_tasks.append((x, y))
                        elif not t.get("watered_today"):
                            water_tasks.append((x, y))
                    elif t is None and seeds.get("MELON", 0) > 0 and day < 24:
                        plant_tasks.append((x, y))
            
            all_tasks = water_tasks + harvest_tasks + plant_tasks
            assigned = set()
            
            for i, hand_pos in enumerate(hands):
                hand_pos = tuple(hand_pos)
                hand_inv = invs[i+1] if i+1 < len(invs) else {}
                inv_total = sum(hand_inv.values()) if hand_inv else 0
                
                # DROP если инвентарь полон
                if inv_total >= 8:
                    if _shed_adjacent(hand_pos):
                        hands_actions[i] = ["DROP"]
                    else:
                        hands_actions[i] = _step(hand_pos, (4,4)) or ["PASS"]
                    continue
                
                # Находим ближайшую задачу
                best_task = None
                best_dist = float('inf')
                for tx, ty in all_tasks:
                    if (tx, ty) in assigned: continue
                    d = _dist(hand_pos, (tx, ty))
                    if d < best_dist:
                        best_dist = d
                        best_task = (tx, ty)
                
                if best_task:
                    assigned.add(best_task)
                    tx, ty = best_task
                    if hand_pos == (tx, ty):
                        if (tx, ty) in harvest_tasks:
                            hands_actions[i] = ["HARVEST"]
                        elif (tx, ty) in water_tasks:
                            hands_actions[i] = ["WATER"]
                        else:
                            hands_actions[i] = ["PLANT", "MELON"]
                    else:
                        hands_actions[i] = _step(hand_pos, (tx, ty)) or ["PASS"]
                else:
                    # Нет задач — сброс инвентаря
                    if hand_inv and sum(hand_inv.values()) > 0:
                        if _shed_adjacent(hand_pos):
                            hands_actions[i] = ["DROP"]
                        else:
                            hands_actions[i] = _step(hand_pos, (4,4)) or ["PASS"]

        return {"farmer": farmer, "hands": hands_actions, "market": market}

    except Exception:
        n = len(obs.get("farms", [{}])[obs.get("player", 0)].get("hands", []))
        return {"farmer": ["PASS"], "hands": [["PASS"]]*n, "market": []}