"""Inspect a public agent file: top-level defs, constants, data blobs."""
import ast
import re
import sys

p = sys.argv[1] if len(sys.argv) > 1 else 'public/lime2710/score2710-t23-kaggriculture-smart-harvest.py'
s = open(p, encoding='utf-8').read()
tree = ast.parse(s)

funcs, classes, assigns = [], [], []
for node in tree.body:
    if isinstance(node, ast.FunctionDef):
        funcs.append((node.name, node.lineno, len(node.body)))
    elif isinstance(node, ast.ClassDef):
        classes.append((node.name, node.lineno))
    elif isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name):
                try:
                    val = ast.literal_eval(node.value)
                    assigns.append((t.id, type(val).__name__, len(val) if hasattr(val, '__len__') else '-'))
                except Exception:
                    assigns.append((t.id, 'expr', '-'))

print('=== top-level functions (%d) ===' % len(funcs))
for name, ln, body in funcs:
    print('  %-42s line %5d  body %3d' % (name, ln, body))
print('=== classes (%d) ===' % len(classes))
for name, ln in classes:
    print('  %-42s line %5d' % (name, ln))
print('=== literal constants (%d) ===' % len(assigns))
for name, kind, size in assigns:
    print('  %-42s %-8s %s' % (name, kind, size))

for marker in ('TAPE', 'PLAN', 'PLANS', 'ACTIONS', 'SHOP_PAIR', 'ROUTE', 'lzma',
               'base64', 'zlib', 'b64decode', 'decompress'):
    print('marker %-12s count %d' % (marker, s.count(marker)))