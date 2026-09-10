"""scan_daily.py — daily measurement pipeline for Kaggriculture.

Reproduces the "tape ladder" meta from the competition discussion.
Every day Kaggle publishes the previous day's top episodes as a dataset
(kaggle/kaggriculture-episodes-YYYY-MM-DD). This script:

1. Reads the live leaderboard (top-N teams by score).
2. Downloads the daily episode dataset (unless already present).
3. Scans every episode; when a top-N team participates, extracts that
   team's 720-turn action tape and builds a standalone tape agent.
4. Duels our champ (champ/main.py) against the top team's tape ON THE
   EPISODE'S OWN SEED (same market/town layout).
5. Prints a table: top team, LB score, our winrate + average delta.

Usage:
    py -3.12 harness/scan_daily.py --date 2026-09-09 --top 10 [--seed-only]
"""
import argparse
import json
import os

from kaggle.api.kaggle_api_extended import KaggleApi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHAMP = os.path.join(ROOT, "champ", "main.py")
DL_DIR = os.path.join(ROOT, "replays", "daily")


def leaderboard_top(n):
    a = KaggleApi()
    a.authenticate()
    rows = a.competition_leaderboard_view("kaggriculture", page_size=200)
    out = {}
    for r in rows:
        name = r.team_name
        try:
            score = float(r.score)
        except (TypeError, ValueError):
            continue
        if name and score:
            out[name] = score
        if len(out) >= n:
            break
    return out


def download_dataset(ds, dest):
    os.makedirs(dest, exist_ok=True)
    a = KaggleApi()
    a.authenticate()
    files = [f.name for f in a.dataset_list_files(ds).files]
    got = set(os.listdir(dest))
    for fn in files:
        p = os.path.join(dest, fn)
        if fn not in got:
            a.dataset_download_file(ds, fn, path=dest, force=True)
    return sorted(os.path.join(dest, f) for f in os.listdir(dest))


def episode_info(path):
    d = json.load(open(path))
    info = d.get("info", {})
    return {
        "id": os.path.basename(path).removesuffix(".json"),
        "names": info.get("TeamNames", []),
        "seed": info.get("seed"),
        "steps": len(d.get("steps", [])),
    }


def build_tape(path, seat, out_path):
    """Write a self-contained tape agent replaying `seat` by step number."""
    d = json.load(open(path))
    steps = d["steps"]
    acts = []
    for s in steps:
        a = s[seat].get("action") if isinstance(s[seat], dict) else {}
        acts.append(a or {})
    code = ('"""Tape agent: %s (episode %s seat %d). scan_daily.py."""\n'
            "ACTIONS = %s\n\n"
            'def agent(obs):\n'
            '    try:\n'
            '        s = obs.get("step")\n'
            '        if s is None:\n'
            '            s = int(obs.get("day", 0)) * 24 + int(obs.get("hour", 0))\n'
            '        s = int(s)\n'
            '        # REPLAY ALIGNMENT FIX: the action stored at step i of the\n'
            '        # episode JSON was generated from the observation at step i-1\n'
            '        # (its market effects are already visible at step i), so when\n'
            '        # the agent receives obs at step s it must return ACTIONS[s+1].\n'
            '        j = s + 1\n'
            '        a = ACTIONS[j] if 0 <= j < len(ACTIONS) else (ACTIONS[-1] if ACTIONS else {})\n'
            '        return {"farmer": a.get("farmer") or ["PASS"],\n'
            '                "hands": a.get("hands") or [],\n'
            '                "market": a.get("market") or []}\n'
            '    except Exception:\n'
            '        return {"farmer": ["PASS"], "hands": [], "market": []}\n')
    code = code % (d["info"]["TeamNames"][seat],
                   os.path.basename(path), seat, json.dumps(acts))
    open(out_path, "w", encoding="utf-8").write(code)
    return out_path


def duel_one(champ, tape, seed, seat_of_top):
    """champ vs tape on a fixed seed; top team is seat_of_top in original."""
    from kaggle_environments import make
    a, b = (champ, tape) if seat_of_top == 1 else (tape, champ)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    env.run([a, b])
    r = []
    for s in env.steps[-1]:
        obs = getattr(s, "observation", None) or {}
        pr = (obs.get("market") or {}).get("prices", {}) or {}
        shed = (obs.get("private") or {}).get("shed", {}) or {}
        r.append((float(s.reward), str(s.status),
                  sum(c * pr.get(k, 0) for k, c in shed.items()
                      if isinstance(c, (int, float)))))
    my, oy = (r[0], r[1]) if seat_of_top == 1 else (r[1], r[0])
    return my[0], oy[0], my[1], oy[1], my[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-09-09")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--min-score", type=float, default=2000.0)
    ap.add_argument("--list-only", action="store_true",
                    help="only list matching episodes, skip duels")
    ap.add_argument("--limit", type=int, default=200)
    a = ap.parse_args()
    ds = f"kaggle/kaggriculture-episodes-{a.date}"
    dest = os.path.join(DL_DIR, a.date.replace("-", ""))
    print(f"[scan_daily] dataset={ds} top={a.top} minScore={a.min_score:.0f}")
    top = leaderboard_top(200)
    targets = {k: v for k, v in top.items() if v >= a.min_score}
    print(f"[scan_daily] leaderboard: {len(top)} teams, "
          f"{len(targets)} above {a.min_score:.0f}")
    topnames = set(targets)
    episodes = download_dataset(ds, dest)
    print(f"[scan_daily] downloaded {len(episodes)} episodes")
    os.makedirs(os.path.join(ROOT, "flight", "tapes"), exist_ok=True)
    results = []
    for path in sorted(episodes):
        ep = episode_info(path)
        matches = [i for i, nm in enumerate(ep["names"]) if nm in topnames]
        if not matches:
            continue
        label = " <-> ".join(
            f"{nm} ({targets.get(nm, 0):.0f})" if nm in topnames else nm
            for nm in ep["names"])
        print(f"\n=== episode {ep['id']} seed={ep['seed']} :: {label}",
              flush=True)
        if a.list_only:
            results.append((ep["id"], ep["names"], ep["seed"]))
            continue
        for seat in matches:
            topnm = ep["names"][seat]
            tape = os.path.join(ROOT, "flight", "tapes",
                                f"tape_{ep['id']}_{seat}.py")
            if not os.path.exists(tape):
                build_tape(path, seat, tape)
            try:
                my, oy, ms, os_, _u = duel_one(CHAMP, tape, ep["seed"], seat)
                w = "WIN " if my > oy else ("TIE " if my == oy else "LOSS")
                print(f"  {w} vs {topnm:22s} seat{seat} seed={ep['seed']} "
                      f"we={my:.0f} opp={oy:.0f} (status {ms}/{os_})",
                      flush=True)
                results.append((topnm, targets.get(topnm, 0),
                                1 if my > oy else 0, my, oy, ep["seed"]))
            except Exception as e:
                print(f"  ERR vs {topnm}: {e}", flush=True)
    if a.list_only:
        return
    print("\n=== SUMMARY ===")
    agg = {}
    for name, score, w, my, oy, seed in results:
        r = agg.setdefault(name, [0, 0.0, 0.0, 0, score])
        r[0] += 1
        r[1] += w
        r[2] += my - oy
        r[3] += 1 if my > oy else 0
    for name, (n, wsum, dsum, wins, score) in sorted(
            agg.items(), key=lambda kv: -kv[1][4]):
        print(f"  {name:22s} lb={score:7.0f} games={n:2d} wr={wsum / n:.2f} "
              f"avgDelta={dsum / n:+.0f} wins={wins}")


if __name__ == "__main__":
    main()