# СВОДКА ШАГА 0 (исправленная)

## 1. git log --oneline (последние 10 коммитов)
```
67411fe (HEAD -> master) v11: clean v7 base, no front-running, real market prices
8c3e086 v7: update results and agenda
e9b44ba v7: champion - endgame liquidation (32498 vs random)
fa655e3 ITER11 DUAL FAIL: land+wheat not profitable, revert to v6
8eecc36 ITER10 SCALE FAIL: 6 hands no improvement, revert to v6
22061b5 v6: update results and agenda
7122ad5 v6: champion - MELON on v5 base (31811 vs random)
9d5a8cb ITER8 a/b FAIL: max plant and fertilizers both fail
5867da6 ITER8a MAX PLANT FAIL: record
0eb421b ITER7 LAND v3 FAIL: record and STOP land
```

## 2. bots/ (какие чемпионы есть)
- melon_maxxer.py
- v0.py, v2.py, v3.py, v4.py, v5.py, v6.py, v7.py, v8.py, v9.py, v10.py, v11.py
- **v1 отсутствует**

## 3. champ/main.py — версия и ключевые параметры
- **Версия**: v6/v7 (MELON monocrop, 4 батрака, DROP-пачки)
- **MAX_HANDS**: 4
- **Культура**: MELON (seed=80, first_yield=10, max_yield=12, max=6)
- **Животные**: нет
- **Земля**: нет
- **Удобрения**: нет
- **DROP_THRESHOLD**: 8
- **Hire**: money > 500

## 4. results.tsv (последние 5 строк)
```
2026-08-06	v5	1.00	+913	3	0.00	champion
2026-08-08	v6	1.00	+23572	0	0.00	champion
2026-08-08	v7	0.88	+2036	0	0.00	champion
```

## 5. EXPERIMENTS.md (последние 5 строк)
```
## v6 MELON (2026-08-08)
vs random: wr=1.00 +31811 | vs starter: wr=1.00 +28014 | vs v5: wr=1.00 +23572
Статус: чемпион

## ИТЕРАЦИЯ #10 SCALE (2026-08-08) — FAIL
...
```

## 6. Текущий чемпион и тесты
- **Чемпион**: `champ/main.py` (код v6/v7 — MELON monocrop, 4 батрака, DROP-пачки)
- **Последний зафиксированный тест**: vs v7 (wr=0.88, delta=+2036) — champion
- **v11**: "clean v7 base" — не попал в results.tsv, значит, не прошёл гейт или не eval'ился