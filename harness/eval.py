import argparse, json, time
from kaggle_environments import make
def ep(a, b, seed, steps):
    t0 = time.time()
    try: env = make("kaggriculture", configuration={"episodeSteps": steps, "seed": seed})
    except Exception: env = make("kaggriculture", configuration={"episodeSteps": steps})
    env.run([a, b]); dt = time.time() - t0
    r = []
    for s in env.steps[-1]:
        obs = getattr(s, "observation", None) or {}
        shed = (obs.get("private") or {}).get("shed", {}) or {}
        pr = (obs.get("market") or {}).get("prices", {}) or {}
        r.append((float(s.reward), str(s.status),
                  sum(c * pr.get(k, 0) for k, c in shed.items() if isinstance(c, (int, float)))))
    return r, dt
def agg(champ, opp, seeds, steps):
    W = C = U = E = T = O = 0.0
    for s in range(seeds):
        a, b, me = (champ, opp, 0) if s % 2 == 0 else (opp, champ, 1)
        r, dt = ep(a, b, s, steps)
        (r0, s0, u0), (r1, s1, u1) = r
        my, oy, myst = (r0, r1, s0) if me == 0 else (r1, r0, s1)
        U += u0 if me == 0 else u1; T += dt; O += oy
        if myst != "DONE": E += 1; continue
        W += 1 if my > oy else (0.5 if my == oy else 0); C += my - oy
    n = max(seeds - E, 1)
    return {"wr": W / n, "delta": C / n, "unsold": U / n, "ocoins": O / n,
            "err": E / seeds, "sec": T / seeds}
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--champ", default="champ/main.py")
    ap.add_argument("--gate", default=None)
    ap.add_argument("--opp", default="random,starter")
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--steps", type=int, default=720)
    a = ap.parse_args()
    f = lambda x: x[5:] if x.startswith("file:") else x
    if a.gate:
        r = agg(a.champ, a.gate, a.seeds, a.steps)
        v = "PASS" if r["wr"] >= 0.55 and r["delta"] >= 0.03 * max(1, r["ocoins"]) else "FAIL"
        print(f"DUEL wr={r['wr']:.2f} dCoins={r['delta']:+.0f} unsold={r['unsold']:.0f} "
              f"err={r['err']:.2f} -> {v}")
        json.dump({"duel": r, "verdict": v}, open("harness/last_eval.json", "w"), indent=1)
    else:
        res = {}
        for opp in a.opp.split(","):
            r = agg(a.champ, f(opp), a.seeds, a.steps); res[opp] = r
            print(f"{opp:10s} wr={r['wr']:.2f} dCoins={r['delta']:+.0f} unsold={r['unsold']:.0f} "
                  f"err={r['err']:.2f} sec/ep={r['sec']:.1f}")
        json.dump(res, open("harness/last_eval.json", "w"), indent=1)
if __name__ == "__main__": main()