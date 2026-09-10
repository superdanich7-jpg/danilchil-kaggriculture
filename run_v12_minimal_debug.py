from kaggle_environments import make
from bots.v12_minimal_v3 import agent

env = make("kaggriculture", debug=True)
env.run([agent, "bots/v9.py"])

# Debug log per day
for step_idx in range(0, len(env.steps), 24):
    if step_idx >= len(env.steps):
        break
    s = env.steps[step_idx]
    o = s[0].observation
    day = o.day
    money = o.farms[o.player].money
    priv = o.private or {}
    shed = priv.get("shed", {}) or {}
    
    # Count geese on tiles
    goose_on_tile = any(isinstance(t, dict) and t.get("animal") == "GOOSE"
                        for row in o.farms[o.player].tiles for t in row)
    
    print(f"day={day:2d} money={money:6.0f} goose={goose_on_tile} "
          f"eggs={shed.get('EGG',0)} melon={shed.get('MELON',0)} "
          f"wheat={shed.get('WHEAT',0)} fertilizer={shed.get('FERTILIZER',0)}")

print("\nFINAL:")
obs = env.steps[-1][0].observation
print(f"money={obs.farms[obs.player].money}")