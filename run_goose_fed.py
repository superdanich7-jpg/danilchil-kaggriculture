from kaggle_environments import make

env = make("kaggriculture", debug=True)
env.run(["bots/goose_fed.py", "pass"])

obs = env.steps[-1][0].observation
f = obs.farms[obs.player]
priv = obs.private or {}
shed = priv.get("shed", {}) or {}
animals = priv.get("animals", {}) or {}

# Считаем метрики
goose_alive = any(isinstance(t, dict) and t.get("animal") == "GOOSE"
                  for row in f.tiles for t in row)
eggs_in_shed = shed.get("EGG", 0)
feeds_done = sum(1 for a in animals.values() if a.get("fed_today", False))
consec_unfed = sum(a.get("consecutive_unfed", 0) for a in animals.values())

print("ШАГ A | лог день/money/goose/eggs/feeds")
print(f"FINAL: day={obs.day} money={f.money} goose_alive={goose_alive} eggs_in_shed={eggs_in_shed} feeds_done={feeds_done} consec_unfed={consec_unfed}")
print(f"animals count: {len(animals)}")
for aid, a in animals.items():
    print(f"  {aid}: type={a.get('type')} consecutive_unfed={a.get('consecutive_unfed', 0)} fed_today={a.get('fed_today', False)}")

# Выводим историю денег и яиц по дням (каждый 24-й шаг)
print("\nДень | money | eggs_shed | feeds")
for step_idx in range(0, len(env.steps), 24):
    if step_idx >= len(env.steps):
        break
    s = env.steps[step_idx]
    o = s[0].observation
    day = o.day
    money = o.farms[o.player].money
    priv_d = o.private or {}
    shed_d = priv_d.get("shed", {}) or {}
    eggs = shed_d.get("EGG", 0)
    animals_d = priv_d.get("animals", {}) or {}
    feeds = sum(1 for a in animals_d.values() if a.get("fed_today", False))
    print(f"{day:3d} | {money:6.0f} | {eggs:9d} | {feeds}")