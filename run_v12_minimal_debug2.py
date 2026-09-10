from kaggle_environments import make
from bots.v12_minimal_v3 import agent

env = make("kaggriculture", debug=True)
env.run([agent, "bots/v9.py"])

# Debug log per step (first 30 steps)
for step_idx in range(min(30, len(env.steps))):
    s = env.steps[step_idx]
    o = s[0].observation
    day = o.day
    hour = o.hour
    money = o.farms[o.player].money
    priv = o.private or {}
    shed = priv.get("shed", {}) or {}
    
    # Check goose
    goose_on_tile = any(isinstance(t, dict) and t.get("animal") == "GOOSE"
                        for row in o.farms[o.player].tiles for t in row)
    
    print(f"step={step_idx:3d} day={day:2d} hour={hour:2d} money={money:6.0f} "
          f"goose={goose_on_tile} eggs={shed.get('EGG',0)} melon={shed.get('MELON',0)} "
          f"wheat={shed.get('WHEAT',0)} goose_shed={shed.get('GOOSE',0)}")

print("\n...")
obs = env.steps[-1][0].observation
print(f"FINAL money={obs.farms[obs.player].money}")