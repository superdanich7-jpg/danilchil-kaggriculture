"""Diagnostics runner for v17: uses file-path agents so HIRE spawns hands."""
from kaggle_environments import make

env = make("kaggriculture", configuration={"seed": 0})
env.run(["bots/v17.py", "random"])

sells = {"FERTILIZER": 0, "WOOL": 0, "MILK": 0, "MELON": 0, "STRAWBERRY": 0}
for step in env.steps:
    try:
        a = step[0].action or {}
        mk = a.get("market") or []
        for m in mk:
            if isinstance(m, list) and m and m[0] == "SELL" and m[1] in sells:
                sells[m[1]] += m[2] if len(m) > 2 else 1
    except Exception:
        pass

print("=== per-day snapshots (player 0) ===")
seen = set()
placed_d2 = None
straw_d15 = None
for s in env.steps:
    o = s[0].observation
    if not isinstance(o, dict):
        continue
    d = o.get("day")
    if d is None or (d in seen):
        if d == 2 and placed_d2 is None:
            fm0 = o["farms"][o["player"]]
            placed_d2 = sum(1 for row in fm0["tiles"] for t in row
                            if isinstance(t, dict) and t.get("animal"))
        if d == 15 and straw_d15 is None:
            fm0 = o["farms"][o["player"]]
            straw_d15 = sum(1 for row in fm0["tiles"] for t in row
                            if isinstance(t, dict) and t.get("kind") == "PLANT"
                            and t.get("crop") == "STRAWBERRY")
        continue
    seen.add(d)

    fm = o["farms"][o["player"]]
    priv = o.get("private") or {}
    shed = priv.get("shed") or {}
    seeds = priv.get("seeds") or {}
    crops = {}
    anims = []
    for row in fm["tiles"]:
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    crops[t.get("crop")] = crops.get(t.get("crop"), 0) + 1
                if t.get("animal"):
                    anims.append(t["animal"])
    print(f"d{d:2d} money={fm['money']:7.0f} hands={len(fm.get('hands') or [])} "
          f"anims={len(anims)}{anims} crops={crops} "
          f"fert_shed={shed.get('FERTILIZER',0)} straw_seeds={seeds.get('STRAWBERRY',0)} "
          f"wheat_shed={shed.get('WHEAT',0)} cow_shed={shed.get('COW',0)} "
          f"sheep_shed={shed.get('SHEEP',0)} quads={len(fm.get('unlocked_quadrants') or [])}")

o = env.steps[-1][0].observation
final_money = o["farms"][o["player"]]["money"]
print("FINAL money =", final_money)
print("SALES:", sells)
print("CHECKS:")
print(f"  [1] animals placed on day 2 (target >=4): {placed_d2}")
print(f"  [2] fertilizer sold total (target >60):  {sells['FERTILIZER']}")
print(f"  [3] strawberry tiles day 15 (target >10): {straw_d15}")
print(f"  [4] wool sold (target >20):              {sells['WOOL']}")
print(f"  [5] milk sold (target >15):              {sells['MILK']}")


