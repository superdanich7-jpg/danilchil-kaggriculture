from kaggle_environments import make

env = make("kaggriculture", debug=True)
env.run(["bots/test_goose_debug.py", "pass"])

# Print first 20 steps only
for step_idx, step in enumerate(env.steps[:20]):
    obs0 = step[0].observation
    f = obs0.farms[obs0.player]
    priv = obs0.private or {}
    shed = priv.get("shed", {}) or {}
    inv = (priv.get("inventories") or [{}])[0]
    pos = tuple(f.farmer)
    day = obs0.day
    hour = obs0.hour
    money = f.money
    has_goose = any(isinstance(t, dict) and t.get("animal") == "GOOSE"
                    for row in f.tiles for t in row)
    print(f"step={step_idx:3d} day={day:2d} hour={hour:2d} pos={pos} money={money:6.0f} "
          f"goose_on_tile={has_goose} shed_goose={shed.get('GOOSE',0)} inv_goose={inv.get('GOOSE',0)}")

print("\n... (truncated) ...")
obs = env.steps[-1][0].observation
farm = obs["farms"][obs["player"]]
goose = [ (x,y,t) for y,row in enumerate(farm["tiles"]) for x,t in enumerate(row)
          if isinstance(t, dict) and t.get("animal")=="GOOSE" ]
print("FINAL GOOSE PLACED:", len(goose)>0, goose)