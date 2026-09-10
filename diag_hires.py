from kaggle_environments import make
import bots.v9 as v9
import bots.v16 as v16

for name, mod in [("v9", v9), ("v16", v16)]:
    env = make("kaggriculture", debug=True)
    env.run([mod.agent, "pass"])
    o0 = env.steps[1][0].observation
    f0 = o0.farms[0]
    o7 = env.steps[13][0].observation  # day 6*24=144 -> step 144? day6
    f7 = o7.farms[0]
    print(f"=== {name} ===")
    print("day1 hires_today=", f0.get("hires_today"), "n_hands=", len(f0.get("hands", [])))
    print("day1 money=", f0["money"])
    print("keys:", sorted(f0.keys()))
    print("day6 hires_today=", f7.get("hires_today"), "n_hands=", len(f7.get("hands", [])))
