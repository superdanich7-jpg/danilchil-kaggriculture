"""Revenue split: for each replay, attribute realized sale revenue per good for
both seats. Reveals which goods actually carry the economy and whether our
tape is dumping goods the opponent leaves alone (shared-market price crash)."""
import json
import sys
from collections import Counter, defaultdict


def run(path):
    d = json.load(open(path, encoding='utf-8'))
    info = d.get('info', {})
    names = info.get('TeamNames') or ['seat0', 'seat1']
    steps = d['steps']
    rev = [{}, {}]
    qty = [{}, {}]
    last_price = [{}, {}]
    for st in steps:
        for seat in (0, 1):
            cell = st[seat]
            obs = cell.get('observation') or {}
            act = cell.get('action') or {}
            prices = ((obs.get('market') or {}).get('prices') or {})
            if prices:
                for g, p in prices.items():
                    last_price[seat][g] = p
            if not isinstance(act, dict):
                continue
            for order in (act.get('market') or []):
                if not order or order[0] != 'SELL' or len(order) < 3:
                    continue
                good, amount = order[1], order[2]
                p = prices.get(good)
                if p is None:
                    continue
                rev[seat][good] = rev[seat].get(good, 0) + p * amount
                qty[seat][good] = qty[seat].get(good, 0) + amount
    print(f'=== {path.split("/")[-1]} | {names[0]} vs {names[1]}')
    for seat in (0, 1):
        tot = sum(rev[seat].values())
        print(f'  seat{seat} {names[seat]:<20} total revenue={tot:>8.0f}')
        for good, value in sorted(rev[seat].items(), key=lambda kv: -kv[1]):
            print(f'      {good:<12} rev={value:>8.0f} qty={qty[seat][good]:>7} '
                  f'px~{value / max(1, qty[seat][good]):>6.1f} end={last_price[seat].get(good)}')
    return rev, qty, names


if __name__ == '__main__':
    for p in sys.argv[1:]:
        run(p)
        print()