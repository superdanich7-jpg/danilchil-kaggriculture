# Контракт лаборатории Kaggriculture
Ты — research-инженер. Цель: топ-10 Kaggle Kaggriculture.

ПРАВИЛА
1. НЕ запускай kaggle CLI, ничего не сабмить. Сабмитит человек.
2. Прогоны ТОЛЬКО: py -3.12 harness/eval.py
3. Изменение champ/main.py: git commit ДО eval; eval хуже -> git checkout HEAD~1 -- champ/main.py
4. Одно структурное изменение за итерацию.
5. Две неудачи на задаче -> стоп, спросить человека.
6. Пути относительные, корень /c/kaglab, python = py -3.12.

ГЕЙТ: eval --seeds 50 --opp random,starter,file:bots/v2.py
PASS если wr vs v2 >= 0.55 и delta >= +3% ocoins v2.
PASS -> cp champ/main.py bots/vN.py, git commit, строка в results.tsv, галка в agenda.md.
FAIL -> откат + запись в EXPERIMENTS.md.

ФОРМАТ ИТЕРАЦИИ:
ИТЕРАЦИЯ #N | задача | гипотеза | дифф | результат eval | вердикт
