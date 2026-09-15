from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Task:
    name: str
    turns_left: int
    gain: float
    energy_cost: int
    food_cost: int = 0
    risk: float = 0.0

@dataclass(frozen=True)
class FarmState:
    energy: int
    food: int
    reserve_energy: int
    reserve_food: int

@dataclass(frozen=True)
class Recommendation:
    task: str
    score: float
    explanation: str

def field_clock(state: FarmState, tasks: Iterable[Task]) -> list[Recommendation]:
    """Rank only visible-state tasks while maintaining energy and food floors.

    A task is rejected when taking it would breach either reserve. Otherwise the
    priority is its value per visible cost, increased as its deadline approaches
    and reduced by its declared risk. The rule is deliberately inspectable so a
    player can tune it from a match log rather than relying on hidden opponent data.
    """
    ranked=[]
    for task in tasks:
        if state.energy-task.energy_cost < state.reserve_energy:
            continue
        if state.food-task.food_cost < state.reserve_food:
            continue
        urgency=6.0/max(task.turns_left, 1)
        efficiency=task.gain/max(task.energy_cost+task.food_cost, 1)
        score=efficiency+urgency-3.0*task.risk
        explanation=(f"{task.name}: value/cost={efficiency:.2f}, "
                     f"deadline bonus={urgency:.2f}, risk penalty={3*task.risk:.2f}")
        ranked.append(Recommendation(task.name, round(score, 4), explanation))
    return sorted(ranked, key=lambda item: (-item.score, item.task))


# ==== CELL ====

# A small, reproducible turn snapshot.
state = FarmState(energy=9, food=4, reserve_energy=2, reserve_food=1)
tasks = [
    Task("harvest ripe field", turns_left=1, gain=15, energy_cost=3, risk=0.02),
    Task("buy seed bundle", turns_left=5, gain=12, energy_cost=2, food_cost=1, risk=0.10),
    Task("repair irrigation", turns_left=2, gain=10, energy_cost=4, risk=0.04),
    Task("expensive detour", turns_left=1, gain=30, energy_cost=8, risk=0.00),
]
recommendations = field_clock(state, tasks)
for item in recommendations:
    print(f"{item.task:22s} score={item.score:5.2f}  {item.explanation}")


# ==== CELL ====

# Synthetic safety checks: the reserve floor and near deadline are both observable.
urgent = field_clock(FarmState(energy=6, food=3, reserve_energy=2, reserve_food=1), [
    Task("urgent harvest", turns_left=1, gain=9, energy_cost=2),
    Task("later sale", turns_left=6, gain=9, energy_cost=2),
])
assert urgent[0].task == "urgent harvest"

floor = field_clock(FarmState(energy=5, food=2, reserve_energy=2, reserve_food=1), [
    Task("safe task", turns_left=2, gain=5, energy_cost=2),
    Task("breaks reserve", turns_left=1, gain=99, energy_cost=4),
])
assert [r.task for r in floor] == ["safe task"]
print("PASS: deadline and reserve-floor checks")


# ==== CELL ====

import matplotlib.pyplot as plt
names=[r.task for r in recommendations]
scores=[r.score for r in recommendations]
fig, ax = plt.subplots(figsize=(8, 3.5))
colors=["#214e73" if i == 0 else "#77a6c8" for i in range(len(names))]
ax.barh(names[::-1], scores[::-1], color=colors[::-1])
ax.set_xlabel("visible-state priority score")
ax.set_title("Field Clock: inspectable next-action ranking")
ax.grid(axis="x", alpha=.25)
plt.show()
