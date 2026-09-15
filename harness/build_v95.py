"""v95: unblock the dormant V219 late-tomato investment on SE land.

Evidence (LB + trace):
- iter47 clean tape = 1996.5, our best ever; v93 (V230 + arbitrage layers) = 1892.
  Trace on the same seed: layers cost 4 017 by d28. Layers are rejected.
- V219 (buy SE land + tomato seeds + dedicated crew, d18-29) exists in the tape but
  NEVER fires: its gate needs TOMATO price >= 70 AND >= 3 of
  {PIZZA_SHOP, FARMERS_MARKET} unlocked. Meanwhile at d28 we hold 66k dead money,
  PLANT=0 and 25 SE tiles still LOCKED, while endgame TOMATO trades at 78-91
  (nobody produces it: MILK/WOOL/FERTILIZER/STRAWBERRY all crash to 1-5).

v95 loosens exactly two numbers of that gate, keeping every safety check:
  TOMATO price >= 70 -> >= 45      (endgame deficit price, still above base)
  shops (PIZZA/FARMERS_MARKET) >= 3 -> >= 1
Build variants for the ablation via the SHOP_MIN / PRICE_MIN constants below.
"""
import ast
import sys

SHOP_MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 1
PRICE_MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 45
OUT = sys.argv[3] if len(sys.argv) > 3 else 'bots/v95.py'

src = open('bots/v_iter47.py', encoding='utf-8').read()

old = (
    "    if farm['money'] < 12000 or obs['market']['prices']['TOMATO'] < 70:\n"
    "        return False\n"
    "    if sum(s in ('PIZZA_SHOP','FARMERS_MARKET') for s in obs['town']['unlocked_shops']) < 3:\n"
    "        return False\n"
)
assert old in src, 'V219 gate anchor missing'

new = (
    "    if farm['money'] < 12000 or obs['market']['prices']['TOMATO'] < %d:\n" % PRICE_MIN +
    "        return False\n"
    "    if sum(s in ('PIZZA_SHOP','FARMERS_MARKET') for s in obs['town']['unlocked_shops']) < %d:\n" % SHOP_MIN +
    "        return False\n"
)
src = src.replace(old, new, 1)

# Mark the variant so traces and telemetry identify it.
src = src.replace(
    "# Appended to frozen V218 by build_v219_tomatoes.py.",
    "# v95: V219 gate loosened (shops>=%d, tomato price>=%d) - see build_v95.py header." % (SHOP_MIN, PRICE_MIN),
    1,
)

open(OUT, 'w', encoding='utf-8').write(src)
ast.parse(src)
print('%s written and valid (SHOP_MIN=%d PRICE_MIN=%d)' % (OUT, SHOP_MIN, PRICE_MIN))
