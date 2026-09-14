import ast

src = open('bots/v83.py', encoding='utf-8').read()

# v84: per-good lead depth by price-impact volatility instead of flat 2.
OLD_SUB = '''def subtract_advanced_sales(action, state, step):
    """Remove quantities already requested one turn early, retaining order slots."""
    if state.sale_due_step == step:
        remaining = dict(state.advanced_sales)
        for order in action["market"]:
            if order and order[0] == "SELL" and len(order) >= 3:
                item = order[1]
                removed = min(max(0, int(order[2])), remaining.get(item, 0))
                if removed > 0:
                    order[2] = int(order[2]) - removed
                    remaining[item] -= removed
    state.advanced_sales = {}
    state.sale_due_step = -1
'''
assert OLD_SUB in src, 'subtract anchor missing'
NEW_SUB = '''_V84_DEPTH = {"MELON": 3, "STRAWBERRY": 2, "TOMATO": 2, "EGG": 2, "MILK": 2, "WOOL": 2, "CARROT": 1}


def subtract_advanced_sales(action, state, step):
    """Remove quantities already requested one turn early, retaining order slots."""
    due = getattr(state, "sale_due_map", None) or {}
    remaining = dict(state.advanced_sales)
    for order in action["market"]:
        if order and order[0] == "SELL" and len(order) >= 3 and due.get(order[1]) == step:
            item = order[1]
            removed = min(max(0, int(order[2])), remaining.get(item, 0))
            if removed > 0:
                order[2] = int(order[2]) - removed
                remaining[item] -= removed
    state.advanced_sales = {k: v for k, v in remaining.items() if v > 0}
    state.sale_due_map = {k: s for k, s in due.items() if k in state.advanced_sales}
'''
src = src.replace(OLD_SUB, NEW_SUB, 1)

OLD_ADV_HEAD = '''    next_step = step + (2 if getattr(state, "lead_shift", False) else 1)
    if next_step > LAST_STEP or next_step % 72 == 0 or (step % 4 == 0 and step < 144):
        return
    planned = {}
    for order in tape[next_step].get("market") or []:
        if order and order[0] == "SELL" and len(order) >= 3 and order[1] in PRODUCTS:
            item = order[1]
            planned[item] = planned.get(item, 0) + max(0, int(order[2]))
'''
assert OLD_ADV_HEAD in src, 'advance head anchor missing'
NEW_ADV_HEAD = '''    lead = getattr(state, "lead_shift", False)
    if not hasattr(state, "sale_due_map"):
        state.sale_due_map = {}
    planned = {}
    plan_step = {}
    for item, depth in _V84_DEPTH.items():
        d = depth if lead else 1
        ns = step + d
        if ns > LAST_STEP or ns % 72 == 0 or (step % 4 == 0 and step < 144):
            continue
        for order in tape[ns].get("market") or []:
            if order and order[0] == "SELL" and len(order) >= 3 and order[1] == item:
                planned[item] = planned.get(item, 0) + max(0, int(order[2]))
                plan_step[item] = ns
'''
src = src.replace(OLD_ADV_HEAD, NEW_ADV_HEAD, 1)

OLD_TAIL = '''        action["market"].append(["SELL", item, quantity])
        state.advanced_sales[item] = quantity
    if state.advanced_sales:
        state.sale_due_step = next_step
'''
assert OLD_TAIL in src, 'advance tail anchor missing'
NEW_TAIL = '''        action["market"].append(["SELL", item, quantity])
        state.advanced_sales[item] = quantity
        state.sale_due_map[item] = plan_step[item]
'''
src = src.replace(OLD_TAIL, NEW_TAIL, 1)

OLD_WHEAT = '''        planned_wheat = planned.get("WHEAT", 0)
        if planned_wheat > 0 and stock.get("WHEAT", 0) - planned_wheat >= 150:
            planned["WHEAT"] = planned_wheat
            skip = ("FERTILIZER",)
'''
assert OLD_WHEAT in src, 'wheat anchor missing'
NEW_WHEAT = '''        planned_wheat = planned.get("WHEAT", 0)
        if planned_wheat > 0 and stock.get("WHEAT", 0) - planned_wheat >= 150:
            ns_w = step + 1
            if ns_w <= LAST_STEP and ns_w % 72 != 0:
                for order in tape[ns_w].get("market") or []:
                    if order and order[0] == "SELL" and len(order) >= 3 and order[1] == "WHEAT":
                        planned["WHEAT"] = planned.get("WHEAT", 0) + max(0, int(order[2]))
                        plan_step["WHEAT"] = ns_w
            skip = ("FERTILIZER",)
'''
src = src.replace(OLD_WHEAT, NEW_WHEAT, 1)

open('bots/v84.py', 'w', encoding='utf-8').write(src)
ast.parse(src)
print('v84 (volatility-depth lead) valid')
