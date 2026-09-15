"""Build v97_oracle = v96_lime (lime2710 composite) + ORACLE price-projection layer."""
import ast

base = open('bots/v96_lime.py', encoding='utf-8').read()
block = open('harness/oracle_block.py', encoding='utf-8').read()

src = base + block
open('bots/v97_oracle.py', 'w', encoding='utf-8').write(src)

ast.parse(src)
ast.parse(block)
print('v97_oracle built:', len(src) // 1024, 'KB, valid')
