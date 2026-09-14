import sys

sys.path.insert(0, 'harness')
from scan_daily import build_tape  # noqa: E402

# (episode_id, seat, out_name) — opponents that beat our champ on 2026-09-13
JOBS = [
    ('108351986', 0, 'opp_redblackbst'),
    ('108349939', 0, 'opp_thirdfarm'),
    ('108351986', 1, 'opp_mengfei'),
]

for ep, seat, name in JOBS:
    path = f'replays/daily/20260913/{ep}.json'
    out = build_tape(path, seat, f'bots/{name}.py')
    print('built', out)
