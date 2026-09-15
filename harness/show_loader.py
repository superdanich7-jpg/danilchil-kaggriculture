"""Inspect kaggle_environments agent loader."""
import inspect
import kaggle_environments.agent as A

print('=== build_agent ===')
print(inspect.getsource(A.build_agent))
print('=== other loader funcs ===')
for name in dir(A):
    if 'load' in name.lower() or 'compile' in name.lower() or 'agent' in name.lower():
        obj = getattr(A, name)
        if callable(obj):
            try:
                src = inspect.getsource(obj)
                print(f'--- {name} ---')
                print(src[:1500])
            except Exception as exc:
                print(name, 'no source:', exc)
