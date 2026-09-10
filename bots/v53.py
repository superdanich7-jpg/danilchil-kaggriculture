"""Kaggriculture v49: iter35 + straw limit 15 (compromise).
Animals from day 0 (fertilizer/wool/milk engine), melon bridge -> strawberry
rotation after day 12, land on days 5-10, wheat bought for feed, small tranches."""

MAX_HANDS = 6
FEED_RESERVE = 250      # ITER33: coins reserved ONLY for animal feed wheat
_BLOCKED = {"n": 0}     # diagnostics: blocked discretionary spends


def _can_spend(money, price):
    """Allow a discretionary spend only if the feed reserve survives."""
    if money - price < FEED_RESERVE:
        _BLOCKED["n"] += 1
        return False
    return True
DROP_THRESHOLD = 6
MELON_DANGER_THRESHOLD = 10
FERT_RESERVE = 8        # keep fertilizer for strawberry doubling from day 10
WHEAT_FEED_MIN = 4
STRAW_PROD_AGES = (10, 12, 14, 16)

# reserved pasture build spots, in build order — ALWAYS adjacent to the shed
# so a feed trip (pickup -> walk -> FEED) takes ~3 turns, not 18.
PASTURE_SPOTS = [
    # NW (unlocked at start), closest ring around shed (4,4)-(5,5)
    (3, 3), (4, 3), (3, 4), (3, 2), (2, 3),
    # NE (after 1st BUY_LAND), closest ring
    (5, 3), (6, 4), (6, 3), (7, 4), (6, 2),
    # SW (after 2nd BUY_LAND)
    (3, 5), (4, 6), (3, 6), (2, 5), (4, 7),
    # SE (after 3rd BUY_LAND)
    (6, 5), (6, 6), (7, 5), (5, 6),
]
_RESERVED = set(PASTURE_SPOTS)


def _farm(o):
    return o["farms"][o["player"]]


def _priv(o):
    return o.get("private", {}) or {}


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _step(p, t):
    if p[0] < t[0]: return ["EAST"]
    if p[0] > t[0]: return ["WEST"]
    if p[1] < t[1]: return ["SOUTH"]
    if p[1] > t[1]: return ["NORTH"]
    return None


def _shed_adjacent(pos, board_size=10):
    half = board_size // 2
    return tuple(pos) in [(half - 1, half - 1), (half, half - 1),
                          (half - 1, half), (half, half)]


def _nearest_shed(pos, board_size=10):
    half = board_size // 2
    access = [(half - 1, half - 1), (half, half - 1),
              (half - 1, half), (half, half)]
    return min(access, key=lambda p: _dist(pos, p))


def _go_drop(u):
    return ["DROP"] if _shed_adjacent(u) else (_step(u, _nearest_shed(u)) or ["PASS"])


def _find_animals(tiles):
    return [((x, y), t) for y, row in enumerate(tiles) for x, t in enumerate(row)
            if isinstance(t, dict) and t.get("kind") in ("PASTURE", "COOP")
            and t.get("animal")]


def _free_structures(tiles):
    return [((x, y), t) for y, row in enumerate(tiles) for x, t in enumerate(row)
            if isinstance(t, dict) and t.get("kind") in ("PASTURE", "COOP")
            and t.get("animal") is None]


def _next_pasture_spot(tiles):
    for (x, y) in PASTURE_SPOTS:
        t = tiles[y][x]
        if t == "LOCKED" or t is None:
            return (x, y)
    return None


def _scan_opponent_crops(obs, crop="MELON"):
    pid = obs["player"]
    n = 0
    for idx, fd in enumerate(obs["farms"]):
        if idx == pid:
            continue
        for row in fd["tiles"]:
            for t in row:
                if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == crop:
                    n += 1
    return n


def _pick_crop(day, seeds, counts, melon_quota, allow_straw=True, wheat_quota=6):
    s = seeds.get("STRAWBERRY", 0)
    m = seeds.get("MELON", 0)
    w = seeds.get("WHEAT", 0)
    # wheat first: animal feed security (animals die without it);
    # wheat matures in 4d -> worth planting until ~day 25
    if w > 0 and counts.get("WHEAT", 0) < wheat_quota and day <= 25:
        return "WHEAT"
    # ITER35 P1: strawberry BEFORE melon - a tile freed by DIG/HARVEST must
    # return to the strawberry engine, otherwise the "dead replant loop"
    # bleeds the engine dry while melon floods the shared market
    # (replay fact: our own melon dump drove MELON price to 7).
    # Strawberry yields at ages 10,12,14,16 then decays: planted day 19
    # still yields on day 29, so day 19 is the hard planting cutoff.
    if s > 0 and allow_straw and day <= 19 and counts.get("STRAWBERRY", 0) < 16:
        return "STRAWBERRY"
    # ITER24: melon planted after day 17 matures after day 29 - pure seed waste
    if m > 0 and counts.get("MELON", 0) < melon_quota and day < 18:
        return "MELON"
    return None


