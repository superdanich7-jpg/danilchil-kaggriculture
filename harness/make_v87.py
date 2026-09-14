import ast
import json
import re

SRC = 'bots/opp_mengfei.py'
DST = 'bots/v87.py'

src = open(SRC, encoding='utf-8').read()

m = re.search(r'ACTIONS = (\[.*?\])\n\ndef agent', src, re.S)
assert m, 'ACTIONS not found'
raw = m.group(1)
# json.dumps wrote true/false/null
py = re.sub(r'\btrue\b', 'True', raw)
py = re.sub(r'\bfalse\b', 'False', py)
py = re.sub(r'\bnull\b', 'None', py)
actions = eval(py)
assert isinstance(actions, list) and len(actions) > 700

# shift: every SELL planned at step s is executed at step s-1 (data-level).
n = len(actions)
sells = []
for s in range(n):
    mk = (actions[s].get('market') or []) if isinstance(actions[s], dict) else []
    sells.append([list(o) for o in mk if isinstance(o, list) and o and o[0] == 'SELL'])

new_actions = []
for s in range(n):
    a = actions[s] if isinstance(actions[s], dict) else {}
    mk = [list(o) for o in (a.get('market') or []) if isinstance(o, list) and o and o[0] != 'SELL']
    if s + 1 < n:
        mk.extend(sells[s + 1])
    na = dict(a)
    na['market'] = mk
    new_actions.append(na)

body = 'ACTIONS = ' + json.dumps(new_actions) + '\n\n\ndef agent(obs):\n'
tail = src[m.end():]
agent_code = re.search(r'def agent\(obs\):.*', src, re.S).group(0)
out = src[:m.start()] + 'ACTIONS = ' + json.dumps(new_actions) + '\n\n\n' + agent_code
open(DST, 'w', encoding='utf-8').write(out)
ast.parse(open(DST, encoding='utf-8').read())
print('v87 (mengfei data-level sell shift -1) valid, actions:', len(new_actions))
