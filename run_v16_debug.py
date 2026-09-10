from kaggle_environments import make
import bots.v16 as m

env = make("kaggriculture", debug=True)
env.run([m.agent, "pass"])

melon_prod = 0
for step_idx in range(1, min(len(env.steps), 720), 1):
    s = env.steps[step_idx]
    o = s[0].observation
    # оцениваем продажи melon по market-логам
    pass

for step_idx in range(0, min(len(env.steps), 720), 24):
    s = env.steps[step_idx]
    o = s[0].observation
    day = o.day
    money = o.farms[o.player].money
    priv = o.private or {}
    shed = priv.get("shed", {}) or {}
    prices = o.get("market", {}).get("prices", {}) or {}
    anims = [t.get("animal") for row in o.farms[o.player].tiles for t in row
             if isinstance(t, dict) and "animal" in t]
    nhand = len(o.farms[o.player].get("hands", []))
    print(f"day={day:2d} money={money:6.0f} hands={nhand} anims={anims} "
          f"melon={shed.get('MELON',0)} fert={shed.get('FERTILIZER',0)} "
          f"milk={shed.get('MILK',0)} pMELON={prices.get('MELON','?')} "
          f"seeds={priv.get('seeds',{}).get('MELON',0)}")

obs = env.steps[-1][0].observation
print("FINAL money=", obs.farms[obs.player].money)
