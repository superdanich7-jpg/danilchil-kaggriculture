import inspect
import kaggle_environments.envs.kaggriculture.kaggriculture as m

for fname in ['_commit_unit', '_do_hire', '_apply_unit_action']:
    print(f'===== {fname} =====')
    print(inspect.getsource(getattr(m, fname)))