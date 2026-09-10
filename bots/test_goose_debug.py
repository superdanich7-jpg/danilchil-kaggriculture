def _step(p, t):
    if p[0] < t[0]: return ["EAST"]
    if p[0] > t[0]: return ["WEST"]
    if p[1] < t[1]: return ["SOUTH"]
    if p[1] > t[1]: return ["NORTH"]
    return ["PASS"]

def agent(obs):
    try:
        f = obs["farms"][obs["player"]]
        priv = obs.get("private", {}) or {}
        shed = priv.get("shed", {}) or {}
        inv = (priv.get("inventories") or [{}])[0]
        pos = tuple(f["farmer"])
        tiles = f["tiles"]
        market = []
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)

        has_goose = any(isinstance(t, dict) and t.get("animal") == "GOOSE"
                        for row in tiles for t in row)
        goose_in_inv = inv.get("GOOSE", 0) > 0
        goose_in_shed = shed.get("GOOSE", 0) > 0
        empty_coop = None
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("kind") == "COOP" and not t.get("animal"):
                    empty_coop = (x, y)

        # Логируем состояние
        print(f"DEBUG day={day} hour={hour} money={f['money']} pos={pos}")
        print(f"  has_goose={has_goose} goose_in_inv={goose_in_inv} goose_in_shed={goose_in_shed} empty_coop={empty_coop}")
        print(f"  inv={inv} shed={shed}")

        if has_goose:
            farmer = ["PASS"]
            print("  ACTION: PASS (goose already placed)")
        elif goose_in_inv:
            if empty_coop:
                farmer = ["PLACE", "GOOSE"] if pos == empty_coop else _step(pos, empty_coop)
                print(f"  ACTION: PLACE_GOOSE or MOVE to {empty_coop}")
            else:
                tgt = (2, 2)
                farmer = ["BUILD_COOP"] if pos == tgt else _step(pos, tgt)
                print(f"  ACTION: BUILD_COOP or MOVE to {tgt}")
        elif goose_in_shed:
            farmer = ["PICKUP", "GOOSE", 1] if pos in [(4,4),(5,4),(4,5),(5,5)] else _step(pos, (4,4))
            print(f"  ACTION: PICKUP_GOOSE or MOVE to shed")
        else:
            if f["money"] > 400:
                market.append(["BUY_ANIMAL", "GOOSE", 1])
                print("  ACTION: BUY_ANIMAL")
            else:
                print("  ACTION: PASS (no money)")
            farmer = ["PASS"]

        print(f"  market={market} farmer={farmer}")
        return {"farmer": farmer, "hands": [], "market": market}
    except Exception as e:
        print(f"ERROR: {e}")
        return {"farmer": ["PASS"], "hands": [], "market": []}