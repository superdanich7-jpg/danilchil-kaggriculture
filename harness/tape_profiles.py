import sys

sys.path.insert(0, '.')
# import the tape-router champ (iter47 clean)
import importlib.util

spec = importlib.util.spec_from_file_location('i47', 'bots/v_iter47.py')
mod = importlib.util.module_from_spec(spec)
sys.modules['i47'] = mod
spec.loader.exec_module(mod)

tapes = mod._INLINE_TAPES
plans = getattr(mod, 'SHOP_PLANS', {})

print('tapes:', len(tapes))
for idx, t in enumerate(tapes):
    from collections import Counter
    c = Counter()
    for a in t:
        for o in (a.get('market') or []):
            if isinstance(o, list) and o and o[0] in ('SELL', 'BUY_SEED', 'BUY_ANIMAL') and len(o) > 1:
                c[(o[0], o[1])] += 1
    top = ', '.join(f'{k[1]}:{v}' for k, v in c.most_common(6))
    print(f'plan {idx:2d} shops={list(plans.keys())[idx] if idx < len(plans) else "?"} | {top}')
