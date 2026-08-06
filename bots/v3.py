"""Kaggriculture v3: efficient carrot-only loop."""

CROPS = {
    "CARROT": {"seed": 20, "first_yield_day": 2, "max_yield_day": 3, "max_yield": 4},
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
        
        # Sell all carrots from shed
        if shed.get("CARROT", 0) > 0:
            market.append(["SELL", "CARROT", shed["CARROT"]])
        
        # Buy carrot seeds to maintain stock >= 2
        if seeds.get("CARROT", 0) < 2 and f["money"] >= CROPS["CARROT"]["seed"]:
            market.append(["BUY_SEED", "CARROT", 2 - seeds.get("CARROT", 0)])
        
        # === FARMER ACTION ===
        farmer = ["PASS"]
        
        # If standing on empty tile and have seeds -> plant
        if tile is None and seeds.get("CARROT", 0) > 0:
            farmer = ["PLANT", "CARROT"]
        
        # If standing on carrot plant
        elif isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile["crop"] == "CARROT":
            age = day - tile["planted_day"]
            if age >= CROPS["CARROT"]["max_yield_day"]:
                farmer = ["HARVEST"]
            elif not tile.get("watered_today"):
                farmer = ["WATER"]
            else:
                # Find other plant to water or empty tile to plant
                target = _find_nearest(f, pos, lambda t: 
                    isinstance(t, dict) and t.get("kind") == "PLANT" 
                    and not t.get("watered_today"))
                if target:
                    farmer = _step(pos, target) or ["PASS"]
                else:
                    target = _find_nearest(f, pos, lambda t: t is None)
                    if target and seeds.get("CARROT", 0) > 0:
                        farmer = _step(pos, target) or ["PASS"]
        
        # If have inventory -> go to shed
        elif inv and not shed_adj:
            farmer = _step(pos, _nearest_shed(pos, board_size)) or ["PASS"]
        elif inv and shed_adj:
            farmer = ["DROP"]
        
        # If no seeds -> find plant to water
        elif seeds.get("CARROT", 0) == 0:
            target = _find_nearest(f, pos, lambda t:
                isinstance(t, dict) and t.get("kind") == "PLANT" 
                and not t.get("watered_today"))
            if target:
                farmer = _step(pos, target) or ["PASS"]
        
        # If have seeds -> find empty tile to plant
        elif seeds.get("CARROT", 0) > 0:
            target = _find_nearest(f, pos, lambda t: t is None)
            if target:
                farmer = _step(pos, target) or ["PASS"]
        
        return {"farmer": farmer, "hands": [], "market": market}
    
    except Exception as e:
        return {"farmer": ["PASS"], "hands": [], "market": []}