def _crop_pool(f, day, seeds, harvest_age, have_fert, melon_quota, allow_straw,
               wheat_quota=6):
    """WATER > HARVEST > FERTILIZE > PLANT > DIG over unlocked tiles."""
    tasks = []
    digs = 0
    # ITER35 FIX: exact crop counts. The old single-pass scan counted only
    # tiles BEFORE the current scan position, so every quota was silently
    # 1.5-2x looser than intended: "quota 13" actually planted ~25 melon
    # tiles (replay fact: 25 melons -> self-flood -> MELON price 7) and
    # starved the strawberry cycle of tiles. Two passes: count, then plan.
    counts = {"MELON": 0, "WHEAT": 0, "STRAWBERRY": 0}
    for row in f["tiles"]:
        for t in row:
            if isinstance(t, dict) and t.get("kind") == "PLANT" \
                    and t.get("crop") in counts:
                counts[t["crop"]] += 1
    for y, row in enumerate(f["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                crop = t.get("crop")
                age = day - t.get("planted_day", day)
                if crop == "MELON":
                    if age >= harvest_age:
                        tasks.append(("HARVEST", x, y, None))
                    elif not t.get("watered_today"):
                        tasks.append(("WATER", x, y, None))
                elif crop == "WHEAT":
                    if age >= 4:
                        tasks.append(("HARVEST", x, y, None))
                    elif not t.get("watered_today"):
                        tasks.append(("WATER", x, y, None))
                elif crop == "STRAWBERRY":
                    if t.get("yield_units", 0) > 0:
                        tasks.append(("HARVEST", x, y, None))
                    elif age >= 18:
                        tasks.append(("DIG", x, y, None))
                    elif ((age + 1) in STRAW_PROD_AGES
                          and t.get("fertilized_until_day", -1) < day + 1
                          and have_fert):
                        tasks.append(("FERTILIZE", x, y, None))
                    elif not t.get("watered_today"):
                        tasks.append(("WATER", x, y, None))
            elif isinstance(t, dict) and t.get("kind") == "WEED":
                if digs < 5:  # ITER34 P0: cap weed clearing per day
                    tasks.append(("DIG", x, y, None))
                    digs += 1
            elif t is None and (x, y) not in _RESERVED:
                c = _pick_crop(day, seeds, counts, melon_quota, allow_straw,
                               wheat_quota)
                if c:
                    counts[c] = counts.get(c, 0) + 1
                    tasks.append(("PLANT", x, y, c))
    return tasks


def _assign_nearest(pos, tasks, assigned):
    best = None
    bd = 1 << 30
    for tk in tasks:
        key = (tk[1], tk[2])
        if key in assigned:
            continue
        d = _dist(pos, key)
        if d < bd:
            bd = d
            best = tk
    if best is None:
        return None
    verb, x, y, arg = best
    assigned.add((x, y))
    if tuple(pos) == (x, y):
        if verb == "PLANT":
            return ["PLANT", arg]
        return [verb]
    return _step(pos, (x, y)) or ["PASS"]


def _animal_crew(idx, k, u, inv, f, shed, placement_first):
    """Placement + daily care. While animals are still in the shed, the
    care hand covers ALL placed animals (survival first); placement hands
    keep placing. After placement completes, care is split modulo k."""
    tiles = f["tiles"]
    in_shed = shed.get("COW", 0) + shed.get("SHEEP", 0)

    def care_task(cover_all):
        anims = _find_animals(tiles)
        if not anims:
            return None
        if cover_all:
            mine = list(anims)
        else:
            mine = [a for j, a in enumerate(anims) if j % k == idx % k]
        if not mine:
            return None
        mine.sort(key=lambda at: (-at[1].get("consecutive_unfed", 0),
                                  not at[1].get("fed_today", False)))
        # wheat logistics only for the FEED part
        need_feed = any(not t.get("fed_today") for _, t in mine)
        if need_feed and inv.get("WHEAT", 0) == 0 and shed.get("WHEAT", 0) > 0:
            if _shed_adjacent(u):
                return ["PICKUP", "WHEAT", 4]
            return _step(u, _nearest_shed(u)) or ["PASS"]
        for (apos, t) in mine:
            if tuple(u) == tuple(apos):
                if not t.get("fed_today") and inv.get("WHEAT", 0) > 0:
                    return ["FEED"]
                if t.get("fertilizer_available"):
                    return ["COLLECT_FERTILIZER"]
                if not t.get("cared_today"):
                    return ["CARE"]
                if t.get("yield_units", 0) > 0:
                    return ["HARVEST"]
            else:
                busy = (not t.get("fed_today") or t.get("fertilizer_available")
                        or not t.get("cared_today") or t.get("yield_units", 0) > 0)
                if busy:
                    return _step(u, apos) or ["PASS"]
        # emergency cross-feed: an animal at consecutive_unfed>=1 escapes
        # tonight even if it is not in this hand's split
        for (apos, t) in anims:
            if t.get("consecutive_unfed", 0) >= 1 and not t.get("fed_today"):
                if inv.get("WHEAT", 0) > 0:
                    if tuple(u) == tuple(apos):
                        return ["FEED"]
                    return _step(u, apos) or ["PASS"]
                if shed.get("WHEAT", 0) > 0:
                    if _shed_adjacent(u):
                        return ["PICKUP", "WHEAT", 4]
                    return _step(u, _nearest_shed(u)) or ["PASS"]
        return None

    def _build_or_walk():
        spot = _next_pasture_spot(tiles)
        if spot is None:
            return None
        if tuple(u) == spot:
            return ["BUILD_PASTURE"]
        return _step(u, spot) or ["PASS"]

    def placement_task(force, allow_pickup=True):
        if not force and in_shed <= 0:
            return None
        carrying = inv.get("COW", 0) + inv.get("SHEEP", 0)
        if carrying > 0:
            free = _free_structures(tiles)
            if free:
                tgt = min(free, key=lambda pt: _dist(u, pt[0]))
                if tuple(u) == tuple(tgt[0]):
                    return ["PLACE", "COW"] if inv.get("COW", 0) > 0 else ["PLACE", "SHEEP"]
                return _step(u, tgt[0]) or ["PASS"]
            # carrying an animal but no free pasture: build one NOW
            return _build_or_walk()
        if not allow_pickup:
            return None
        if _free_structures(tiles):
            # never grab another animal while pastures may run out mid-trip
            if _shed_adjacent(u):
                if shed.get("COW", 0) > 0:
                    return ["PICKUP", "COW", 1]
                if shed.get("SHEEP", 0) > 0:
                    return ["PICKUP", "SHEEP", 1]
                return None
            return _step(u, _nearest_shed(u)) or ["PASS"]
        return _build_or_walk()

    # a hand holding an animal must ALWAYS deliver it first (inventory is
    # otherwise blocked -> it can neither feed nor pick up wheat)
    if inv.get("COW", 0) + inv.get("SHEEP", 0) > 0:
        return placement_task(True) or care_task(False)
    if in_shed > 0:
        if placement_first:
            return placement_task(False)
        # care hand: never grab animals - feeding has absolute priority
        return care_task(True) or placement_task(False, allow_pickup=False)
    return care_task(False) or placement_task(False)


def _scan_opponent_animals(obs):
    pid = obs["player"]
    n = 0
    for idx, fd in enumerate(obs["farms"]):
        if idx == pid:
            continue
        for row in fd["tiles"]:
            for t in row:
                if isinstance(t, dict) and t.get("animal"):
                    n += 1
    return n


# ITER23: irreversible mode latch (reset at day 0 of each episode)
_MODE_DIV = {"on": False}


# ===== AGENT =====
def agent(obs):
    try:
        f = _farm(obs)
        priv = _priv(obs)
        day = obs["day"]
        hour = obs.get("hour", 0)
        seeds = priv.get("seeds", {}) or {}
        shed = priv.get("shed", {}) or {}
        invs = priv.get("inventories") or [{}]
        money = f["money"]
        quads = f.get("unlocked_quadrants") or ["NW"]
        units = [tuple(f["farmer"])] + [tuple(h) for h in f.get("hands", [])]
        n = len(units)
        tiles = f["tiles"]
        anims = _find_animals(tiles)
        herd = len(anims)
        in_shed = shed.get("COW", 0) + shed.get("SHEEP", 0)
        if herd <= 4:
            n_anim_hands = 2
        elif herd <= 9:
            n_anim_hands = 3
        else:
            n_anim_hands = 4  # ITER35: was 5 - 17-18 animals starved the crop
            # engine of labor (3 crop units for ~50 tasks = ~1 planting/day)
        enemy_melons = _scan_opponent_crops(obs)
        enemy_straw = _scan_opponent_crops(obs, "STRAWBERRY")
        enemy_anim = _scan_opponent_animals(obs)
        harvest_age = 11 if enemy_melons >= MELON_DANGER_THRESHOLD else 12
        # ITER24: endgame pull-forward - harvest wave-2 at age 10 (yield cap
        # already reached) so it gets SOLD before the season ends
        if day >= 26:
            harvest_age = min(harvest_age, 10)
        # ITER23: irreversible latch - once the opponent shows melon flooding,
        # strawberries>=6 or animals>=8, stay diversified for the whole game
        if day == 0:
            _MODE_DIV["on"] = False
        if (enemy_melons >= MELON_DANGER_THRESHOLD or enemy_straw >= 6
                or enemy_anim >= 8):
            _MODE_DIV["on"] = True
        melon_mode = not _MODE_DIV["on"]
        melon_quota = 20 if melon_mode else 13
        wheat_quota = 6 if melon_mode else 12
        # ITER35: div herd cap 20 -> 12. Replay fact: ladder winners run 12-14
        # animals; our 17-18 burned cash + 5 hands of labor daily while the
        # strawberry cycle (the actual point of diversification) collapsed.
        herd_cap = 8 if melon_mode else 12
        if melon_mode:
            n_anim_hands = min(n_anim_hands, 3)  # keep hands on melon
        feed_need = max(WHEAT_FEED_MIN, herd)

        market = []
        # --- SELL every hour (throughput!), revenue-priority tranches ---
        # ITER24: two aggressiveness tracks - stable-price goods (wool/milk/
        # straw/fert/wheat) are salvaged hard from day 25 (pure win), while
        # MELON keeps normal tranches until d28 (quadratic price: early dump
        # destroys our own revenue) and gets the x5 nuke on day 29 only
        big_stable = 3 if day >= 25 else 1
        big_melon = 5 if day >= 29 else (2 if day >= 28 else 1)
        # ITER24: on day 29 sell the ENTIRE remaining stock (no tranche caps)
        full_dump = day >= 29
        if shed.get("WOOL", 0) > 0:
            market.append(["SELL", "WOOL", shed["WOOL"] if full_dump
                           else min(6 * big_stable, shed["WOOL"])])
        if shed.get("MILK", 0) > 0:
            market.append(["SELL", "MILK", shed["MILK"] if full_dump
                           else min(8 * big_stable, shed["MILK"])])
        if shed.get("STRAWBERRY", 0) > 0:
            market.append(["SELL", "STRAWBERRY", shed["STRAWBERRY"] if full_dump
                           else min(8 * big_stable, shed["STRAWBERRY"])])
        if day >= 12 and shed.get("MELON", 0) > 0:
            market.append(["SELL", "MELON", shed["MELON"] if full_dump
                           else min(10 * big_melon, shed["MELON"])])
        fert_res = 0 if (day < 10 or melon_mode or day >= 27) else FERT_RESERVE
        fv = shed.get("FERTILIZER", 0) - fert_res
        if fv > 0:
            market.append(["SELL", "FERTILIZER", fv if full_dump
                           else min(8 * big_stable, fv)])
        # wheat surplus: keep only near-term feed stock, sell the rest
        wv = shed.get("WHEAT", 0) - ((feed_need + 4) if day < 29 else 0)
        if wv > 0:
            market.append(["SELL", "WHEAT", wv if full_dump
                           else min(10 * big_stable, wv)])
        # --- HIRE (labor is nearly free: fib 1+1+2+3+5+8=20/day) ---
        # fib-gated: even a nearly-broke farm affords 2 hands (1+1 coins) -
        # losing ALL hands means animals starve and the farm collapses
        # ITER30: hire up to 7 hands once the herd reaches 5 (service capacity)
        max_hands_today = 9 if herd >= 5 else MAX_HANDS
        n_hired = f.get("hires_today", 0)
        fib_cost = (1, 1, 2, 3, 5, 8, 13, 21)[min(n_hired, 7)]
        if n_hired < max_hands_today and money > fib_cost:
            market.append(["HIRE"])
        # --- day-0 bootstrap: animals + bridge seeds + starter feed ---
        if day == 0 and hour == 0 and seeds.get("MELON", 0) == 0:
            market += [["BUY_ANIMAL", "COW", 1], ["BUY_ANIMAL", "SHEEP", 1],
                       ["BUY_SEED", "MELON", 3], ["BUY_SEED", "WHEAT", 4],
                       ["BUY_PRODUCT", "WHEAT", 4]]
        # --- seed top-ups (ITER33: gated by feed reserve) ---
        if melon_mode:
            if seeds.get("MELON", 0) < 4 and _can_spend(money, 330):
                market.append(["BUY_SEED", "MELON", 4])
        else:
            # ITER35 P1: strawberry engine at scale. Replay fact: winners run
            # 30+ straw tiles by d12 (bought 2-16 seeds/day), we were
            # throttled to 2 seeds/day and sold 27 vs their 168. Buy as many
            # as the feed reserve safely allows (1-6) so mid-game cash dips
            # don't stall the replant cycle; window d4-d19 (d19 still yields
            # on day 29, later planting never yields).
            if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 12:
                n_straw = min(6, int((money - FEED_RESERVE) // 100))
                if n_straw >= 1:
                    market.append(["BUY_SEED", "STRAWBERRY", n_straw])
            if day < 11 and seeds.get("MELON", 0) < 1 and _can_spend(money, 150):
                market.append(["BUY_SEED", "MELON", 2])
        # --- feed logistics: PRIORITY - no reserve applies (ITER33) ---
        if day < 29 and (herd > 0 or in_shed > 0) \
                and shed.get("WHEAT", 0) < feed_need \
                and money >= 45 * min(10, max(2, herd)):
            market.append(["BUY_PRODUCT", "WHEAT", min(10, max(2, herd))])
        # --- land: gated by feed reserve (ITER33) ---
        if len(quads) == 1 and day >= 5 and in_shed == 0 \
                and _can_spend(money, 1000):
            market.append(["BUY_LAND"])
        if len(quads) == 2 and _can_spend(money, 2000):
            market.append(["BUY_LAND"])
        if len(quads) == 3 and not melon_mode and _can_spend(money, 4000):
            market.append(["BUY_LAND"])
        # cow needs 8 days to first milk, so cows after d16 never repay.
        # Sheep carry the late window (first wool at +6d). Small herd wins:
        # capital + feed burn beat marginal output vs weak opponents. ---
        if 9 <= day <= 22 and herd < herd_cap and in_shed == 0 and money > 900 \
                and shed.get("WHEAT", 0) >= 2:
            n_sh = sum(1 for _, t in anims if t.get("animal") == "SHEEP")
            n_cow = sum(1 for _, t in anims if t.get("animal") == "COW")
            if n_cow < 8 and day <= 16 and _can_spend(money, 400):
                market.append(["BUY_ANIMAL", "COW", 1])
                if money - 800 >= FEED_RESERVE and n_cow < 7:
                    market.append(["BUY_ANIMAL", "COW", 1])
            elif n_sh < 10 and _can_spend(money, 500):
                market.append(["BUY_ANIMAL", "SHEEP", 1])
                if money - 1000 >= FEED_RESERVE and n_sh < 9:
                    market.append(["BUY_ANIMAL", "SHEEP", 1])
        market = market[:10]

        have_fert = shed.get("FERTILIZER", 0) > 0
        pool = _crop_pool(f, day, seeds, harvest_age, have_fert,
                          melon_quota, allow_straw=not melon_mode,
                          wheat_quota=wheat_quota)
        assigned = set()
        actions = [["PASS"] for _ in range(n)]
        for i, u in enumerate(units):
            inv = invs[i] if i < len(invs) else {}
            it = sum(v for v in inv.values() if isinstance(v, (int, float)))
            # hands carry wheat as animal feed - wheat should not force a drop
            it_drop = it - (inv.get("WHEAT", 0) if i > 0 else 0)
            if it_drop >= DROP_THRESHOLD:
                actions[i] = _go_drop(u)
                continue
            # ITER30: hands 1-2 are DEDICATED to animals (never switch to
            # crops) - stable service route beats crop fallback churn
            if 0 < i <= n_anim_hands and n > 1:
                a = _animal_crew(i - 1, n_anim_hands, u, inv, f, shed,
                                 placement_first=(i % 2 == 1))
                if a:
                    actions[i] = a
                    continue
                if herd > 0 and i <= 2:
                    actions[i] = ["PASS"]  # stay on animal duty
                    continue
            actions[i] = _assign_nearest(u, pool, assigned) or ["PASS"]

        return {"farmer": actions[0], "hands": actions[1:], "market": market}
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}