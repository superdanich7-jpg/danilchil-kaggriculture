import ast

SRC = 'bots/opp_mengfei.py'
DST = 'bots/v86.py'

src = open(SRC, encoding='utf-8').read()

wrapper = '''

# V86: mengfei tape + final liquidation (seat-lead disabled: ACTIONS hidden
# inside the tape file, external peek impossible; lead is only safe on our
# own Policy architecture).
_v86_tape = agent


def agent(obs):
    step = int(obs.get("step") or 0)
    a = _v86_tape(obs)
    if step < 719:
        return a
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
print('v86 (mengfei + liquidation) valid')
