"""Quick summary of iter36 replays in a folder (win/loss + rewards)."""
import json, glob, os, sys

ME = "DanilChil"
files = sorted(glob.glob(r"replays/iter36/*.json"))
wins = losses = 0
for f in files:
    d = json.load(open(f))
    names = d["info"]["TeamNames"]
    rewards = d.get("rewards", [0, 0])
    our_idx = names.index(ME) if ME in names else 0
    opp_idx = 1 - our_idx
    us, op = rewards[our_idx], rewards[opp_idx]
    res = "WIN" if us > op else "LOSS"
    if us > op:
        wins += 1
    else:
        losses += 1
    ep = os.path.basename(f).replace("-replay.json", "")
    print(f"{ep} | {res} | us={us:.0f} opp({names[opp_idx]})={op:.0f} margin={us-op:+.0f}")
print(f"\nW: {wins} L: {losses}")