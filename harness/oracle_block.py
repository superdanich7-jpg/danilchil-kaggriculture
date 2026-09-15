# ============================================================
# ORACLE layer: exact price-projection sell timing.
# Market is a closed ledger: inventory changes only via player
# commits and town consumption (no replenishment). Price = exact
# formula of inventory. Town shop schedule is visible. Therefore
# the future price path is computable: defer glut sales into the
# shop-driven recovery, sell scarcity goods immediately.
# ============================================================
import math as _orcl_math

_ORCL_I0 = 10000
_ORCL_PARAMS = {
    "WHEAT":      {"base":  25, "T": 400, "bf": "sqrt",  "bt": 0.80, "af": "log",   "at": 0.20},
    "CARROT":     {"base":  35, "T": 450, "bf": "hinge", "bt": 1.00, "af": "sqrt",  "at": 0.70},
    "TOMATO":     {"base":  60, "T": 200, "bf": "hinge", "bt": 0.40, "af": "sqrt",  "at": 0.60},
    "STRAWBERRY": {"base": 120, "T": 100, "bf": "sqrt",  "bt": 0.70, "af": "linear","at": 1.60},
    "MELON":      {"base": 250, "T": 300, "bf": "log",   "bt": 0.20, "af": "sq",    "at": 3.60},
    "EGG":        {"base":  50, "T": 332, "bf": "hinge", "bt": 0.40, "af": "log",   "at": 0.20},
    "MILK":       {"base": 160, "T": 122, "bf": "sqrt",  "bt": 0.60, "af": "linear","at": 1.60},
    "WOOL":       {"base": 200, "T": 105, "bf": "log",   "bt": 0.20, "af": "sq",    "at": 3.20},
    "FERTILIZER": {"base": 100, "T": 200, "bf": "linear","bt": 0.40, "af": "linear","at": 0.40},
}
_ORCL_SHOPS = {
    "BAKERY": ["EGG", "WHEAT"], "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"],
    "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"], "YARN_STORE": ["WOOL"],
    "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"], "PET_CAFE": ["CARROT"],
    "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"],
    "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}
_ORCL_STATE = {}
_ORCL_REPORT = {"orcl_defers": 0, "orcl_reissues": 0, "orcl_forced": 0,
                "orcl_kept_scarcity": 0, "orcl_kept_weak_gain": 0, "orcl_errors": 0}
_ORCL_MIN_QTY = 12
_ORCL_MIN_GAIN = 0.12
_ORCL_ISSUE_FRAC = 0.93
_ORCL_MAX_WAIT = 4
_ORCL_PEND_CAP = 30
_ORCL_FORCE_STEP = 648
_ORCL_NO_DEFER_GOODS = {"WHEAT", "MILK", "EGG"}


def _orcl_gate(obs):
    """Defer only when the opponent demonstrably dumped into this market."""
    try:
        player = int(obs["player"])
        step = int(obs["step"])
        if step < 96 or step > 624:  # d5..d26 window only
            return False
        inv = obs["market"]["inventory"]
        hist = _ORCL_STATE.get(player, {}).get("inv_hist")
        if hist is None:
            return False
        prev = hist.get("inv") or {}
        for good, now in inv.items():
            delta = int(now) - int(prev.get(good, now))
            if delta >= 60:  # someone mass-dumped this turn pair
                return True
        return False
    except Exception:
        return False


def _orcl_shape(func, x, T):
    x = x if x > 0.0 else 0.0
    if func == "linear":
        return x
    if func == "sq":
        return x * x
    if func == "sqrt":
        return _orcl_math.sqrt(x)
    if func == "log":
        return _orcl_math.log(1.0 + x)
    if func == "hinge":
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def _orcl_price(item, inv):
    p = _ORCL_PARAMS.get(item)
    if p is None:
        return 1
    base, T, I0 = p["base"], p["T"], _ORCL_I0
    if inv < I0:
        f = p["bf"]
        amp = p["bt"] * base / _orcl_shape(f, T, T)
        price = base + amp * _orcl_shape(f, I0 - inv, T)
    else:
        f = p["af"]
        amp = p["at"] * base / _orcl_shape(f, T, T)
        price = base - amp * _orcl_shape(f, inv - I0, T)
    return max(1, int(round(price)))


def _orcl_drain_rate(good, shops):
    total = 0
    for name in shops:
        products = _ORCL_SHOPS.get(name)
        if products and good in products:
            total += 2 if len(products) == 1 else 1
    return total


def _orcl_projected_best(item, inv, step, shops, horizon=10):
    rate = _orcl_drain_rate(item, shops)
    center = 1 if item != "FERTILIZER" else 0
    best = _orcl_price(item, inv)
    cur = inv
    for k in range(1, horizon + 1):
        t = step + k
        if t % 4 == 0:
            cur -= rate
        if t % 24 == 0:
            cur -= center
        price = _orcl_price(item, cur)
        if price > best:
            best = price
    return best


_ORCL_PARENT = agent
