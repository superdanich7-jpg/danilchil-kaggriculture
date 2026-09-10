"""Analyze iter35 replay results correctly."""
import json, glob, os

OUR_NAME = "DanilChil"
files = sorted(glob.glob(r"replays/iter35/*.json"))

wins, losses = 0, 0
print(f"Total replays: {len(files)}\n")

for f in files:
    d = json.load(open(f))
    names = d["info"]["TeamNames"]
    rewards = d["rewards"]
    ep_id = os.path.basename(f).replace("-replay.json", "")

    our_idx = None
    opp_name = None
    opp_idx = None
    for i, n in enumerate(names):
        if n == OUR_NAME:
            our_idx = i
        else:
            opp_name = n
            opp_idx = i

    our_score = rewards[our_idx]
    opp_score = rewards[opp_idx]

    if our_score > opp_score:
        result = "WIN"
        wins += 1
    else:
        result = "LOSS"
        losses += 1

    margin = our_score - opp_score
    print(f"{ep_id} | {result}: us={our_score:.0f} vs {opp_name}={opp_score:.0f} (margin={margin:+.0f})")

print(f"\nWins: {wins}, Losses: {losses}")