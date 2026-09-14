import ast

src = open('bots/v83.py', encoding='utf-8').read()

# v89: seat-lead v3 —
#  1) FERTILIZER joins the seat-1 lead shift (linear 0.4 impact but ~10k units
#     sold; timing edge compounds), WHEAT stays excluded (log impact);
#  2) rubber-band threshold 3000 -> 2000 (react earlier to falling behind).
old = """    skip = ("WHEAT", "FERTILIZER")
    lead = getattr(state, "lead_shift", False)"""
assert old in src, 'skip anchor missing'
new = """    lead = getattr(state, "lead_shift", False)
    skip = ("WHEAT",) if lead else ("WHEAT", "FERTILIZER")"""
src = src.replace(old, new, 1)

old2 = "behind=money+3000<int(obs['farms'][1-player]['money'])"
assert old2 in src, 'rubber anchor missing'
new2 = "behind=money+2000<int(obs['farms'][1-player]['money'])"
src = src.replace(old2, new2, 1)

open('bots/v89.py', 'w', encoding='utf-8').write(src)
ast.parse(src)
print('v89 (seat-lead v3) valid')
