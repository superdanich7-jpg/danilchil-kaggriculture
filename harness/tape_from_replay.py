"""Extract a playable tape-agent from any replay seat.

Usage:
    py -3.12 harness/tape_from_replay.py <replay.json> <seat> [out_path]

Produces a python file with a single TAPES list (list of per-step
{"farmer":..,"hands":[...],"market":[...]} dicts) and an agent(obs) wrapper
that replays it verbatim (with +1 step alignment as verified earlier:
action recorded at step i is applied on transition (i-1)->i, so replay
lookup uses step index i for the action recorded at i).
"""
import json
import sys


def extract(replay_path: str, seat: int) -> list:
    d = json.load(open(replay_path))
    steps = d["steps"]
    n = d["configuration"]["episodeSteps"] - 1 if "configuration" in d else len(steps) - 1
    tape = []
    for i, st in enumerate(steps[:n]):
        act = st[seat]["action"]
        if isinstance(act, dict):
            tape.append(act)
        else:
            tape.append({"farmer": ["PASS"], "hands": [], "market": []})
    return tape


TMPL = '''"""Tape extracted from replay. Replays actions verbatim."""
import copy

TAPES = {tapes!r}
_LAST = len(TAPES[0]) - 1


def agent(obs, context=None):
    step = min(obs.get("step", 0), _LAST)
    return copy.deepcopy(TAPES[0][step])
'''


def main():
    replay, seat = sys.argv[1], int(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else f"bots/opp_tape_{replay.split('-')[1]}_{seat}.py"
    tape = extract(replay, seat)
    with open(out, "w", encoding="utf-8") as f:
        f.write(TMPL.format(tapes=[tape]))
    print(f"written {out} ({len(tape)} steps)")


if __name__ == "__main__":
    main()
