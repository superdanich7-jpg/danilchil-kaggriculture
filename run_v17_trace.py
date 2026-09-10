"""Hour-by-hour trace of crew behavior on days 2-4."""
from kaggle_environments import make

env = make("kaggriculture", configuration={"seed": 0})
env.run(["bots/v17.py", "random"])

for s in env.steps:
    o = s[0].observation
    if not isinstance(o, dict):
        continue
    d, h = o.get("day"), o.get("hour")
    if d not in (1, 2, 3) :
        continue
    fm = o["farms"][o["player"]]
    priv = o.get("private") or {}
    shed = priv.get("shed") or {}
    act = s[0].action or {}
    anims = []
    for y, row in enumerate(fm["tiles"]):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("animal"):
                anims.append((x, y, t["animal"], t.get("fed_today"),
                              t.get("consecutive_unfed")))
    acts = [act.get("farmer")] + list(act.get("hands") or [])
    print(f"d{d} h{h:2d} shedW={shed.get('WHEAT',0)} money={fm['money']:.0f} "
          f"hands={len(fm.get('hands') or [])} anims={anims} acts={acts}")
