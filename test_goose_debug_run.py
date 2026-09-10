from kaggle_environments import make

env = make("kaggriculture", debug=True)
env.run(["bots/test_goose_debug.py", "pass"])
obs = env.steps[-1][0].observation
farm = obs["farms"][obs["player"]]
goose = [ (x,y,t) for y,row in enumerate(farm["tiles"]) for x,t in enumerate(row)
          if isinstance(t, dict) and t.get("animal")=="GOOSE" ]
print("\n\nFINAL GOOSE PLACED:", len(goose)>0, goose)