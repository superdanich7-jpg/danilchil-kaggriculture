"""Create v75: Sven-economy (sell everything, buy animals aggressively).

Key insights from Sven forensics (episode-106818921):
1. Sells ALL fertilizer (288 vs our 170) - main income for hiring
2. Sells ALL wool (135 vs our 38) - more animals = more wool
3. Sells ALL milk (153 vs our 134)
4. Sells almost no wheat (21 vs our 249) - wheat is for feeding, not selling
5. 16 animals sustained (we have 13)
6. 12 hands sustained (we have 12)
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Sell ALL fertilizer (no reserve)
src = src.replace(
    '''        fert_res = 0 if (day < 10 or melon_mode or day >= 27) else FERT_RESERVE
        fv = shed.get("FERTILIZER", 0) - fert_res
        if fv > 0:
            market.append(["SELL", "FERTILIZER", fv if full_dump
                           else min(8 * big_stable, fv)])''',
    '''        # ITER75: Sven sells ALL fertilizer (no reserve)
        fv = shed.get("FERTILIZER", 0)
        if fv > 0:
            market.append(["SELL", "FERTILIZER", fv if full_dump
                           else min(8 * big_stable, fv)])'''
)

# 2. Sell ALL wool (no cap)
src = src.replace(
    '''        if shed.get("WOOL", 0) > 0:
            market.append(["SELL", "WOOL", shed["WOOL"] if full_dump
                           else min(6 * big_stable, shed["WOOL"])])''',
    '''        # ITER75: Sven sells ALL wool
        if shed.get("WOOL", 0) > 0:
            market.append(["SELL", "WOOL", shed["WOOL"] if full_dump
                           else min(8 * big_stable, shed["WOOL"])])'''
)

# 3. Sell ALL milk (no cap)
src = src.replace(
    '''        if shed.get("MILK", 0) > 0:
            market.append(["SELL", "MILK", shed["MILK"] if full_dump
                           else min(8 * big_stable, shed["MILK"])])''',
    '''        # ITER75: Sven sells ALL milk
        if shed.get("MILK", 0) > 0:
            market.append(["SELL", "MILK", shed["MILK"] if full_dump
                           else min(8 * big_stable, shed["MILK"])])'''
)

# 4. Wheat: only sell surplus above feed need + small buffer
src = src.replace(
    '''        wv = shed.get("WHEAT", 0) - ((feed_need + 4) if day < 29 else 0)
        if wv > 0:
            market.append(["SELL", "WHEAT", wv if full_dump
                           else min(10 * big_stable, wv)])''',
    '''        # ITER75: Sven sells almost no wheat (only true surplus)
        wv = shed.get("WHEAT", 0) - ((feed_need + 8) if day < 29 else 0)
        if wv > 0:
            market.append(["SELL", "WHEAT", wv if full_dump
                           else min(10 * big_stable, wv)])'''
)

# 5. Herd cap: 16 (Sven's level)
src = src.replace(
    'herd_cap = 8 if melon_mode else 12',
    'herd_cap = 10 if melon_mode else 16  # ITER75: Sven has 16 animals'
)

# 6. Animal buying: more aggressive (start earlier, buy more)
src = src.replace(
    '''        if 9 <= day <= 22 and herd < herd_cap and in_shed == 0 and money > 900 \\
                and shed.get("WHEAT", 0) >= 2:''',
    '''        # ITER75: Sven buys animals aggressively from d1
        if 1 <= day <= 24 and herd < herd_cap and in_shed == 0 and money > 500 \\
                and shed.get("WHEAT", 0) >= 2:'''
)

# 7. Docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v75: Sven-economy (sell everything, buy animals aggressively).'
)

open("bots/v75.py", "w", encoding="utf-8").write(src)
print("v75.py created")
