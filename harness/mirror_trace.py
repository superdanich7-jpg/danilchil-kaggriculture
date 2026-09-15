"""Trace a mirror match step by step to find unused margin.

Runs a single episode where both seats play the same champ agent, and logs per
day: money of both players, market prices, town shops unlocked, our crop tiles,
shed contents.

Usage:
    py -3.12 harness/mirror_trace.py [champ_path] [seed] [step_filter]
"""
import importlib.util
import sys

from kaggle_environments import make

TOWN_SHOPS = {
    "BAKERY": ["EGG", "WHEAT"],
    "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"],
    "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE": ["WOOL"],
    "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"],
    "PET_CAFE": ["CARROT"],
    "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"],
    "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def crop_counts(obs, seat):
    counts = {}
    empty = 0
    for row in obs["farms"][seat]["tiles"]:
        for tile in ([row] if isinstance(row, dict) else row):
            if tile in (None, "LOCKED"):
                continue
            if isinstance(tile, dict):
                crop = tile.get("crop")
                kind = tile.get("kind")
                if crop:
                    counts[crop] = counts.get(crop, 0) + 1
                elif kind == "WEED":
                    counts["WEED"] = counts.get("WEED", 0) + 1
                elif kind is None:
                    empty += 1
    return counts, empty


def shop_demand(shops):
    demand = {}
    for name in shops:
        products = TOWN_SHOPS.get(name)
        if not products:
            continue
        mult = 2 if len(products) == 1 else 1
        for item in products:
            demand[item] = demand.get(item, 0) + mult
    return demand


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "champ/main.py"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    step_filter = int(sys.argv[3]) if len(sys.argv) > 3 else 72

    mod = load(path, "trace_agent")
    env = make("kaggriculture",
               configuration={"episodeSteps": 720, "seed": seed})
    env.run([mod.agent, mod.agent])

    for step, states in enumerate(env.steps):
        if step % step_filter:
            continue
        obs = states[0].observation
        day = step // 24
        ours = int(obs["farms"][0]["money"])
        theirs = int(obs["farms"][1]["money"])
        prices = obs["market"]["prices"]
        inventory = obs["market"].get("inventory", {})
        shops = (obs.get("town") or {}).get("unlocked_shops", [])
        demand = shop_demand(shops)
        crops, empty = crop_counts(obs, 0)
        shed = {k: v for k, v in ((obs.get("private") or {}).get("shed") or {}).items() if v}
        print(f"d{day:02d} us={ours:7d} op={theirs:7d} gap={ours-theirs:+7d} "
              f"hands={len(obs['farms'][0].get('hands') or [])} empty={empty}")
        print(f"      crops={crops}")
        print(f"      shed={shed}")
        print(f"      demand={demand}")
        print("      prices=" + " ".join(f"{k}={v}" for k, v in sorted(prices.items())))
        print("      inv=" + " ".join(f"{k}={v}" for k, v in sorted(inventory.items())))


if __name__ == "__main__":
    main()