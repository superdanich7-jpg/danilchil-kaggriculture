import ast

src = open('bots/v81.py', encoding='utf-8').read()

# seat-aware lead shift: when we act second in a mirror, sell one turn earlier
# (including WHEAT if the shed keeps a feed buffer, and FERTILIZER) so we hit
# the clean market before the verbatim clone dumps its own stock.
old = """def advance_sales(action, view, state, tape, step):
    \"\"\"Bring eligible sales from our next planned action forward by one turn.\"\"\"
    next_step = step + 1
    if next_step > LAST_STEP or next_step % 72 == 0 or (step % 4 == 0 and step < 144):
        return
    planned = {}
    for order in tape[next_step].get("market") or []:
        if order and order[0] == "SELL" and len(order) >= 3 and order[1] in PRODUCTS:
            item = order[1]
            planned[item] = planned.get(item, 0) + max(0, int(order[2]))
    already_selling = {order[1] for order in action["market"]
                       if order and order[0] == "SELL" and len(order) > 1}
    stock = projected_shed(action, view)
    for item in PRODUCTS:
        if item in ("WHEAT", "FERTILIZER") or item in already_selling:
            continue
"""
assert old in src, 'advance_sales anchor missing'
new = """def advance_sales(action, view, state, tape, step):
    \"\"\"Bring eligible sales from our next planned action forward by one turn.\"\"\"
    next_step = step + 1
    if next_step > LAST_STEP or next_step % 72 == 0 or (step % 4 == 0 and step < 144):
        return
    planned = {}
    for order in tape[next_step].get("market") or []:
        if order and order[0] == "SELL" and len(order) >= 3 and order[1] in PRODUCTS:
            item = order[1]
            planned[item] = planned.get(item, 0) + max(0, int(order[2]))
    already_selling = {order[1] for order in action["market"]
                       if order and order[0] == "SELL" and len(order) > 1}
    stock = projected_shed(action, view)
    # V232 seat-aware: acting second -> lead the clone by one turn on bulk goods.
    skip = ("WHEAT", "FERTILIZER")
    lead = getattr(state, "lead_shift", False)
    if lead and int(view.prices.get("WHEAT", 0)) > 2:
        planned_wheat = planned.get("WHEAT", 0)
        if planned_wheat > 0 and stock.get("WHEAT", 0) - planned_wheat >= 150:
            planned["WHEAT"] = planned_wheat
            skip = ("FERTILIZER",)
    for item in PRODUCTS:
        if item in skip or item in already_selling:
            continue
"""
src = src.replace(old, new, 1)

# enable lead_shift at policy start for seat 1
old2 = "        state = self.players[player] = DayState()\n        state.last_step = step\n"
assert old2 in src, 'state anchor missing'
new2 = ("        state = self.players[player] = DayState()\n"
        "        state.last_step = step\n"
        "        state.lead_shift = player == 1\n")
src = src.replace(old2, new2, 1)

open('bots/v82.py', 'w', encoding='utf-8').write(src)
ast.parse(src)
print('v82 (seat-lead shift) valid')

# --- v83: double lead shift for seat 1 ---
src2 = open('bots/v82.py', encoding='utf-8').read()
oldn = """    next_step = step + 1
    if next_step > LAST_STEP or next_step % 72 == 0 or (step % 4 == 0 and step < 144):
        return
"""
assert oldn in src2, 'v83 anchor missing'
newn = """    next_step = step + (2 if getattr(state, "lead_shift", False) else 1)
    if next_step > LAST_STEP or next_step % 72 == 0 or (step % 4 == 0 and step < 144):
        return
"""
src2 = src2.replace(oldn, newn, 1)
open('bots/v83.py', 'w', encoding='utf-8').write(src2)
ast.parse(src2)
print('v83 (double lead shift) valid')
