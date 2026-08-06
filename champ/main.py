"""Kaggriculture v2: упрощённая рабочая версия."""

CROPS = {
    "WHEAT": {"seed": 10, "first_yield_day": 2, "max_yield_day": 4, "max_yield": 6},
    "CARROT": {"seed": 20, "first_yield_day": 2, "max_yield_day": 3, "max_yield": 4},
}
ANIMALS = {
    "GOOSE": {"cost": 300, "product": "EGG", "base_price": 50},
}

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

def _count_animals(f, animal_type):
    count = 0
    for row in f["tiles"]:
        for t in row:
            if isinstance(t, dict) and t.get("animal") == animal_type:
                count += 1
    return count

def _find_nearest(f, pos, condition):
    """Найти ближайший тайл, удовлетворяющий условию."""
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

def agent(obs):
    try:
        f = _farm(obs)
        priv = _priv(obs)
        pos = tuple(f["farmer"])
        tile = f["tiles"][pos[1]][pos[0]]
        day = obs["day"]
        seeds = priv.get("seeds", {}) or {}
        shed = priv.get("shed", {}) or {}
        inv = (priv.get("inventories") or [{}])[0]
        
        board_size = len(f["tiles"])
        shed_adj = _shed_adjacent(pos, board_size)
        
        # === MARKET ORDERS ===
        market = []
        
        # Продаём морковь
        if shed.get("CARROT", 0) > 0:
            market.append(["SELL", "CARROT", shed["CARROT"]])
        
        # Продаём яйца
        if shed.get("EGG", 0) > 0:
            market.append(["SELL", "EGG", shed["EGG"]])
        
        # Покупаем семена моркови
        if seeds.get("CARROT", 0) == 0 and f["money"] >= CROPS["CARROT"]["seed"]:
            market.append(["BUY_SEED", "CARROT", 1])
        
        # Покупаем гусей (максимум 2)
        goose_count = _count_animals(f, "GOOSE")
        if goose_count < 2 and day < 20 and f["money"] >= ANIMALS["GOOSE"]["cost"]:
            market.append(["BUY_ANIMAL", "GOOSE", 1])
        
        # === FARMER ACTION ===
        farmer = ["PASS"]
        
        # Если стоим на пустом тайле и есть семена — сажаем
        if tile is None and seeds.get("CARROT", 0) > 0:
            farmer = ["PLANT", "CARROT"]
        
        # Если стоим на растении моркови
        elif isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile["crop"] == "CARROT":
            age = day - tile["planted_day"]
            if age >= CROPS["CARROT"]["max_yield_day"]:
                farmer = ["HARVEST"]
            elif not tile.get("watered_today"):
                farmer = ["WATER"]
            else:
                # Ищем другое растение для полива
                target = _find_nearest(f, pos, lambda t: 
                    isinstance(t, dict) and t.get("kind") == "PLANT" 
                    and not t.get("watered_today"))
                if target:
                    farmer = _step(pos, target) or ["PASS"]
                else:
                    # Ищем пустой тайл для посадки
                    target = _find_nearest(f, pos, lambda t: t is None)
                    if target and seeds.get("CARROT", 0) > 0:
                        farmer = _step(pos, target) or ["PASS"]
        
        # Если стоим на гусе и есть пшеница — кормим
        elif isinstance(tile, dict) and tile.get("animal") == "GOOSE":
            if not tile.get("fed_today") and (inv.get("WHEAT") or 0) > 0:
                farmer = ["FEED"]
            elif (tile.get("yield_units") or 0) > 0:
                farmer = ["HARVEST"]
            else:
                # Ищем другое животное для ухода
                target = _find_nearest(f, pos, lambda t:
                    isinstance(t, dict) and t.get("animal") and not t.get("fed_today"))
                if target and (inv.get("WHEAT") or 0) > 0:
                    farmer = _step(pos, target) or ["PASS"]
                elif inv and not shed_adj:
                    # Идём к сараю для DROP
                    farmer = _step(pos, _nearest_shed(pos, board_size)) or ["PASS"]
                elif inv and shed_adj:
                    farmer = ["DROP"]
        
        # Если стоим на пустом COOP и есть гусь в инвентаре — размещаем
        elif isinstance(tile, dict) and tile.get("kind") == "COOP" and not tile.get("animal"):
            if (inv.get("GOOSE") or 0) > 0:
                farmer = ["PLACE", "GOOSE"]
            elif shed.get("GOOSE", 0) > 0 and shed_adj:
                farmer = ["PICKUP", "GOOSE", 1]
            elif shed.get("GOOSE", 0) > 0 and not shed_adj:
                farmer = _step(pos, _nearest_shed(pos, board_size)) or ["PASS"]
        
        # Если есть продукт в инвентаре — идём к сараю
        elif inv and not shed_adj:
            farmer = _step(pos, _nearest_shed(pos, board_size)) or ["PASS"]
        elif inv and shed_adj:
            farmer = ["DROP"]
        
        # Если нет гусей в сарае и есть деньги — ищем пустой тайл для BUILD_COOP
        elif shed.get("GOOSE", 0) > 0 and goose_count < 2:
            coop_count = sum(1 for row in f["tiles"] for t in row 
                           if isinstance(t, dict) and t.get("kind") == "COOP")
            if coop_count <= goose_count:
                target = _find_nearest(f, pos, lambda t: t is None)
                if target:
                    if _dist(pos, target) == 0:
                        farmer = ["BUILD_COOP"]
                    else:
                        farmer = _step(pos, target) or ["PASS"]
        
        # Ищем растение для полива
        elif seeds.get("CARROT", 0) == 0:
            target = _find_nearest(f, pos, lambda t:
                isinstance(t, dict) and t.get("kind") == "PLANT" 
                and not t.get("watered_today"))
            if target:
                farmer = _step(pos, target) or ["PASS"]
        
        # Ищем пустой тайл для посадки
        elif seeds.get("CARROT", 0) > 0:
            target = _find_nearest(f, pos, lambda t: t is None)
            if target:
                farmer = _step(pos, target) or ["PASS"]
        
        return {"farmer": farmer, "hands": [], "market": market}
    
    except Exception as e:
        return {"farmer": ["PASS"], "hands": [], "market": []}