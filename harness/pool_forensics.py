"""Standalone _crop_pool forensics on a real replay step."""
import importlib.util
import json
import sys

spec = importlib.util.spec_from_file_location("v22dbg", r"c:\kaglab\bots\v22_dbg.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

d = json.load(open(r"c:\kaglab\replays\iter34\episode-104020214-replay.json"))
step = int(sys.argv[1]) if len(sys.argv) > 1 else 24
o = d["steps"][step][0]["observation"]
f = o["farms"][0]
day = step // 24
seeds = (o.get("private") or {}).get("seeds", {})
tiles = f["tiles"]
mc = sum(1 for row in tiles for t in row
         if isinstance(t, dict) and t.get("kind") == "PLANT"
         and t.get("crop") == "MELON")
print(f"step={step} day={day} melon_tiles={mc} seeds={seeds}")
counts = {"MELON": 0, "WHEAT": 0, "STRAWBERRY": 0}
for y, row in enumerate(tiles):
    for x, t in enumerate(row):
        if isinstance(t, dict) and t.get("kind") == "PLANT":
            crop = t.get("crop")
            if crop in counts:
                counts[crop] += 1
print("manual counts:", counts)
pool = mod._crop_pool(f, day, seeds, 12, False, 13, True, 6)
from collections import Counter
print("pool PLANTs:", Counter(t[3] for t in pool if t[0] == "PLANT"))
print("pool verbs:", Counter(t[0] for t in pool))
