"""Find the exact source line of the NameError."""
import io
import sys
import traceback

from kaggle_environments import agent as agent_mod
from kaggle_environments import make

orig_act = agent_mod.Agent.act


def traced_act(self, observation):
    result = orig_act(self, observation)
    if isinstance(result[0], BaseException):
        exc = result[0]
        tb = traceback.extract_tb(exc.__traceback__) if exc.__traceback__ else []
        print('[agent ERROR]', repr(exc))
        for frame in tb[-6:]:
            print(f'   {frame.filename}:{frame.lineno} in {frame.name}: {frame.line}')
    return result


agent_mod.Agent.act = traced_act
env = make('kaggriculture', configuration={'episodeSteps': 120, 'seed': 1})
env.run(['bots/v97_oracle.py', 'random'])
r = env.steps[-1]
print('rewards:', r[0]['reward'], r[1]['reward'])
