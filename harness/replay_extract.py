"""Extract full 720-turn action history from a replay JSON.

Output format: list of 720 actions, one per turn (per agent).
Each action = dict with keys: 'market', 'farmer', 'hands', 'units'
or 'observation' for analysis.

Usage: py -3.12 harness/replay_extract.py <replay_path>
"""
import json
import sys

path = sys.argv[1]
d = json.load(open(path))

steps = d["steps"]
names = d["info"]["TeamNames"]
print(f"Players: {names}")
print(f"Total steps: {len(steps)}")

# Find which seat is DanilChil (ME)
me = 0 if "DanilChil" in names and names[1] == "DanilChil" else 0
# Actually DanilChil appears at index 0 or 1 depending on the episode
if names[0] == "DanilChil":
    me = 0
else:
    me = 1
opp = 1 - me
print(f"ME = {names[me]} (seat {me}), OPP = {names[opp]} (seat {opp})")

# Extract all actions from ME
me_actions = []
opp_actions = []

for i, s in enumerate(steps):
    me_action = s[me].get("action") or {}
    opp_action = s[opp].get("action") or {}
    me_actions.append(me_action)
    opp_actions.append(opp_action)

# Print summary
print(f"\nME actions: {len(me_actions)} turns")
print(f"OPP actions: {len(opp_actions)} turns")

# Show first 10 actions (day 0)
print("\n=== ME first 12 hours (day 0) ===")
for i in range(min(12, len(me_actions))):
    a = me_actions[i]
    market = a.get("market", [])
    farmer = a.get("farmer", [])
    hands = a.get("hands", [])
    print(f"  {i:3d} (h{i%24:2d}): market={market} farmer={farmer} hands={hands}")

# Show market actions by day
print("\n=== ME market actions by day ===")
from collections import defaultdict
day_market = defaultdict(list)
for i, a in enumerate(me_actions):
    day = i // 24
    m = a.get("market", [])
    if m:
        day_market[day].extend(m)

for day in sorted(day_market.keys())[:15]:
    print(f"  d{day:2d}: {day_market[day]}")

# Save to file
with open(f"replays/actions_{path.split('/')[-1].replace('-replay.json','')}.py", "w") as f:
    f.write(f"""# Extracted from {path.split('/')[-1]}
# ME = {names[me]}, OPP = {names[opp]}
# {len(me_actions)} turns

ME_ACTIONS = {json.dumps(me_actions, indent=2)}

OPP_ACTIONS = {json.dumps(opp_actions, indent=2)}
""")
print(f"\nSaved to replays/actions_{path.split('/')[-1].replace('-replay.json','')}.py")
