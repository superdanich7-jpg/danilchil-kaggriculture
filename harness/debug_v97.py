"""Debug v97_oracle: run one episode, check agent health + telemetry."""
import importlib.util
import sys
from kaggle_environments import make

sys.path.insert(0, 'harness')

spec = importlib.util.spec_from_file_location('v97', 'bots/v97_oracle.py')
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    print('IMPORT OK')
    print('has agent:', hasattr(mod, 'agent'), callable(getattr(mod, 'agent', None)))
except Exception as exc:
    import traceback
    traceback.print_exc()
    print('IMPORT FAILED:', exc)
    sys.exit(1)

env = make('kaggriculture', configuration={}, debug=True)
env.run([mod.agent, 'random'])
final = env.steps[-1]
print('rewards:', final[0]['reward'], final[1]['reward'])
print('statuses:', final[0]['status'], final[1]['status'])

# call agent directly on a real observation to surface swallowed exceptions
obs = final[0]['observation']
try:
    act = mod.agent(obs, env.configuration)
    market = act.get('market', []) or []
    print('direct call OK, market orders:', len(market))
    for order in market[:5]:
        print('  order:', order)
except Exception:
    import traceback
    traceback.print_exc()

print('telemetry:', {k: v for k, v in mod._ORCL_REPORT.items() if v})
