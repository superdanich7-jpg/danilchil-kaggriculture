# Experiment Log
## v2 baseline (2026-08-06)
vs random: wr=1.00 +1669 | vs starter: wr=0.00 -1956 | vs melon: wr=0.00 -4489 | vs v0: wr=0.57 +78
Статус: чемпион (единственный)

## v3 crop-only (2026-08-06)
vs random: wr=1.00 +6586 | vs starter: wr=1.00 +3042 | vs v2: wr=1.00 +4659
Статус: чемпион

## ИТЕРАЦИЯ #2 A7 (2026-08-06) — FAIL
Гипотеза: переключение на strawberry/melon с траншами продаж удвоит доход.
Результаты (50 seeds):
- a) CARROT+транши: vs random wr=1.00 +6658 | vs starter wr=1.00 +3042 | vs v3 wr=0.36 -26
- b) STRAWBERRY:    vs random wr=0.99 +306  | vs starter wr=0.00 -3184
- c) MELON:         vs random wr=1.00 +838  | vs starter wr=0.00 -2648
Вердикт: FAIL. Гейт wr vs v3 >= 0.55 не пройден (0.36).
Вывод: транши продаж для CARROT (base 35, linear) бесполезны — продажа всеми партиями даёт тот же доход.
STRAWBERRY/MELON нуждаются в защите ранней фазы (первый урожай day 10) или в батраках/земле.