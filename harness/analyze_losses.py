"""Analyze our losses: opponent animals, hands, utilization."""
import json, glob, os
from collections import defaultdict

loss_dir = "replays/iter47_losses"
files = sorted(glob.glob(f"{loss_dir}/*.json"))

for f in files:
    d = json.load(open(f))
    info = d["info"]
    opp_name = info.get("TeamNames", [None, None])[0]
    steps = d["steps"]
    opp = 0
    
    anim_last = sum(1 for row in steps[-1][opp]["observation"]["farms"][opp]["tiles"]
                    for t in row if isinstance(t, dict) and t.get("animal"))
    hands_last = len(steps[-1][opp]["action"].get("hands", []))
    
    total_tiles = len(steps[0][opp]["observation"]["farms"][opp]["tiles"])
    util_last = sum(1 for row in steps[-1][opp]["observation"]["farms"][opp]["tiles"] if row)
    util_pct = util_last / total_tiles * 100 if total_tiles > 0 else 0
    
    # money
    money_opp = int(steps[-1][opp]["observation"]["farms"][opp]["money"])
    money_me = int(steps[-1][1]["observation"]["farms"][1]["money"])
    
    print(f"{os.path.basename(f):30s} opp={opp_name:20s} anim={anim_last:2d} hands={hands_last:2d} util={util_pct:5.1f}% opp_money={money_opp:6d} me_money={money_me:6d}")
