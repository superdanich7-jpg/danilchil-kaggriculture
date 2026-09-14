import json

SRC = 'bots/opp_thirdfarm.py'
DST = 'bots/v85.py'

src = open(SRC, encoding='utf-8').read()

# Append final-liquidation wrapper: on the last turns sell everything in the
# shed (the raw tape under-sells ~441 units on foreign seeds).
wrapper = '''

# V85: final liquidation — the raw tape leaves goods unsold on foreign seeds.
# Only fire on the very last step so the tape plan stays intact.
_v85_tape = agent


def agent(obs):
    try:
        step = int(obs.get("step") or 0)
    except Exception:
        step = 0
    if step < 719:
        return _v85_tape(obs)
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

import ast
ast.parse(open(DST, encoding='utf-8').read())
print('v85 (thirdfarm + liquidation) valid')
