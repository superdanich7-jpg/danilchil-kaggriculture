import ast

src = open('bots/v90.py', encoding='utf-8').read()

# v92: combined router — when the detected mirror-opponent is also RICH
# (money > ours at d10), switch our tape to the strongest foreign economy
# (mengfei ACTIONS embedded); otherwise keep the Shop-Router plan.
# The foreign tape is only used in clone-rich matchups, where offline duels
# proved +43k vs mengfei-level and +22k vs our own base.

# 1) embed mengfei actions at module scope
meng = open('bots/opp_mengfei.py', encoding='utf-8').read()
import re
am = re.search(r'ACTIONS = (\[.*?\])\n\ndef agent', meng, re.S)
assert am, 'mengfei ACTIONS not found'
mf_actions = am.group(1)

anchor = '_INLINE_TAPES = json.loads('
assert anchor in src, 'inline tapes anchor missing'
src = src.replace(anchor, 'MENGFEI_ACTIONS = ' + mf_actions + '\n\n' + anchor, 1)

# 2) extend the d10 gate: keep lead only vs mirror herds, and switch to the
#    foreign tape when the opponent is ALSO rich (both are clones/strong).
OLD_GATE = """        if step == 240 and player == 1:
            # clone-detect at day 10: opponent herd size from visible farm
            opp_farm = observation["farms"][1 - player]
            herd = 0
            rows = opp_farm.get("tiles") or []
            for row in rows:
                tiles = row if isinstance(row, list) else [row]
                for tile in tiles:
                    if isinstance(tile, dict) and tile.get("kind") in ("COOP", "PASTURE"):
                        herd += 1
            state.lead_shift = 12 <= herd <= 20"""
assert OLD_GATE in src, 'gate anchor missing'
NEW_GATE = """        if step == 240 and player == 1:
            # clone-detect at day 10: opponent herd size + money from visible farm
            opp_farm = observation["farms"][1 - player]
            herd = 0
            rows = opp_farm.get("tiles") or []
            for row in rows:
                tiles = row if isinstance(row, list) else [row]
                for tile in tiles:
                    if isinstance(tile, dict) and tile.get("kind") in ("COOP", "PASTURE"):
                        herd += 1
            mirror = 12 <= herd <= 20
            rich = int(opp_farm.get("money") or 0) > int(observation["farms"][player].get("money") or 0) * 1.3
            state.lead_shift = mirror
            state.use_foreign = bool(mirror and rich)
"""
src = src.replace(OLD_GATE, NEW_GATE, 1)

# 3) honor the switch in tape selection
OLD_TAPE = """        view = FarmView(observation)
        tape = self.tapes[state.plan]
        action = copy.deepcopy(tape[step])"""
assert OLD_TAPE in src, 'tape anchor missing'
NEW_TAPE = """        view = FarmView(observation)
        if getattr(state, "use_foreign", False):
            tape = MENGFEI_ACTIONS
        else:
            tape = self.tapes[state.plan]
        action = copy.deepcopy(tape[step])"""
src = src.replace(OLD_TAPE, NEW_TAPE, 1)

open('bots/v92.py', 'w', encoding='utf-8').write(src)
ast.parse(src)
print('v92 (router + rich-mirror -> mengfei switch) valid')
