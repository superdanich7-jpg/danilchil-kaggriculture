"""diag_tape.py — find the FIRST state divergence between original episode
and both-seats tape replay, and the action that caused it.

Usage: py -3.12 harness/diag_tape.py <episode_id>
"""
import importlib.util
import json
import sys

from kaggle_environments import make

HERE = r"c:\kaglab"
TAPE_DIR = HERE + r"\flight\tapes"
DAILY = HERE + r"\replays\daily\20260909"


def load_agent(path):
    spec = importlib.util.spec_from_file_location(
        "tape_agent_" + str(abs(hash(path))), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def state_snapshot(obs, seat):
    try:
        farm = obs["farms"][seat]
        units = [tuple(farm["farmer"])] + [tuple(h) for h in farm.get("hands", [])]
        return {
            "money": round(float(farm["money"]), 1),
            "n_hands": len(farm.get("hands", [])),
            "units": sorted(units),
        }
    except Exception as e:
        return {"err": str(e)}


def main():
    epid = sys.argv[1]
    d = json.load(open(f"{DAILY}\\{epid}.json"))
    seed = d["info"].get("seed")
    steps = d["steps"]

    a0 = load_agent(f"{TAPE_DIR}\\tape_{epid}_0.py")
    a1 = load_agent(f"{TAPE_DIR}\\tape_{epid}_1.py")

    env = make("kaggriculture",
               configuration={"episodeSteps": 720, "seed": seed})
    env.run([a0, a1])

    # find first step where either seat's state snapshot differs
    first_bad = None
    for i in range(len(steps)):
        if i >= len(env.steps):
            break
        try:
            robs0 = env.steps[i][0].observation
            # obs for seat s lives in env.steps[i][s].observation? In kaggle
            # envs, per-agent obs is in steps[i][agent]['observation'].
            o0 = state_snapshot(robs0, 0)
        except Exception:
            # fallback: shared observation
            try:
                o0 = state_snapshot(env.steps[i][0].observation, 0)
            except Exception:
                o0 = {"err": "no-obs"}
        try:
            o1 = state_snapshot(env.steps[i][1].observation, 1)
        except Exception:
            o1 = {"err": "no-obs"}
        orig0 = state_snapshot(steps[i][0]["observation"], 0)
        orig1 = state_snapshot(steps[i][1]["observation"], 1)
        if o0 != orig0 or o1 != orig1:
            first_bad = i
            break

    if first_bad is None:
        print("STATES MATCH ALL STEPS")
        return

    print(f"first state divergence at step {first_bad} "
          f"(day {first_bad // 24}, hour {first_bad % 24})")
    for seat, o, orig in ((0, o0, orig0), (1, o1, orig1)):
        if o != orig:
            print(f"  seat{seat} replayed={o}")
            print(f"  seat{seat} original={orig}")
            # actions around the divergence:
            # replayed action returned at obs step first_bad-1 is ACTIONS[first_bad]
            tb = open(f"{TAPE_DIR}\\tape_{epid}_{seat}.py", encoding="utf-8").read()
            ns = {}
            exec(tb.split("def agent")[0], ns)
            A = ns["ACTIONS"]
            print(f"  tape returns at obs {first_bad - 1}: "
                  f"{json.dumps(A[first_bad])[:200]}")
            print(f"  original action stored at step {first_bad}: "
                  f"{json.dumps(steps[first_bad][seat].get('action') or {})[:200]}")
            print(f"  original action stored at step {first_bad - 1}: "
                  f"{json.dumps(steps[first_bad - 1][seat].get('action') or {})[:200]}")


if __name__ == "__main__":
    main()
