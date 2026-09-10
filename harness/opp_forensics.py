"""Opponent economy forensics: per-day money + aggregate market actions."""
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = sys.argv[1]
opp_name = sys.argv[2] if len(sys.argv) > 2 else None

d = json.load(open(path))
names = d["info"]["TeamNames"]
me = names.index("DanilChil") if "DanilChil" in names else 0
opp = 1 - me
if opp_name:
    opp = names.index(opp_name)
print(f"{names[me]} vs {names[opp]} | rewards {d['rewards']}")

steps = d["steps"]

def day_obs(day):
    st = min(day * 24, len(steps) - 1)
    return steps[st][opp]["observation"]

def farm_stats(f):
    tiles = f.get("tiles", [])
    plants = {}
    herd = 0
    empty = 0
    for row in tiles:
        for t in row:
            if t is None:
                empty += 1
            elif isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    plants[t.get("crop", "?")] = plants.get(t.get("crop", "?"), 0) + 1
                if t.get("kind") in ("PASTURE", "COOP") and t.get("animal"):
                    herd += 1
    return plants, herd, empty, f.get("money", 0), len(f.get("hands", []))

# per-day money + field
print("\nday | money | herd hands straw melon wheat | empty")
for day in range(0, 30):
    o = day_obs(day)
    farms = o.get("farms")
    if not farms:
        continue
    plants, herd, empty, money, hands = farm_stats(farms[opp])
    print(f"d{day:2d} | {money:6.0f} | {herd:3d} {hands:3d}  {plants.get('STRAWBERRY',0):4d} {plants.get('MELON',0):4d} {plants.get('WHEAT',0):4d} | {empty:4d}")

# aggregate market actions per type per day
from collections import defaultdict
sells = defaultdict(lambda: defaultdict(int))  # day -> item -> qty
buys = defaultdict(lambda: defaultdict(int))
hires = defaultdict(int)
for i, s in enumerate(steps):
    if not isinstance(s, list) or len(s) <= opp:
        continue
    a = s[opp].get("action") or {}
    day = i // 24
    for order in a.get("market", []) or []:
        if not isinstance(order, list) or len(order) < 2:
            continue
        verb = order[0]
        if verb == "SELL" and len(order) >= 3:
            sells[day][order[1]] += int(order[2])
        elif verb == "BUY_SEED":
            buys[day][order[1]] += int(order[2]) if len(order) >= 3 else 1
        elif verb == "BUY_ANIMAL":
            buys[day][order[1]] += int(order[2]) if len(order) >= 3 else 1
        elif verb == "BUY_PRODUCT":
            buys[day][order[1]] += int(order[2]) if len(order) >= 3 else 1
        elif verb == "HIRE":
            hires[day] += 1

print("\nSELLS per day (item: qty):")
for day in sorted(sells):
    tot = {k: v for k, v in sells[day].items() if v}
    if tot:
        print(f"d{day:2d}: {tot}")
print("\nBUYS per day (item: qty):")
for day in sorted(buys):
    tot = {k: v for k, v in buys[day].items() if v}
    if tot:
        print(f"d{day:2d}: {tot}")
print("\nHIRES per day:", {f"d{k:2d}": v for k, v in sorted(hires.items())})
