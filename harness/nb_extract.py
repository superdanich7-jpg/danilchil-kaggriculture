"""Extract agent source from downloaded Kaggle notebooks (.ipynb).

Handles %%writefile main.py magics: everything after the magic line in a cell
is agent file content (possibly continued across following cells).
"""
import json
import glob
import os

for nb in glob.glob('public/*/*.ipynb'):
    d = json.load(open(nb, encoding='utf-8'))
    base = os.path.splitext(nb)[0]
    files = {}    # agent filename -> list of source chunks
    current = None
    normal = []   # cells that are not writefile content
    for cell in d.get('cells', []):
        if cell.get('cell_type') != 'code':
            current = None
            continue
        text = ''.join(cell.get('source', []))
        lines = text.split('\n')
        # find a %%writefile magic at cell start
        if lines and lines[0].strip().startswith('%%writefile'):
            fname = lines[0].split('%%writefile')[1].strip()
            current = fname
            body = '\n'.join(lines[1:])
            if body.strip():
                files.setdefault(fname, []).append(body)
            continue
        if current is not None:
            if text.strip():
                files.setdefault(current, []).append(text)
        else:
            normal.append(text)
    for fname, parts in files.items():
        body = '\n'.join(parts)
        out = '%s__%s' % (base, fname.replace('.py', '.py'))
        open(out, 'w', encoding='utf-8').write(body)
        print('%s (%d chars)' % (out, len(body)))
    fb = base + '_normal.py'
    open(fb, 'w', encoding='utf-8').write('\n\n# ==== CELL ====\n\n'.join(normal))
    print('%s (%d chars)' % (fb, sum(len(x) for x in normal)))
