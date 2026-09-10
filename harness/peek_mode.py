import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else \
    r"c:/kaglab/replays/iter34/episode-104020214-replay.json"
d = json.load(open(path))
for step in (0, 12, 23, 24, 47, 71):
    o = d["steps"][step][0]["observation"]
    me = o["farms"][0]["tiles"]
    op = o["farms"][1]["tiles"]

    def cnt(ts, crop):
        return sum(1 for row in ts for t in row
                   if isinstance(t, dict) and t.get("kind") == "PLANT"
                   and t.get("crop") == crop)
    oa = sum(1 for row in op for t in row
             if isinstance(t, dict) and t.get("animal"))
    print(f"step {step} (d{step//24} h{step%24}): "
          f"opp_melon={cnt(op,'MELON')} my_melon={cnt(me,'MELON')} "
          f"opp_straw={cnt(op,'STRAWBERRY')} opp_anim={oa}")
