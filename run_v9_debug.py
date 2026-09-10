from kaggle_environments import make
import bots.v9 as v9

env = make("kaggriculture", debug=True)
env.run([v9.agent, "pass"])

# day-boundary steps: day N == step N*24
for day in range(0, 12):
    step = day * 24
    if step >= len(env.steps):
        break
    o = env.steps[step][0].observation
    f = o.farms[o.player]
    priv = o.private or {}
    shed = priv.get("shed", {}) or {}
    hands = f.get("hands", [])
    mel = sum(1 for row in f["tiles"] for t in row
              if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON")
    print(f"day={day:2d} money={f['money']:6.0f} n_hands={len(hands)} hires_today={f.get('hires_today',0)} "
          f"melon_tiles={mel} shed_melon={shed.get('MELON',0)}")

obs = env.steps[-1][0].observation
print("FINAL money=", obs.farms[obs.player].money)
