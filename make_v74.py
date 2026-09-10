"""Create v74: Sven-strategy (replay-forensics based).

Key principles from Sven's action log (episode-106818921):
1. Hire 6 hands immediately (not 1)
2. Buy 6 melon + 6 strawberry seeds (not 15 melon)
3. Buy 2 sheep + 1 cow immediately
4. Buy 9 wheat (not 4)
5. Continuous hiring: sell fertilizer to fund new hands
6. Buy animals constantly (cows and sheep)
7. Buy land on d21
8. Sell wool, milk, fertilizer, melon, strawberry as needed
"""
import re

src = open("champ/main.py", encoding="utf-8").read()

# 1. Day-0 bootstrap: Sven's opening
src = src.replace(
    '''        if day == 0 and hour == 0 and seeds.get("MELON", 0) == 0:
            market += [["BUY_ANIMAL", "COW", 1], ["BUY_ANIMAL", "SHEEP", 1],
                       ["BUY_SEED", "MELON", 3], ["BUY_SEED", "WHEAT", 4],
                       ["BUY_PRODUCT", "WHEAT", 4]]''',
    '''        # ITER74: Sven opening - 6 melon + 6 straw + 2 sheep + 1 cow + 9 wheat
        if day == 0 and hour == 0 and seeds.get("MELON", 0) == 0:
            market += [["BUY_ANIMAL", "SHEEP", 2], ["BUY_ANIMAL", "COW", 1],
                       ["BUY_SEED", "MELON", 6], ["BUY_SEED", "STRAWBERRY", 6],
                       ["BUY_SEED", "WHEAT", 4], ["BUY_PRODUCT", "WHEAT", 9]]'''
)

# 2. Hire immediately: 6 hands on day 0
src = src.replace(
    '''        max_hands_today = 12 if herd >= 5 else MAX_HANDS''',
    '''        # ITER74: Sven hires 6 immediately, then continuous
        max_hands_today = 12 if herd >= 5 else MAX_HANDS
        if day == 0 and hour == 1 and f.get("hires_today", 0) < 6:
            market.append(["HIRE"])
            market.append(["HIRE"])
            market.append(["HIRE"])
            market.append(["HIRE"])
            market.append(["HIRE"])'''
)

# 3. Straw seed buying: 6 per day (not 2-6)
src = src.replace(
    '''            if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 12:
                n_straw = min(6, int((money - FEED_RESERVE) // 100))
                if n_straw >= 1:
                    market.append(["BUY_SEED", "STRAWBERRY", n_straw])''',
    '''            # ITER74: Sven buys 6 straw seeds/day
            if day >= 4 and day <= 19 and seeds.get("STRAWBERRY", 0) < 12:
                n_straw = min(6, int((money - FEED_RESERVE) // 100))
                if n_straw >= 1:
                    market.append(["BUY_SEED", "STRAWBERRY", n_straw])'''
)

# 4. Animal buying: more aggressive
src = src.replace(
    '''        if 9 <= day <= 22 and herd < herd_cap and in_shed == 0 and money > 900 \\
                and shed.get("WHEAT", 0) >= 2:''',
    '''        # ITER74: Sven buys animals more aggressively
        if 1 <= day <= 22 and herd < herd_cap and in_shed == 0 and money > 600 \\
                and shed.get("WHEAT", 0) >= 2:'''
)

# 5. Land buying: d21
src = src.replace(
    '''        if len(quads) == 3 and not melon_mode and _can_spend(money, 4000):
            market.append(["BUY_LAND"])''',
    '''        # ITER74: Sven buys land on d21
        if len(quads) == 3 and not melon_mode and day >= 21 and _can_spend(money, 4000):
            market.append(["BUY_LAND"])'''
)

# 6. Docstring
src = src.replace(
    '"""Kaggriculture v17: diversified economy per top-player replay analysis.',
    '"""Kaggriculture v74: Sven-strategy (replay-forensics based).'
)

open("bots/v74.py", "w", encoding="utf-8").write(src)
print("v74.py created")
