import sys
from collections import defaultdict

sys.path.insert(0, 'harness')
from kaggle_environments import make

A, B = 'bots/v_iter47.py', 'bots/opp_mengfei.py'

for seed in range(3):
    env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': seed})
    env.run([A, B])
    vol = [defaultdict(int), defaultdict(int)]
    for st in env.steps:
        for seat in (0, 1):
            a = st[seat].action
            if isinstance(a, dict):
                for o in (a.get('market') or []):
                    if isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL':
                        vol[seat][o[1]] += int(o[2])
    rw = [float(s.reward) for s in env.steps[-1]]
    print(f'=== seed {seed}: us={rw[0]:.0f} mengfei={rw[1]:.0f} diff={rw[0]-rw[1]:+.0f}')
    for g in sorted(set(vol[0]) | set(vol[1])):
        print(f'  {g:11s} us={vol[0][g]:6d} mf={vol[1][g]:6d} diff={vol[0][g]-vol[1][g]:+6d}')
