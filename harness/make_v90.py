import ast

src = open('bots/v83.py', encoding='utf-8').read()

# v90: combined strategy —
#  clone-detect gate on the seat-lead layer. Mirror matches (both playing the
#  Shop-Router economy: opponent herd 12..20 at day 10) -> keep seat-lead ON
#  (it wins mirror tails). Foreign economies -> play the tape verbatim
#  (lead timing was tuned against mirrors; against other economies it breaks
#  our own delivery rhythm, cf. v87 fail).
OLD = """        view = FarmView(observation)
        tape = self.tapes[state.plan]
        action = copy.deepcopy(tape[step])
        repair_weeds(action, view, state, step)
        subtract_advanced_sales(action, state, step)
        advance_sales(action, view, state, tape, step)"""
assert OLD in src, 'act anchor missing'
NEW = """        if step == 240 and player == 1:
            # clone-detect at day 10: opponent herd size from visible farm
            opp_farm = observation["farms"][1 - player]
            herd = 0
            rows = opp_farm.get("tiles") or []
            for row in rows:
                tiles = row if isinstance(row, list) else [row]
                for tile in tiles:
                    if isinstance(tile, dict) and tile.get("kind") in ("COOP", "PASTURE"):
                        herd += 1
            state.lead_shift = 12 <= herd <= 20
        view = FarmView(observation)
        tape = self.tapes[state.plan]
        action = copy.deepcopy(tape[step])
        repair_weeds(action, view, state, step)
        subtract_advanced_sales(action, state, step)
        advance_sales(action, view, state, tape, step)"""
src = src.replace(OLD, NEW, 1)

open('bots/v90.py', 'w', encoding='utf-8').write(src)
ast.parse(src)

# v91: same gate + conservative lead depth 1 (was 2) in lead mode
src2 = src.replace(
    'next_step = step + (2 if getattr(state, "lead_shift", False) else 1)',
    'next_step = step + 1',
    1,
)
open('bots/v91.py', 'w', encoding='utf-8').write(src2)
ast.parse(src2)
print('v90 (clone-gate lead2) + v91 (clone-gate lead1) valid')
