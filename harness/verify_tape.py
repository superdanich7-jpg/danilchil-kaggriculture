"""verify_tape.py — sanity check for tape extraction.

Replays BOTH seats' tapes verbatim in a fresh environment on the episode's
own seed. If extraction is correct, final rewards must be close to the
original episode's rewards. A large mismatch means the tape pipeline is
broken (indexing, action format, market rejection, ...).

Usage:
    py -3.12 harness/verify_tape.py <episode_id> [seed]
"""
import importlib.util
import json
import sys
import time

from kaggle_environments import make

HERE = r"c:\kaglab"
TAPE_DIR = HERE + r"\flight\tapes"
DAILY = HERE + r"\replays\daily\20260909"


def load_agent(path):
    spec = importlib.util.spec_from_file_location("tape_agent_" + str(abs(hash(path))), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def main():
    epid = sys.argv[1]
    path = f"{DAILY}\\{epid}.json"
    d = json.load(open(path))
    seed = d["info"].get("seed")
    orig = [s.get("reward") for s in d["steps"][-1]]
    print(f"episode {epid}: seed={seed} original rewards={orig}")

    a0 = load_agent(f"{TAPE_DIR}\\tape_{epid}_0.py")
    a1 = load_agent(f"{TAPE_DIR}\\tape_{epid}_1.py")

    t0 = time.time()
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    except Exception:
        env = make("kaggriculture", configuration={"episodeSteps": 720})
    env.run([a0, a1])
    got = [float(s.reward) for s in env.steps[-1]]
    print(f"replayed rewards = {got}  ({time.time()-t0:.0f}s)")
    if orig[0]:
        print(f"drift: seat0 {got[0]-orig[0]:+.0f} ({100*(got[0]-orig[0])/orig[0]:+.1f}%), "
              f"seat1 {got[1]-orig[1]:+.0f} ({100*(got[1]-orig[1])/orig[1]:+.1f}%)")

    # diagnose divergence: first step where replayed money differs a lot
    for i in range(0, 720, 24):
        try:
            om = d["steps"][i][0]["observation"]["farms"][0]["money"]
            rm = env.steps[i][0].observation["farms"][0]["money"]
        except Exception:
            continue
        if abs(om - rm) > max(50, 0.2 * max(om, 1)):
            print(f"DIVERGE at day {i//24}: original money={om:.0f} replayed={rm:.0f}")
            break
    else:
        print("no early divergence (money tracks within 20%)")


if __name__ == "__main__":
    main()
