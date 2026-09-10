import inspect, json
import kaggle_environments.envs.kaggriculture.kaggriculture as m

print("===== ANIMALS =====")
print(json.dumps(m.ANIMALS, default=str, indent=1))

print("===== COLLECT_FERTILIZER source =====")
src = inspect.getsource(m._apply_unit_action)
lines = src.split('\n')
for i, l in enumerate(lines):
    if l.strip().startswith('if op == "COLLECT_FERTILIZER"'):
        print('\n'.join(lines[i:i+10]))

# Try common names for market params
print("===== MARKET_PARAMS candidates =====")
for name in dir(m):
    if any(k in name for k in ['MARKET', 'PRICE', 'PARAM', 'IMPACT']):
        try:
            val = getattr(m, name)
            if isinstance(val, dict):
                for p in ['MILK','WOOL','EGG','FERTILIZER','WHEAT']:
                    if p in val:
                        print(name, p, val[p])
        except Exception:
            pass
