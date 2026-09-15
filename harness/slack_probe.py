"""Measure idle capacity (PASS commands) and tile mix of our champ per day.

Used to size the late-game "deficit crop" engine (V232): how many hand-actions
per day are actually free for carrot/wheat cycles on top of the tape's plan.
"""
import importlib.util
import json
import sys
from collections import Counter, defaultdict

from kaggle_environments import make

PATH = sys.argv[1] if len(sys.argv) > 1 else 'champ/main.py'
SEEDS = [int(sys.argv[2])] if len(sys.argv) > 2 else [0, 1]

spec = importlib.util.spec_from_file_location('champ_mod', PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

records = defaultdict(list)
snapshots = defaultdict(dict)
_agent = mod.agent


def wrap(player):
    def agent_fn(observation, configuration=None):
        action = _agent(observation, configuration)
        step = int(observation['step'])
        records[player].append((step, action))
        if step % 24 == 23:
            farm = observation['farms'][player]
            kinds = Counter()
            crops = Counter()
            for row in farm['tiles']:
                for tile in row:
                    if isinstance(tile, dict):
                        kinds[tile.get('kind')] += 1
                        if tile.get('kind') == 'PLANT':
                            crops[tile.get('crop')] += 1
                    elif isinstance(tile, str):
                        kinds[tile] += 1
            snapshots[step // 24][player] = dict(
                money=int(farm['money']), hands=len(farm['hands']),
                tiles=sum(kinds.values()), kinds=dict(kinds), crops=dict(crops),
                quadrants=list(farm['unlocked_quadrants']),
                shed=dict((observation['private']['shed'] or {})),
                prices=dict(observation['market']['prices']),
            )
        return action
    return agent_fn


for seed in SEEDS:
    records.clear()
    snapshots.clear()
    env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': seed})
    env.run([wrap(0), wrap(1)])
    print(f'=== seed={seed} final={[s.reward for s in env.steps[-1]]}')
    per_day = defaultdict(lambda: defaultdict(int))
    for player, seq in records.items():
        for step, action in seq:
            day = step // 24
            if day < 15:
                continue
            commands = [action.get('farmer') or ['PASS'], *(action.get('hands') or [])]
            for cmd in commands:
                head = cmd[0] if cmd else 'PASS'
                per_day[day][head] += 1
    for day in sorted(per_day):
        snap = snapshots[day]
        row = per_day[day]
        total = sum(row.values())
        idle = row.get('PASS', 0)
        mix = snap.get(0, {})
        print(f'  d{day}: actions={total} PASS={idle} ({idle / max(1, total):.0%})'
              f' WATER={row.get("WATER", 0)} HARVEST={row.get("HARVEST", 0)}'
              f' PLANT={row.get("PLANT", 0)} | money={mix.get("money")}'
              f' crops={mix.get("crops")} kinds={mix.get("kinds")}'
              f' q={mix.get("quadrants")}')