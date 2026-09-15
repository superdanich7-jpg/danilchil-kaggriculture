"""Build champ/main.py from the lime2710 public agent (iter54).

The upstream file ends with a notebook-only packaging cell guarded by
`if __name__ == "__main__":` that writes submission.tar.gz next to the script.
Kaggle may execute the submitted file with __name__ == "__main__", which would
make the agent try to open a file for writing at import time. Strip that block;
the agent itself is untouched.
"""

import ast
import hashlib

SRC = 'public/lime2710/score2710-t23-kaggriculture-smart-harvest.py'
DST = 'bots/v96_lime.py'

src = open(SRC, encoding='utf-8').read()
marker = 'if __name__ == "__main__":'
idx = src.index(marker)
kept = src[:idx].rstrip() + '\n'

assert 'submission.tar.gz' not in kept, 'packaging block not fully stripped'
for name in ('_code_tarfile', '_code_archive', '_code_pathlib', '_code_source'):
    assert name not in kept, f'{name} leaked into agent body'
ast.parse(kept)

with open(DST, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(kept)

print('lime2710 md5:', hashlib.md5(open(SRC, 'rb').read()).hexdigest())
print('champ    md5:', hashlib.md5(open(DST, 'rb').read()).hexdigest())
print('champ lines:', kept.count('\n'), '| def agent present:', '\ndef agent(' in kept)
print('champ/main.py written and valid')