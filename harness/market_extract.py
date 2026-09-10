"""Extract opponent market activity from a replay."""
import json
import sys
from collections import Counter, defaultdict

path = sys.argv[1]
who = sys.argv[2] if len(sys.argv) > 2 else None
d = json.load(open(path))
names = d["info"]["TeamNames"]
opp = names.index(who) if who in names else 1
buys = Counter()
sells = Counter()
buys_day = defaultdict(Counter)
sells_day = defaultdict(Counter)
for i, st in enumerate(d["steps"]):
    day = i // 24
    a = st[opp].get("action") or {}
    for m in (a.get("market") or []):
        if not m:
            continue
        op = m[0]
        n = m[2] if len(m) > 2 else 1
        if op in ("BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT"):
            buys[f"{op}:{m[1]}"] += n
            buys_day[day][f"{op}:{m[1]}"] += n
        elif op == "SELL":
            sells[m[1]] += n
            sells_day[day][m[1]] += n
print(f"{who or names[opp]} buys:", dict(buys))
print(f"{who or names[opp]} sells:", dict(sells))
print("buys per day:", {k: dict(v) for k, v in sorted(buys_day.items())})
print("sells per day:", {k: dict(v) for k, v in sorted(sells_day.items())})
