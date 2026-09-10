"""List all replay files with their opponent names."""
import json
import glob

for path in sorted(glob.glob("replays/iter*/episode-*.json")):
    try:
        d = json.load(open(path))
        names = d["info"]["TeamNames"]
        print(f"{path.split('/')[-1]:40s} {names}")
    except Exception as e:
        print(f"{path}: ERROR {e}")
