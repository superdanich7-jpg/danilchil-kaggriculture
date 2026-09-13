import ast

src = open('bots/v80.py', encoding='utf-8').read()

old = (
    "    prices=obs['market']['prices']\n"
    "    market=[list(order) for order in action.get('market',[])[:MAX_ORDERS]]\n"
    "    money=int(obs['farms'][player]['money'])"
)
assert old in src, 'anchor1 missing'
new = (
    "    prices=obs['market']['prices']\n"
    "    market=[list(order) for order in action.get('market',[])[:MAX_ORDERS]]\n"
    "    money=int(obs['farms'][player]['money'])\n"
    "    # rubber-band: deviate only when meaningfully behind the opponent\n"
    "    behind=money+3000<int(obs['farms'][1-player]['money'])\n"
    "    if not behind:\n"
    "        action=copy.deepcopy(action);action['market']=market\n"
    "        return action"
)
src = src.replace(old, new, 1)

# telemetry counters for rubber-band usage
src = src.replace(
    "_V230_REPORT=dict(_V228_REPORT,price_deferrals=0,forward_keeps=0,cow_topups=0,\n    cow_topup_declines=0)",
    "_V230_REPORT=dict(_V228_REPORT,price_deferrals=0,forward_keeps=0,cow_topups=0,\n    cow_topup_declines=0,behind_turns=0)",
    1,
)
src = src.replace(
    "    # rubber-band: deviate only when meaningfully behind the opponent\n",
    "    # rubber-band: deviate only when meaningfully behind the opponent\n"
    "    _V230_REPORT['behind_turns']+=1\n",
    1,
)

open('bots/v81.py', 'w', encoding='utf-8').write(src)
ast.parse(src)
print('v81 (rubber-band) valid')
