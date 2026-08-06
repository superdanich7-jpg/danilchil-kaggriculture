import importlib, inspect, json, re
def main():
    mod = importlib.import_module("kaggle_environments.envs.kaggriculture.kaggriculture")
    raw = {n: getattr(mod, n) for n in dir(mod) if n.isupper()}
    scal = lambda d: {k: v for k, v in d.items() if isinstance(v, (int, float, str, bool))}
    crops = {k: scal(v) for k, v in raw.get("CROPS", {}).items() if isinstance(v, dict)}
    animals = {k: scal(v) for k, v in raw.get("ANIMALS", {}).items() if isinstance(v, dict)}
    sus = [n for n in list(raw) + [f for f, o in vars(mod).items() if inspect.isfunction(o)]
           if re.search(r"IMPACT|PRICE|SHOP|TOWN|DEMAND|HIRE|COST|LAND|QUAD|SCHED", n, re.I)]
    funcs = [n for n, o in vars(mod).items() if inspect.isfunction(o)]
    cfg = {}
    try:
        from kaggle_environments import make
        c = make("kaggriculture", debug=True).configuration
        cfg = {k: getattr(c, k) for k in dir(c) if not k.startswith("_")
               if isinstance(getattr(c, k), (int, float, str, bool))}
    except Exception as e: cfg = {"error": str(e)}
    out = {"crops": crops, "animals": animals, "config": cfg, "suspects": sus,
           "other_upper": {k: raw[k] for k in raw if k not in ("CROPS", "ANIMALS")
                           and isinstance(raw[k], (int, float, str, bool))}}
    json.dump(out, open("harness/constants.json", "w"), indent=1, default=str)
    print("CROPS:")
    [print(f"  {k:12s} {v}") for k, v in crops.items()]
    print("ANIMALS:")
    [print(f"  {k:12s} {v}") for k, v in animals.items()]
    print("CONFIG:", cfg); print("SUSPECTS:", sus); print("FUNCS:", funcs)
if __name__ == "__main__": main()