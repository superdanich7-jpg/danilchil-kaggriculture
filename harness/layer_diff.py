"""Compare the layer/tape composition of a public candidate against our v_iter47."""
import ast
import sys

CAND = sys.argv[1] if len(sys.argv) > 1 else 'public/lime2710/score2710-t23-kaggriculture-smart-harvest.py'
OURS = sys.argv[2] if len(sys.argv) > 2 else 'bots/v_iter47.py'

MARKERS = ['SHOP_PAIRS', 'TAPES', 'SHOP_ROUTES', 'OLD_SHOPS', 'crop_public_order',
           'terminal', 'storage', 'weed', 'liquidation', 'R110', 'EXP-']


def report(path, label):
    src = open(path, encoding='utf-8').read()
    tree = ast.parse(src)
    print('=== %s (%d bytes) ===' % (label, len(src)))
    for marker in MARKERS:
        print('   %-18s %d' % (marker, src.count(marker)))
    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    print('   top-level funcs   %d' % len(funcs))
    blobs = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str) and len(node.value.value) > 1500:
            name = node.targets[0].id if isinstance(node.targets[0], ast.Name) else '?'
            blobs.append((name, len(node.value.value)))
    print('   big string blobs  %d' % len(blobs))
    for name, size in sorted(blobs, key=lambda x: -x[1])[:14]:
        print('      %-34s %d' % (name, size))
    # layer wrapper chain: consecutive redefinitions of agent
    redefs = [n.name for n in funcs if n.name == 'agent']
    print('   "def agent" count %d' % len(redefs))


report(OURS, 'OURS ' + OURS)
print()
report(CAND, 'CAND ' + CAND)
