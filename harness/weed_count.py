"""Count WEED tiles on our farm at the end of a game (P0 metric)."""
import sys
from kaggle_environments import make


def weeds_and_straw(env, me, step=-1):
    obs = env.steps[step][me].observation
    farm = obs["farms"][me]
    tiles = farm["tiles"]
    w = sum(1 for row in tiles for t in row
            if isinstance(t, dict) and t.get("kind") == "WEED")
    s = sum(1 for row in tiles for t in row
            if isinstance(t, dict) and t.get("kind") == "PLANT"
            and t.get("crop") == "STRAWBERRY")
    m = sum(1 for row in tiles for t in row
            if isinstance(t, dict) and t.get("kind") == "PLANT"
            and t.get("crop") == "MELON")
    empty = sum(1 for row in tiles for t in row if t is None)
    day = obs.get("day", -1)
    money = farm.get("money", 0)
    herd = sum(1 for row in tiles for t in row
               if isinstance(t, dict) and t.get("kind") in ("PASTURE", "COOP")
               and t.get("animal"))
    return w, s, m, empty, day, money, herd


def run(agent_a, agent_b, seeds=10):
    tot_a = tot_b = 0
    for seed in range(seeds):
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        env.run([agent_a, agent_b])
        ra, rb = env.steps[-1][0].reward, env.steps[-1][1].reward
        print(f"seed {seed}: A r={ra:.0f} | B r={rb:.0f}")
        for day in (9, 15, 19, 21, 26, 29):
            for side, name in ((0, "A"), (1, "B")):
                w, s, m, e, d, mo, hd = weeds_and_straw(env, side, day * 24 + 23)
                print(f"  d{day} {name}: weeds={w} straw={s} melon={m} "
                      f"empty={e} money={mo:.0f} herd={hd}")
        tot_a += weeds_and_straw(env, 0)[0]
        tot_b += weeds_and_straw(env, 1)[0]
    print(f"AVG weeds: A={tot_a/seeds:.1f} B={tot_b/seeds:.1f}")


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10)
