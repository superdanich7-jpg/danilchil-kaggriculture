import json
from kaggle_environments import make
from bots.v12_debug4 import agent as agent_v12, debug_log

def run_debug_game(seed=0):
    # Очищаем лог
    debug_log.clear()
    
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    env.run([agent_v12, agent_v12])  # играем сами с собой для диагностики
    
    # Выводим лог
    print("day | money | animals | consec_unfed | wheat_shed | wheat_inv | feeds_done | shed_total")
    print("-" * 80)
    for entry in debug_log:
        day, money, animals, consec_unfed, wheat_shed, wheat_inv, feeds_done, shed_total, buy_animal_orders, build_orders, place_orders, hire_orders = entry
        print(f"{day:3d} | {money:6.0f} | {animals:7d} | {consec_unfed:12d} | {wheat_shed:10d} | {wheat_inv:9d} | {feeds_done:10d} | {shed_total:10d} | buy_animal={buy_animal_orders} | build={build_orders} | place={place_orders} | hire={hire_orders}")
    
    # Финальное состояние
    final_obs = env.steps[-1][0].observation
    priv = final_obs.get("private", {}) or {}
    final_animals = priv.get("animals", {}) or {}
    print(f"\nФинальные животные: {len(final_animals)}")
    for aid, a in final_animals.items():
        print(f"  {aid}: type={a.get('type')}, consecutive_unfed={a.get('consecutive_unfed', 0)}")
    
    return debug_log

if __name__ == "__main__":
    run_debug_game(seed=0)