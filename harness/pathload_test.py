"""Why does path-loaded v97 die? Probe agent calls through the loader path."""
import io
import os
import sys
from contextlib import redirect_stdout, redirect_stderr

from kaggle_environments import make

buf_out, buf_err = io.StringIO(), io.StringIO()
env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': 1})
env.run(['bots/v97_oracle.py', 'random'])
r = env.steps[-1]
print(f'v97 path-load: seat0={r[0]["reward"]} seat1={r[1]["reward"]}')

# rerun capturing loader stderr (tracebacks swallowed by Agent.act)
err = io.StringIO()
with redirect_stdout(io.StringIO()), redirect_stderr(err):
    env2 = make('kaggriculture', configuration={'episodeSteps': 240, 'seed': 1})
    env2.run(['bots/v97_oracle.py', 'random'])
text = err.getvalue()
lines = [l for l in text.splitlines() if l.strip()]
print('captured loader output (last 25 lines):')
for line in lines[-25:]:
    print('   ', line[:160])
