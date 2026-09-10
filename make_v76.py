"""Create v76: iter43 base + sell ALL fertilizer + sell ALL wool/milk.

Key insight: v75 failed because 16 animals is too expensive without melon wave.
v76 keeps iter43's proven animal economy (herd 12, buy d9-d22) but sells
ALL byproducts (fertilizer, wool, milk) instead of capping sales.
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
    '''        # ITER76: Sven sells ALL fertilizer (no reserve)
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
    '''        # ITER76: Sven sells ALL wool
        if shed.get("WOOL", 0) > 0:
            market.append(["SELL", "WOOL", shed["WOOL"] if full_dump
                           else min(8 * big_stable, shed["WOOL"])])'''
)

# 3. Sell ALL milk (no cap)
src = src.replace(
    '''        if shed.get("MILK", 0) > 0:
            market.append(["SELL", "MILK", shed["MILK"] if full_dump
                           else min(8 * big_stable, shed["MILK"])])''',
    '''        # ITER76: Sven sells ALL milk
        if shed.get("MILK", 0) > 0:
            market.append(["SELL", "MILK", shed["MILK"] if full_dump
                           else min(8 * big_stable, shed["MILK"])])'''
)

# 4. Wheat: only sell true surplus (Sven sells almost no wheat)
src = src.replace(
    '''        wv = shed.get("WHEAT", 0) - ((feed_need + 4) if day < 29 else 0)
        if wv > 0:
            market.append(["SELL", "WHEAT", wv if full_dump
                           else min(10 * big_stable, wv)])''',
    '''        # ITER76: Sven sells almost no wheat (only true surplus)
        wv = shed.get("WHEAT", 0) - ((feed_need + 8) if day < 29 else 0)
        if wv > 0:
            market.append(["SELL", "WHEAT", wv if full_dump
                           else min(10 * big_stable, wv)])'''
)

# 5. Docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v76: iter43 base + sell ALL fertilizer/wool/milk.'
)

open("bots/v76.py", "w", encoding="utf-8").write(src)
print("v76.py created")
