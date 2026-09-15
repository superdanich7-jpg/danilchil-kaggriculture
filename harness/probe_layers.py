"""Probe which runtime layers actually fire inside a stacked agent.

Loads the agent file directly (so ``agent.telemetry`` is reachable), runs one
episode against a reference opponent and prints the non-zero telemetry
counters plus a final farm summary.  Usage:

    py -3.12 harness/probe_layers.py bots/v94.py [seeds] [opp_path]
"""
import importlib.util
import sys

from kaggle_environments import make


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def farm_summary(obs):
    farm = obs["farms"][obs["player"]]
    tiles = farm["tiles"]
    crops = {}
    for row in tiles:
        for tile in ([row] if isinstance(row, dict) else row):
            if isinstance(tile, dict) and tile.get("crop"):
                crops[tile["crop"]] = crops.get(tile["crop"], 0) + 1
    shed = (obs.get("private") or {}).get("shed") or {}
    return {
        "money": int(farm["money"]),
        "crops": crops,
        "shed": {k: v for k, v in shed.items() if v},
        "quadrants": farm.get("unlocked_quadrants"),
        "hands": len(farm.get("hands") or []),
    }


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "champ/main.py"
    seeds = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    opp_path = sys.argv[3] if len(sys.argv) > 3 else "bots/v_iter47.py"

    mine = load(path, "probe_mine")
    opp = load(opp_path, "probe_opp")

    for seed in range(seeds):
        env = make("kaggriculture",
                   configuration={"episodeSteps": 720, "seed": seed})
        env.run([mine.agent, opp.agent])
        rewards = [float(s.reward) for s in env.steps[-1]]
        tel = dict(mine.agent.telemetry)
        obs = env.steps[-1][0].observation
        print(f"seed={seed} rewards={rewards} summary={farm_summary(obs)}")
        fires = {k: v for k, v in tel.items()
                 if isinstance(v, (int, float)) and v and k not in ("step", "day")}
        print(f"  telemetry(nonzero)={fires}")


if __name__ == "__main__":
    main()