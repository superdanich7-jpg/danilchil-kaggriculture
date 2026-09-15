"""Dump first actions from path-loaded v97 vs lime."""
import io
import sys
from contextlib import redirect_stderr

from kaggle_environments import agent as agent_mod
from kaggle_environments import make

orig_act = agent_mod.Agent.act
seen = [0]


def traced_act(self, observation):
    result = orig_act(self, observation)
    if seen[0] < 12:
        act = result[0]
        if not isinstance(act, BaseException):
            market = (act.get('market') if isinstance(act, dict) else None) or []
            print(f'turn {seen[0]}: {len(market)} orders: {market[:4]}')
        seen[0] += 1
    return result


agent_mod.Agent.act = traced_act
for name in ('bots/v97_oracle.py', 'bots/v96_lime.py'):
    seen[0] = 0
    print('===', name)
    with redirect_stderr(io.StringIO()):
        env = make('kaggriculture', configuration={'episodeSteps': 120, 'seed': 1})
        env.run([name, 'random'])
    r = env.steps[-1]
    print('rewards:', r[0]['reward'], r[1]['reward'])
