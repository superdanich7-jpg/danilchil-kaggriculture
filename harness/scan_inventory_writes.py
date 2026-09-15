"""Find every write to market inventory + any daily replenishment in the env."""
import re

PATH = r"C:\Users\plotn\AppData\Local\Programs\Python\Python312\Lib\site-packages\kaggle_environments\envs\kaggriculture\kaggriculture.py"
src = open(PATH, encoding="utf-8").read().splitlines()

for i, line in enumerate(src, 1):
    if re.search(r'inventory', line) and re.search(r'(\+=|-=|=\s| = )', line):
        print(f"{i}: {line.strip()[:120]}")
