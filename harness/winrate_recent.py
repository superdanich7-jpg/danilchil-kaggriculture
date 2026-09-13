"""winrate_recent.py — W/L stats for the latest episodes of a submission.

Downloads the most recent episode replays of a submission, determines our
seat by team name, prints W/L per episode + opponent and a summary.
Usage: py -3.12 harness/winrate_recent.py [submission_id] [count]
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from kaggle.api.kaggle_api_extended import KaggleApi

ME = "DanilChil"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "replays", "recent")

api = KaggleApi()
api.authenticate()

sub_id = int(sys.argv[1]) if len(sys.argv) > 1 else 56147133
count = int(sys.argv[2]) if len(sys.argv) > 2 else 25

os.makedirs(OUT, exist_ok=True)

# 1. list recent episodes for this submission
eps = api.competition_list_episodes(sub_id)
ids = [e.id for e in eps][:count]

results = []
for eid in ids:
    path = os.path.join(OUT, f"{eid}.json")
    if not os.path.exists(path):
        try:
            api.competition_episode_replay(eid, path=OUT)
        except Exception:
            results.append((eid, "?", "DL-FAIL", 0, 0, 0))
            continue
    if not os.path.exists(path):
        # Kaggle may name files differently; look for any file containing eid
        cand = [f for f in os.listdir(OUT) if str(eid) in f]
        if cand:
            path = os.path.join(OUT, cand[0])
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        # maybe download created a different name
        results.append((eid, "?", "NOFILE", 0, 0, 0))
        continue
    names = d.get("info", {}).get("TeamNames", [])
    steps = d.get("steps", [])
    last = steps[-1]
    money = []
    for i, s in enumerate(last):
        obs = s.get("observation", {}) if isinstance(s, dict) else {}
        farm = (obs.get("farms") or [{}])[i] if i < len(obs.get("farms", [])) else {}
        # farms[0] belongs to seat 0; agents' own farms are in farms[pid]
        try:
            pid = obs.get("player", i)
            mv = obs["farms"][pid].get("money", 0)
        except Exception:
            mv = 0
        money.append(float(mv) + (float(obs.get("reward")) if obs.get("reward") else 0))
    seat = names.index(ME) if ME in names else -1
    if seat < 0:
        results.append((eid, names, "NAME?", 0, 0, 0))
        continue
    my = money[seat]
    opp = money[1 - seat]
    oname = names[1 - seat]
    r = "WIN" if my > opp else ("LOSS" if my < opp else "TIE")
    results.append((eid, r, oname, my, opp, my - opp))

wins = sum(1 for r in results if r[1] == "WIN")
losses = sum(1 for r in results if r[1] == "LOSS")
ties = sum(1 for r in results if r[1] == "TIE")
print(f"episode  result  opponent                            mine     opp")
for eid, r, on, my, opp, diff in results:
    print(f"{eid}  {r:5} {on[:32]:32} {my:9.0f} {opp:9.0f} d={my - opp:+.0f}")
print(f"\nW={wins} L={losses} T={ties} wr={wins / max(1, wins + losses):.2f}")
