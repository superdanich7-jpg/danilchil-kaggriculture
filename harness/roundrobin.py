"""Round-robin tournament of tape agents (in-process, fast).

Usage: py -3.12 harness/roundrobin.py [seeds_per_pair]
Each unordered pair plays N episodes, seats alternating. Ranks by
(winrate, avg dCoins) aggregated over all opponents.
"""
import json, sys, time, importlib.util
from kaggle_environments import make

CANDS = [
    "champ/main.py",
    "bots/opp_haodou.py",
    "bots/opp_schott.py",
    "bots/opp_umataro.py",
    "bots/opp_tk256.py",
    "bots/opp_107688351.py",
    "bots/opp_107762618.py",
    "bots/opp_107780814.py",
    "bots/opp_107796074.py",
]

def load(path):
    spec = importlib.util.spec_from_file_location("ag_" + str(abs(hash(path))), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent

def episode(agent_a, agent_b, seed, steps=720):
    try:
        env = make("kaggriculture", configuration={"episodeSteps": steps, "seed": seed})
    except Exception:
        env = make("kaggriculture", configuration={"episodeSteps": steps})
    env.run([agent_a, agent_b])
    r = [float(s.reward) for s in env.steps[-1]]
    return r

def main():
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    agents = {p: load(p) for p in CANDS}
    stats = {p: {"w": 0.0, "n": 0, "coins": 0.0} for p in CANDS}
    t0 = time.time()
    for i in range(len(CANDS)):
        for j in range(i + 1, len(CANDS)):
            pa, pb = CANDS[i], CANDS[j]
            for s in range(n_seeds):
                if s % 2 == 0:
                    r = episode(agents[pa], agents[pb], 100 + s)
                    my, oy = r[0], r[1]
                else:
                    r = episode(agents[pb], agents[pa], 100 + s)
                    my, oy = r[1], r[0]
                stats[pa]["n"] += 1
                stats[pa]["w"] += 1.0 if my > oy else (0.5 if my == oy else 0.0)
                stats[pa]["coins"] += my - oy
                stats[pb]["n"] += 1
                stats[pb]["w"] += 1.0 if oy > my else (0.5 if my == oy else 0.0)
                stats[pb]["coins"] += oy - my
            print(f"done {pa} vs {pb}  ({time.time()-t0:.0f}s)", flush=True)
    rows = sorted(stats.items(), key=lambda kv: (kv[1]["coins"] / max(kv[1]["n"], 1)), reverse=True)
    print("\n=== RANKING (by avg dCoins vs field) ===")
    for p, st in rows:
        n = max(st["n"], 1)
        print(f"{p:32s} wr={st['w']/n:.3f} dCoins={st['coins']/n:+9.0f} (n={st['n']})")
    json.dump({p: st for p, st in stats.items()}, open("harness/last_rr.json", "w"), indent=1)

if __name__ == "__main__":
    main()
