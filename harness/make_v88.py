import ast

SRC = 'bots/opp_ymgaq.py'
DST = 'bots/v88.py'

src = open(SRC, encoding='utf-8').read()

wrapper = '''

# V88: ymg_aq tape + final liquidation (fires only on the last step).
_v88_tape = agent


def agent(obs):
    try:
        step = int(obs.get("step") or 0)
    except Exception:
        step = 0
    if step < 719:
        return _v88_tape(obs)
    try:
        shed = (obs.get("private") or {}).get("shed") or {}
    except Exception:
        shed = {}
    prices = (obs.get("market") or {}).get("prices") or {}
    market = [["SELL", item, int(qty)] for item, qty in shed.items()
              if isinstance(qty, (int, float)) and int(qty) > 0 and int(prices.get(item, 0)) >= 2]
    market.sort(key=lambda o: -int(prices.get(o[1], 0)) * o[2])
    return {"farmer": ["PASS"], "hands": [], "market": market}
'''
open(DST, 'w', encoding='utf-8').write(src + wrapper)
ast.parse(open(DST, encoding='utf-8').read())
print('v88 (ymgaq + liquidation) valid')
