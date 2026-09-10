from kaggle_environments import make
from bots.v13 import agent

env = make("kaggriculture", debug=True)
env.run([agent, "bots/v9.py"])

for step_idx in range(0, min(len(env.steps), 720), 24):
    s = env.steps[step_idx]
    o = s[0].observation
    day = o.day
    money = o.farms[o.player].money
    priv = o.private or {}
    shed = priv.get("shed", {}) or {}
    cows = [t for row in o.farms[o.player].tiles for t in row
            if isinstance(t, dict) and t.get("animal") == "COW"]
    print(f"day={day:2d} money={money:6.0f} cows={len(cows)} "
          f"fert={shed.get('FERTILIZER',0)} milk={shed.get('MILK',0)} "
          f"melon_prod={shed.get('MELON',0)} wheat={shed.get('WHEAT',0)}")

obs = env.steps[-1][0].observation
print("FINAL money=", obs.farms[obs.player].money)
