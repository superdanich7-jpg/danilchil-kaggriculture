import ast

src = open('bots/v90.py', encoding='utf-8').read()

# V93: v90 + market-arbitrage layer.
# Small counter-cyclical trades (<=3% cash, <=2 extra orders, only liquid
# goods): buy when price < 0.55x trailing median, sell holdings when
# > 1.45x. Adds margin vs EVERY opponent without touching tape deliveries
# (uses end of market list; MAX_ORDERS enforced by env anyway).
anchor = '_V230_REPORT = '
idx = src.find('_V230_REPORT')
assert idx > 0, 'V230 anchor missing'
layer = '''

# V93 arbitrage: counter-cyclical small trades.
_V93_HIST = {}
_V93_HOLD = {}


def _v93_median(vals):
    o = sorted(vals)
    n = len(o)
    return o[n // 2] if n % 2 else (o[n // 2 - 1] + o[n // 2]) / 2


def _v93_arb(obs, action, player):
    prices = obs["market"]["prices"]
    day = int(obs["step"]) // 24
    hist = _V93_HIST.setdefault(player, {})
    hold = _V93_HOLD.setdefault(player, {})
    for good, price in prices.items():
        s = hist.setdefault(good, [])
        if s and s[-1][0] == day:
            s[-1] = (day, int(price))
        else:
            s.append((day, int(price)))
    money = int(obs["farms"][player]["money"])
    market = action.setdefault("market", [])
    for good in ("WHEAT", "MILK", "EGG"):
        series = [p for _, p in hist.get(good, [])][-8:]
        if len(series) < 4:
            continue
        med = _v93_median(series)
        price = int(prices.get(good, 0))
        if price <= 0 or med <= 0:
            continue
        if len(market) < MAX_ORDERS - 1 and price < 0.55 * med and money >= 6000:
            spend = min(int(money * 0.03), 1200)
            qty = max(1, spend // price)
            market.append(["BUY_PRODUCT", good, qty])
            hold[good] = hold.get(good, 0) + qty
            money -= spend
        elif price > 1.45 * med and hold.get(good, 0) > 0:
            market.append(["SELL", good, hold[good]])
            hold[good] = 0
'''
ins = src.find('def agent(', idx)
assert ins > 0, 'agent def not found after V230'
src = src[:ins] + layer + '\n\n' + src[ins:]

OLD_RET = """    try:
        action=_v230_adapt(observation,action,FarmView(observation),state)
    except Exception:
        pass
    _V230_REPORT.update(_V228_REPORT)
    return action"""
assert OLD_RET in src, 'return anchor missing'
NEW_RET = """    try:
        action=_v230_adapt(observation,action,FarmView(observation),state)
    except Exception:
        pass
    try:
        if int(observation["step"]) < 648:
            _v93_arb(observation,action,player)
    except Exception:
        pass
    _V230_REPORT.update(_V228_REPORT)
    return action"""
src = src.replace(OLD_RET, NEW_RET, 1)

open('bots/v93.py', 'w', encoding='utf-8').write(src)
ast.parse(src)
print('v93 (v90 + arbitrage) valid')
