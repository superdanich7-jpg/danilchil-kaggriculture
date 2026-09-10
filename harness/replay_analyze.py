"""Replay analyzer: per-day state of both farms + market prices.
Adapted for kaggriculture tile format (tiles contain {'crop','age','kind'} or None).
"""
import json
import sys
import glob
import os
# Force UTF-8 for console output with non-ASCII player names
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ME = "DanilChil"


def count_tiles(tiles, pred):
    return sum(1 for row in tiles for t in row if isinstance(t, dict) and pred(t))


def tile_kind(t):
    if t is None:
        return None
    if isinstance(t, str):
        return t
    if isinstance(t, dict):
        return t.get("kind")
    return None


def farm_stats(f, day):
    tiles = f.get("tiles", [])
    plants = {}
    for row in tiles:
        for t in row:
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                crop = t.get("crop", "?")
                plants[crop] = plants.get(crop, 0) + 1
    weeds = count_tiles(tiles, lambda t: tile_kind(t) == "WEED")
    structures = count_tiles(tiles, lambda t: isinstance(t, dict) and tile_kind(t) in ("PASTURE", "COOP"))
    herd = 0
    for row in tiles:
        for t in row:
            if isinstance(t, dict) and tile_kind(t) in ("PASTURE", "COOP"):
                if t.get("animal"):
                    herd += 1
    empty = sum(1 for row in tiles for t in row if t is None)
    money = f.get("money", 0)
    hands = len(f.get("hands", []))
    tiles_total = len(tiles) * len(tiles[0]) if tiles else 0
    utilization = (tiles_total - empty - weeds) / tiles_total if tiles_total else 0
    return weeds, plants, herd, empty, money, hands, utilization


def analyze(path):
    d = json.load(open(path))
    names = d["info"]["TeamNames"]
    rewards = d.get("rewards", [0, 0])
    me = names.index(ME) if ME in names else 0
    opp = 1 - me
    steps = d["steps"]

    print(f"\n=== {path.split(chr(92))[-1]} | {names[0]} vs {names[1]} ===")
    print(f"rewards: {rewards[me]:.0f} (me) vs {rewards[opp]:.0f} ({names[opp]})")
    result = "WIN" if rewards[me] > rewards[opp] else "LOSS"
    margin = rewards[me] - rewards[opp]
    print(f"Result: {result} (margin={margin:+.0f})")

    # Per-day snapshots
    for day in (0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 29):
        st_idx = min(day * 24 + 23, len(steps) - 1)
        # find the step for this day
        obs = None
        for s in steps[st_idx:st_idx+1]:
            if isinstance(s, list) and len(s) > 0:
                obs = s[0].get("observation", {})
        if not obs:
            continue
        farms = obs.get("farms")
        if not farms:
            continue
        wm, pm, hm, em, mm, hnd_m, util_m = farm_stats(farms[me], day)
        wo, po, ho, eo, mo, hnd_o, util_o = farm_stats(farms[opp], day)
        pm = {k: v for k, v in pm.items() if v}
        po = {k: v for k, v in po.items() if v}
        print(f"d{day:2d} ME  weeds={wm:3d} straw={pm.get('STRAWBERRY', 0):3d} "
              f"melon={pm.get('MELON', 0):3d} wheat={pm.get('WHEAT', 0):3d} "
              f"carrot={pm.get('CARROT', 0):3d} herd={hm:2d} hands={hnd_m} "
              f"empty={em:3d} util={util_m:.0%} money={mm:6.0f}")
        print(f"    OPP ({names[opp][:12]:12s}) weeds={wo:3d} straw={po.get('STRAWBERRY', 0):3d} "
              f"melon={po.get('MELON', 0):3d} wheat={po.get('WHEAT', 0):3d} "
              f"carrot={po.get('CARROT', 0):3d} herd={ho:2d} hands={hnd_o} "
              f"empty={eo:3d} util={util_o:.0%} money={mo:6.0f}")
    # prices at end
    o = steps[-1][0]["observation"] if steps and steps[-1] else {}
    pr = (o.get("market") or {}).get("prices", {})
    inv = (o.get("market") or {}).get("inventory", {})
    print("END prices:", {k: v for k, v in pr.items() if v})
    print("END market inv:", {k: v for k, v in inv.items() if v})
    mine = o.get("private", [None, None])
    if isinstance(mine, list) and len(mine) > me and mine[me]:
        mine = mine[me]
    elif isinstance(mine, dict):
        pass
    else:
        mine = {}
    if isinstance(mine, dict):
        shed = mine.get("shed", {})
        seeds = mine.get("seeds", {})
        print("MY shed end:", {k: v for k, v in shed.items() if v} if shed else {})
        print("MY seeds end:", {k: v for k, v in seeds.items() if v} if seeds else {})


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob(
        r"c:\kaglab\replays\iter35\*.json"))
    for f in files:
        analyze(f)

