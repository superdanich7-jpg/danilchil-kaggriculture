"""Kaggriculture ШАГ A: гусь + FEED (минимальный рабочий цикл)."""

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
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        money = f["money"]
        market = []

        # Находим гуся на поле
        goose_pos = None
        goose_tile = None
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("animal") == "GOOSE":
                    goose_pos = (x, y)
                    goose_tile = t
                    break
            if goose_pos:
                break

        # Находим COOP (если ещё не построен)
        coop_pos = None
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("kind") == "COOP":
                    coop_pos = (x, y)
                    break
            if coop_pos:
                break

        # Если гуся нет — покупаем и размещаем
        if goose_pos is None:
            # 1. BUY_ANIMAL GOOSE (только day 0, hour 0)
            if day == 0 and hour == 0 and money >= 300:
                market.append(["BUY_ANIMAL", "GOOSE", 1])
                return {"farmer": ["PASS"], "hands": [], "market": market}

            # 2. PICKUP GOOSE из сарая
            if shed.get("GOOSE", 0) > 0 and pos in [(4,4),(5,4),(4,5),(5,5)]:
                return {"farmer": ["PICKUP", "GOOSE", 1], "hands": [], "market": market}

            # 3. BUILD_COOP
            if coop_pos is None:
                target = (2, 2)  # фиксированная позиция для COOP
                if pos == target:
                    return {"farmer": ["BUILD_COOP"], "hands": [], "market": market}
                else:
                    return {"farmer": _step(pos, target), "hands": [], "market": market}

            # 4. PLACE GOOSE
            if coop_pos and pos == coop_pos:
                return {"farmer": ["PLACE", "GOOSE"], "hands": [], "market": market}
            elif coop_pos:
                return {"farmer": _step(pos, coop_pos), "hands": [], "market": market}

        # Гусь размещён — FEED цикл
        if goose_pos and goose_tile:
            # FEED критичен — приоритет выше всего
            # Проверяем нужно ли кормить
            needs_feed = not goose_tile.get("fed_today", False)

            if needs_feed:
                # Нужна пшеница в инвентаре
                if inv.get("WHEAT", 0) == 0:
                    # Пытаемся купить пшеницу (если денег > 30)
                    if money > 30 and shed.get("WHEAT", 0) == 0:
                        market.append(["BUY_PRODUCT", "WHEAT", 1])
                    # Или PICKUP из сарая
                    elif shed.get("WHEAT", 0) > 0 and pos in [(4,4),(5,4),(4,5),(5,5)]:
                        return {"farmer": ["PICKUP", "WHEAT", 1], "hands": [], "market": market}
                    # Идём к сараю
                    elif pos not in [(4,4),(5,4),(4,5),(5,5)]:
                        return {"farmer": _step(pos, (4,4)), "hands": [], "market": market}
                    else:
                        return {"farmer": ["PASS"], "hands": [], "market": market}

                # Есть пшеница — идём к гусю и кормим
                if pos != goose_pos:
                    return {"farmer": _step(pos, goose_pos), "hands": [], "market": market}
                else:
                    return {"farmer": ["FEED"], "hands": [], "market": market}

            # Гусь накормлен — проверяем яйца
            if goose_tile.get("yield_units", 0) > 0:
                # HARVEST
                if pos != goose_pos:
                    return {"farmer": _step(pos, goose_pos), "hands": [], "market": market}
                else:
                    return {"farmer": ["HARVEST"], "hands": [], "market": market}

            # GUard: если инвентарь полон — идём сбрасывать
            if sum(inv.values()) >= 8:
                if pos in [(4,4),(5,4),(4,5),(5,5)]:
                    return {"farmer": ["DROP"], "hands": [], "market": market}
                else:
                    return {"farmer": _step(pos, (4,4)), "hands": [], "market": market}

        # Если ничего не нужно — PASS
        return {"farmer": ["PASS"], "hands": [], "market": market}

    except Exception as e:
        return {"farmer": ["PASS"], "hands": [], "market": []}