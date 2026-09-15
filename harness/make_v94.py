import ast

src = open('bots/v93.py', encoding='utf-8').read()

# V94 fixes to the arbitrage layer:
#  1) drop MILK (linear impact + massive mirror oversupply -> self-dump, the
#     21k-unit milk order crashed our own 212-coin milk market to 5.9);
#  2) absolute floor: never BUY below price 8 (near-zero prices stay there);
#  3) cap SELL by actual shed stock (no phantom orders that crash the market).
old = '    for good in ("WHEAT", "MILK", "EGG"):'
assert old in src, 'goods anchor missing'
src = src.replace(old, '    for good in ("WHEAT", "EGG"):', 1)

old2 = """        if len(market) < MAX_ORDERS - 1 and price < 0.55 * med and money >= 6000:"""
assert old2 in src, 'buy anchor missing'
new2 = """        if len(market) < MAX_ORDERS - 1 and price < 0.55 * med and price >= 8 and money >= 6000:"""
src = src.replace(old2, new2, 1)

old3 = """        elif price > 1.45 * med and hold.get(good, 0) > 0:
            market.append(["SELL", good, hold[good]])
            hold[good] = 0"""
assert old3 in src, 'sell anchor missing'
new3 = """        elif price > 1.45 * med and hold.get(good, 0) > 0:
            shed = (obs.get("private") or {}).get("shed") or {}
            can_sell = min(hold[good], int(shed.get(good, 0) or 0))
            if can_sell > 0:
                market.append(["SELL", good, can_sell])
                hold[good] -= can_sell"""
src = src.replace(old3, new3, 1)

open('bots/v94.py', 'w', encoding='utf-8').write(src)
ast.parse(src)
print('v94 (arb fixes: no milk, floor, shed-cap) valid')
