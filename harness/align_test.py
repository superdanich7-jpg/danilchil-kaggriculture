"""align_test.py — definitive alignment + drift test for tape replay.

Tests both alignment hypotheses (+1 and +0) for tape replay of BOTH seats
on the episode's own seed, with STRICT per-step comparison of money and
market prices. Prints the first divergence for each mode with full action
JSON around it.

Usage: py -3.12 harness/align_test.py <episode_id>
"""
import importlib.util
import json
import sys

from kaggle_environments import make

DAILY = r"replays/daily/20260909"


def load(path):
    spec = importlib.util.spec_from_file_location("ta_" + str(abs(hash(path))), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def make_tape_agent(acts, offset):
    def agent(obs):
        try:
            s = obs.get("step")
            if s is None:
                s = int(obs.get("day", 0)) * 24 + int(obs.get("hour", 0))
            j = int(s) + offset
            if 0 <= j < len(acts):
                a = acts[j]
            elif acts:
                a = acts[-1]
            else:
                a = {}
            return {"farmer": a.get("farmer") or ["PASS"],
                    "hands": a.get("hands") or [],
                    "market": a.get("market") or []}
        except Exception:
            return {"farmer": ["PASS"], "hands": [], "market": []}
    return agent


def first_diff(d, env, label, check_prices=True):
    steps = d["steps"]
    for i in range(min(len(steps), len(env.steps))):
        for seat in (0, 1):
            try:
                ro = env.steps[i][seat].observation
            except Exception:
                continue
            oo = steps[i][seat]["observation"]
            om = oo["farms"][seat]["money"]
            rm = ro["farms"][seat]["money"]
            if abs(om - rm) > 0.01:
                print(f"[{label}] first MONEY diff: step {i} seat{seat} "
                      f"orig={om} replay={rm}")
                for j in (max(0, i - 1), i):
                    print(f"  orig step {j} seat{seat}: "
                          f"{json.dumps(steps[j][seat].get('action') or {})[:200]}")
                return i
            if check_prices:
                op = (oo.get("market") or {}).get("prices", {}) or {}
                rp = (ro.get("market") or {}).get("prices", {}) or {}
                for k in op:
                    if k in rp and abs(float(op[k]) - float(rp[k])) > 0.01:
                        print(f"[{label}] first PRICE diff: step {i} {k} "
                              f"orig={op[k]} replay={rp[k]}")
                        for j in (max(0, i - 1), i):
                            print(f"  orig step {j} seat{seat}: "
                                  f"{json.dumps(steps[j][seat].get('action') or {})[:200]}")
                        return i
    print(f"[{label}] no diff in {min(len(steps), len(env.steps))} steps")
    return None


def main():
    epid = sys.argv[1]
    d = json.load(open(f"{DAILY}/{epid}.json"))
    seed = d["info"].get("seed")
    steps = d["steps"]
    print(f"episode {epid} seed={seed} steps={len(steps)}")
    print("steps[0] actions:",
          json.dumps(steps[0][0].get("action")), "|",
          json.dumps(steps[0][1].get("action")))
    print("steps[1] actions:",
          json.dumps(steps[1][0].get("action"))[:120], "|",
          json.dumps(steps[1][1].get("action"))[:120])

    acts0 = [(s[0].get("action") or {}) for s in steps]
    acts1 = [(s[1].get("action") or {}) for s in steps]

    for offset in (1, 0):
        env = make("kaggriculture",
                   configuration={"episodeSteps": 720, "seed": seed})
        env.run([make_tape_agent(acts0, offset),
                 make_tape_agent(acts1, offset)])
        first_diff(d, env, f"offset={offset:+d}")
        got = [float(s.reward) for s in env.steps[-1]]
        orig = [float(s["reward"]) for s in steps[-1]]
        print(f"[offset={offset:+d}] final orig={orig} replay={got}")


if __name__ == "__main__":
    main()
