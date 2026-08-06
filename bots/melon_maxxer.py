from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS
MELON_SEED_COST = CROPS["MELON"]["seed"]
MELON_MAX_YIELD_DAY = CROPS["MELON"]["max_yield_day"]
SELL_THRESHOLD = 200
def _step_toward(fx, fy, tx, ty):
    if fx > tx: return "WEST"
    if fx < tx: return "EAST"
    if fy > ty: return "NORTH"
    if fy < ty: return "SOUTH"
    return None
def _find_target_tile(farm, board_size, have_seed):
    fx, fy = farm["farmer"]; candidates = []
    for y in range(board_size):
        for x in range(board_size):
            tile = farm["tiles"][y][x]
            if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile["crop"] == "MELON":
                purpose = None
                if tile["yield_units"] > 0 and tile.get("planted_day") is not None: purpose = "harvest"
                if not tile["watered_today"]: purpose = purpose or "water"
                if purpose: candidates.append((x, y, purpose))
            elif tile is None and have_seed: candidates.append((x, y, "plant"))
    if not candidates: return None
    pr = {"harvest": 0, "water": 1, "plant": 2}
    candidates.sort(key=lambda c: (pr[c[2]], abs(c[0]-fx) + abs(c[1]-fy)))
    return candidates[0]
def agent(obs):
    farms = obs.get("farms", []); player = obs.get("player", 0)
    private = obs.get("private", {}) or {}
    if not farms or player >= len(farms):
        return {"farmer": ["PASS"], "hands": [], "market": []}
    farm = farms[player]; board_size = len(farm["tiles"])
    fx, fy = farm["farmer"]; tile = farm["tiles"][fy][fx]; day = obs.get("day", 0)
    seeds = private.get("seeds", {}); shed = private.get("shed", {})
    prices = (obs.get("market", {}) or {}).get("prices", {})
    melon_price = prices.get("MELON", 0); market = []
    if shed.get("MELON", 0) > 0 and melon_price >= SELL_THRESHOLD:
        market.append(["SELL", "MELON", shed["MELON"]])
    if seeds.get("MELON", 0) == 0 and farm["money"] >= MELON_SEED_COST:
        market.append(["BUY_SEED", "MELON", 1])
    farmer = ["PASS"]
    if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile["crop"] == "MELON":
        age = day - tile["planted_day"]
        if age >= MELON_MAX_YIELD_DAY and tile["yield_units"] > 0: farmer = ["HARVEST"]
        elif not tile["watered_today"]: farmer = ["WATER"]
        else:
            t = _find_target_tile(farm, board_size, seeds.get("MELON", 0) > 0)
            if t: farmer = [_step_toward(fx, fy, t[0], t[1])] or farmer
    elif tile is None and seeds.get("MELON", 0) > 0: farmer = ["PLANT", "MELON"]
    else:
        t = _find_target_tile(farm, board_size, seeds.get("MELON", 0) > 0)
        if t: farmer = [_step_toward(fx, fy, t[0], t[1])] or farmer
    return {"farmer": farmer, "hands": [], "market": market}