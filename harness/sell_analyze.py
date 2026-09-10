"""Analyze which items each player sells per day in an iter35 loss replay.
Shows market sell orders (SELL) and total income buckets."""
import json
import sys
from collections import defaultdict

ME = "DanilChil"
path = sys.argv[1]
d = json.load(open(path))
names = d["info"]["TeamNames"]
rewards = d.get("rewards", [0, 0])
me = names.index(ME) if ME in names else 0
opp = 1 - me
steps = d["steps"]
print(f"\n=== {path.split(chr(92))[-1]} | {names[0]} vs {names[1]} | {rewards[0]:.0f}:{rewards[1]:.0f} ===")

sell_per_day = {i: defaultdict(lambda: defaultdict(int)) for i in (me, opp)}
buy_per_day = {i: defaultdict(lambda: defaultdict(int)) for i in (me, opp)}
all_buys = {i: defaultdict(int) for i in (me, opp)}
all_sells = {i: defaultdict(int) for i in (me, opp)}

for st in steps:
    for p, team in enumerate(st):
        obs = team.get("observation", {})
        day = obs.get("day", 0)
        for m in ((team.get("action") or {}).get("market") or []):
            if not m or len(m) < 2:
                continue
            op = m[0]
            item = m[1]
            n = m[2] if len(m) > 2 else 1
            if op == "SELL":
                sell_per_day[p][day][item] += n
                all_sells[p][item] += n
            elif op in ("BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT"):
                buy_per_day[p][day][f"{op}:{item}"] += n
                all_buys[p][item] += n

print("  day | us SELL (item:qty) | opp SELL")
for day in range(0, 30):
    us = dict(sell_per_day[me].get(day, {}))
    op = dict(sell_per_day[opp].get(day, {}))
    if us or op:
        us_s = ",".join(f"{k}:{v}" for k, v in sorted(us.items()))
        op_s = ",".join(f"{k}:{v}" for k, v in sorted(op.items()))
        print(f"  {day:3d} | {us_s or '-':34s} | {op_s or '-'}")

print("  TOTAL SELLS us:", dict(all_sells[me]))
print("  TOTAL SELLS opp:", dict(all_sells[opp]))
print("  TOTAL BUYS us:", dict(all_buys[me]))
print("  TOTAL BUYS opp:", dict(all_buys[opp]))