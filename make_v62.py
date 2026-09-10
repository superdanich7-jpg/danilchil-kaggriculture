"""Create v62: EARLY ANIMAL RAMP (fundamental fix for slow start).

kirito83 forensics (127k): bought 4 animals on DAY 0, kept buying daily
until d11 (13-14 animals), fert conveyor from d1 = ~1000/day pure profit.
Cow pays back in 2.2 days (fert 100/day + milk 80/day from d8).

We buy animals only from d9 and reach 13 animals by d15 - we lose the
entire early fert/milk stream (2-3 fert/day vs his 8-14/day).

v62 changes:
1. Day-0 bootstrap: 2 COW + 2 SHEEP (was 1+1)
2. Animal buying window: d1-22 (was d9-22), money gate 900 -> 650
3. Cow cap day: d16 -> d20, cow count 8 -> 10
4. FERT_RESERVE for selling: 8 -> 0 (kirito83 sells ALL fert: ~390/game)
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Day-0 bootstrap: 2 COW + 2 SHEEP
src = src.replace(
    '''        if day == 0 and hour == 0 and seeds.get("MELON", 0) == 0:
            market += [["BUY_ANIMAL", "COW", 1], ["BUY_ANIMAL", "SHEEP", 1],
                       ["BUY_SEED", "MELON", 3], ["BUY_SEED", "WHEAT", 4],
                       ["BUY_PRODUCT", "WHEAT", 4]]''',
    '''        if day == 0 and hour == 0 and seeds.get("MELON", 0) == 0:
            # ITER62: kirito83 bought 4 animals on d0 - fert conveyor from
            # d1 (~400/day) + early milk/wool. Animals pay back in 2-3 days.
            market += [["BUY_ANIMAL", "COW", 2], ["BUY_ANIMAL", "SHEEP", 2],
                       ["BUY_SEED", "MELON", 3], ["BUY_SEED", "WHEAT", 4],
                       ["BUY_PRODUCT", "WHEAT", 4]]'''
)

# 2. Buying window d1-22, money gate 650
src = src.replace(
    '''        if 9 <= day <= 22 and herd < herd_cap and in_shed == 0 and money > 900 \\
                and shed.get("WHEAT", 0) >= 2:
            n_sh = sum(1 for _, t in anims if t.get("animal") == "SHEEP")
            n_cow = sum(1 for _, t in anims if t.get("animal") == "COW")
            if n_cow < 8 and day <= 16 and _can_spend(money, 400):
                market.append(["BUY_ANIMAL", "COW", 1])
                if money - 800 >= FEED_RESERVE and n_cow < 7:
                    market.append(["BUY_ANIMAL", "COW", 1])
            elif n_sh < 10 and _can_spend(money, 500):
                market.append(["BUY_ANIMAL", "SHEEP", 1])
                if money - 1000 >= FEED_RESERVE and n_sh < 9:
                    market.append(["BUY_ANIMAL", "SHEEP", 1])''',
    '''        # ITER62: early continuous ramp (kirito83 buys daily to d11).
        # Cow ROI: fert 100/day + milk 80/day = 2.2-day payback.
        if 1 <= day <= 22 and herd < herd_cap and in_shed == 0 and money > 650 \\
                and shed.get("WHEAT", 0) >= 2:
            n_sh = sum(1 for _, t in anims if t.get("animal") == "SHEEP")
            n_cow = sum(1 for _, t in anims if t.get("animal") == "COW")
            if n_cow < 10 and day <= 20 and _can_spend(money, 400):
                market.append(["BUY_ANIMAL", "COW", 1])
                if money - 800 >= FEED_RESERVE and n_cow < 9:
                    market.append(["BUY_ANIMAL", "COW", 1])
            elif n_sh < 12 and _can_spend(money, 500):
                market.append(["BUY_ANIMAL", "SHEEP", 1])
                if money - 1000 >= FEED_RESERVE and n_sh < 11:
                    market.append(["BUY_ANIMAL", "SHEEP", 1])'''
)

# 3. Sell ALL fertilizer (reserve 8 -> 0)
src = src.replace(
    '        fert_res = 0 if (day < 10 or melon_mode or day >= 27) else FERT_RESERVE',
    '        fert_res = 0  # ITER62: sell all fert (kirito83: ~390/game)'
)

# 4. Docstring
src = src.replace(
    '"""Kaggriculture v49: iter35 + straw limit 15 only.',
    '"""Kaggriculture v62: early animal ramp (d0-22, sell all fert).'
)

open("bots/v62.py", "w", encoding="utf-8").write(src)
print("v62.py created")
