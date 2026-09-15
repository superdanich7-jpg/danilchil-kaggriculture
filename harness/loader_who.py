"""Which callable does the loader pick from v97_oracle?"""
import os
import sys

sys.stderr = open(os.devnull, 'w')
from kaggle_environments.agent import get_last_callable

src = open('bots/v97_oracle.py', encoding='utf-8').read()
fn = get_last_callable(src, path='bots/v97_oracle.py')
print('loader picked:', getattr(fn, '__name__', '?'))
print('qualname:', getattr(fn, '__qualname__', '?'))
