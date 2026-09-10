import json
import glob
from collections import defaultdict

for path in sorted(glob.glob(r"replays/iter42/*.json")):
    d = json.load(open(path))
    names = d["info"]["TeamNames"]
    me = names.index("DanilChil")
    opp = 1 - me
    tot = [defaultdict(int), defaultdict(int)]
    for i, s in enumerate(d["steps"]):
        for idx in (me, opp):
            a = (s[idx].get("action") or {})
            for o in a.get("market", []) or []:
                if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
                    tot[idx][o[1]] += int(o[2])
    print(path.split("episode-")[1][:6], names[opp][:14])
    print("  ME :", dict(sorted(tot[me].items())))
    print("  OPP:", dict(sorted(tot[opp].items())))

names = d["info"]["TeamNames"]
me = names.index("DanilChil")
sells = defaultdict(lambda: defaultdict(int))
for i, s in enumerate(d["steps"]):
    a = (s[me].get("action") or {}) if isinstance(s, list) and len(s) > me else {}
    for o in a.get("market", []) or []:
        if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
            sells[i // 24][o[1]] += int(o[2])
print("MY sells per day:")
for day in sorted(sells):
    print("d%2d:" % day, dict(sells[day]))
tot = defaultdict(int)
for day in sells:
    for k, v in sells[day].items():
        tot[k] += v
print("TOTAL:", dict(tot))
