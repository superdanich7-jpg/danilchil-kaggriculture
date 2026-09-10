"""probe_tape.py — log obs.step & exceptions inside the tape agent calls."""
import importlib.util
import json
import sys
import traceback

from kaggle_environments import make

EPID = sys.argv[1] if len(sys.argv) > 1 else "106946631"
DAILY = r"c:\kaglab\replays\daily\20260909"
TAPE_DIR = r"c:\kaglab\flight\tapes"

d = json.load(open(f"{DAILY}\\{EPID}.json"))
seed = d["info"]["seed"]

spec = importlib.util.spec_from_file_location("tape_mod", f"{TAPE_DIR}\\tape_{EPID}_0.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
inner = mod.agent

LOG = []


def probed(obs):
    keys = list(obs.keys())[:12]
    step = obs.get("step", "MISSING")
    day = obs.get("day", "MISSING")
    hour = obs.get("hour", "MISSING")
    try:
        r = inner(obs)
    except Exception as e:
        LOG.append(f"EXC step={step} day={day} hour={hour}: {e!r}")
        r = {"farmer": ["PASS"], "hands": [], "market": []}
    if len(LOG) < 6:
        LOG.append(f"call: step={step!r} day={day!r} hour={hour!r} keys={keys} "
                   f"-> market={json.dumps(r.get('market'))[:80]}")
    return r


a1 = None
spec1 = importlib.util.spec_from_file_location("tape_mod1", f"{TAPE_DIR}\\tape_{EPID}_1.py")
m1 = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(m1)

env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
env.run([probed, m1.agent])
print("\n".join(LOG))

