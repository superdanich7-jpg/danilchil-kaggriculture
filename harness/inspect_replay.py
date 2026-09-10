"""Inspect replay structure."""
import json, sys

path = sys.argv[1]
d = json.load(open(path))
steps = d["steps"]
names = d["info"]["TeamNames"]
print("TeamNames:", names)
print("rewards:", d.get("rewards"))

o = steps[0][0]["observation"]
print("day:", o.get("day"))
print("hour:", o.get("hour"))
print("farms type:", type(o.get("farms")))
farms = o.get("farms")
if isinstance(farms, list) and len(farms) > 0:
    print("farm[0] keys:", list(farms[0].keys()) if isinstance(farms[0], dict) else "N/A")
    tiles = farms[0].get("tiles", [])
    print("tiles shape:", len(tiles), "x", len(tiles[0]) if tiles else 0)
    if tiles and len(tiles) > 4:
        t = tiles[4][4]
        print("tile[4][4]:", t)
pr = o.get("market", {}).get("prices", {})
print("prices:", {k: v for k, v in pr.items() if v})
