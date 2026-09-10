"""Fix v24.py indentation and seed buying properly."""
with open("bots/v24.py", encoding="utf-8") as f:
    lines = f.readlines()

# Fix lines around the n_anim_hands block (find it dynamically)
for i, l in enumerate(lines):
    stripped = l.lstrip()
    if stripped.startswith('if herd <= 4:'):
        lines[i] = '        if herd <= 4:\n'
    elif stripped.startswith('n_anim_hands = 2') and i > 0 and 'if herd' in lines[i-1]:
        lines[i] = '            n_anim_hands = 2\n'
    elif stripped.startswith('elif herd <= 9:'):
        lines[i] = '        elif herd <= 9:\n'
    elif stripped.startswith('n_anim_hands = 3') and i > 0 and 'elif herd' in lines[i-1]:
        lines[i] = '            n_anim_hands = 3\n'
    elif stripped.startswith('else:'):
        lines[i] = '        else:\n'
    elif stripped.startswith('n_anim_hands = 3') and i > 0 and 'else:' in lines[i-1]:
        lines[i] = '            n_anim_hands = 3  # ITER35: was 5 - 17-18 animals starved the\n'
    elif stripped.startswith('# engine of labor. ITER36'):
        lines[i] = '            # engine of labor. ITER36: kept 3 - 4 crop workers couldn\'t\n'
    elif stripped.startswith('# water 30+') and 'ITER36' in lines[i-1] or (i > 0 and 'couldn' in lines[i-1]):
        lines[i] = '            # water 30+ strawberry tiles (33 weeds in offline test)\n'
    elif stripped.startswith('enemy_melons = _scan'):
        lines[i] = '        enemy_melons = _scan_opponent_crops(obs)\n'

# Fix min(8 to min(5 for strawberry seeds
content = ''.join(lines)
content = content.replace('n_straw = min(8, int((money - 400) // 100))',
                          'n_straw = min(5, int((money - 400) // 100))')

with open("bots/v24.py", "w", encoding="utf-8") as f:
    f.write(content)

# Verify
import ast
try:
    ast.parse(content)
    print("Syntax: OK")
except SyntaxError as e:
    print(f"Syntax: ERROR - {e}")

# Show relevant lines
lines2 = content.split('\n')
for i in range(365, 380):
    if i < len(lines2):
        print(f"{i+1}: {lines2[i]}")


