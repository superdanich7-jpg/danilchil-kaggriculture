"""Instrument the loader path: monkeypatch get_last_callable + trace agent call errors."""
import io
import os
import sys

from kaggle_environments import agent as agent_mod
from kaggle_environments import make

orig = agent_mod.get_last_callable


def traced(raw, fallback=None, path=None):
    fn = orig(raw, fallback=fallback, path=path)
    if path and 'v97' in str(path):
        print(f'[loader] picked {getattr(fn, "__name__", "?")} for {path}')
    return fn


agent_mod.get_last_callable = traced

# also trace what the agent returns each call
env = make('kaggriculture', configuration={'episodeSteps': 120, 'seed': 1})
orig_agent_cls_act = agent_mod.Agent.act


def traced_act(self, observation):
    result = orig_agent_cls_act(self, observation)
    if isinstance(result[0], BaseException):
        print('[agent ERROR]', repr(result[0])[:300])
    return result


agent_mod.Agent.act = traced_act
env.run(['bots/v97_oracle.py', 'random'])
r = env.steps[-1]
print(f'v97 short-run: seat0={r[0]["reward"]} seat1={r[1]["reward"]}')
