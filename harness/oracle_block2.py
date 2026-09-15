

def _orcl_adapt(obs, action, state):
    step = int(obs["step"])
    prices = obs["market"]["prices"]
    inv = obs["market"]["inventory"]
    shops = (obs.get("town") or {}).get("unlocked_shops") or []
    pending = state["pending"]

    def issue(good, qty):
        market = action.get("market")
        if market is None or len(market) >= 10:
            return False
        if any(len(o) >= 2 and o[0] == "SELL" and o[1] == good for o in market):
            return False
        market.append(["SELL", good, int(qty)])
        return True

    for good in sorted(pending.keys()):
        rec = pending[good]
        qty = rec["qty"]
        if qty <= 0:
            del pending[good]
            continue
        waited = step - rec["step"]
        cur_price = int(prices.get(good, 1))
        if step >= _ORCL_FORCE_STEP or waited >= _ORCL_MAX_WAIT or cur_price <= 1:
            if issue(good, qty):
                _ORCL_REPORT["orcl_forced" if step >= _ORCL_FORCE_STEP else "orcl_reissues"] += 1
            del pending[good]
            continue
        best = _orcl_projected_best(good, int(inv.get(good, _ORCL_I0)), step, shops)
        if cur_price >= _ORCL_ISSUE_FRAC * best:
            if issue(good, qty):
                _ORCL_REPORT["orcl_reissues"] += 1
            del pending[good]

    market = action.get("market")
    if market is not None and step < _ORCL_FORCE_STEP:
        kept = []
        for order in market:
            try:
                is_sell = (len(order) >= 3 and order[0] == "SELL"
                           and order[1] in _ORCL_PARAMS and int(order[2]) >= _ORCL_MIN_QTY)
            except Exception:
                is_sell = False
            if not is_sell:
                kept.append(order)
                continue
            good = order[1]
            qty = int(order[2])
            price = int(prices.get(good, 1))
            cur_inv = int(inv.get(good, _ORCL_I0))
            if price <= 1 or cur_inv < _ORCL_I0 or good in _ORCL_NO_DEFER_GOODS:
                _ORCL_REPORT["orcl_kept_scarcity"] += 1
                kept.append(order)
                continue
            already = pending.get(good, {"qty": 0})["qty"]
            if already + qty > _ORCL_PEND_CAP:
                kept.append(order)
                continue
            best = _orcl_projected_best(good, cur_inv, step, shops)
            if best > price * (1.0 + _ORCL_MIN_GAIN):
                rec = pending.setdefault(good, {"qty": 0, "step": step})
                rec["qty"] += qty
                _ORCL_REPORT["orcl_defers"] += 1
                continue
            _ORCL_REPORT["orcl_kept_weak_gain"] += 1
            kept.append(order)
        action["market"] = kept
    return action


def agent(observation, configuration=None):
    player = int(observation["player"])
    step = int(observation["step"])
    if player not in _ORCL_STATE or step <= _ORCL_STATE[player]["step"]:
        _ORCL_STATE[player] = {"pending": {}, "step": step, "inv_hist": {}}
    state = _ORCL_STATE[player]
    state["step"] = step
    state["inv_hist"] = dict(observation["market"]["inventory"])
    action = _ORCL_PARENT(observation, configuration)
    try:
        if _orcl_gate(observation):
            action = _orcl_adapt(observation, action, state)
        else:
            pending = state["pending"]
            prices = observation["market"]["prices"]
            for good in sorted(pending.keys()):
                rec = pending[good]
                if step - rec["step"] >= _ORCL_MAX_WAIT or step >= _ORCL_FORCE_STEP:
                    market = action.get("market")
                    if market is not None and len(market) < 10 and not any(
                            len(o) >= 2 and o[0] == "SELL" and o[1] == good for o in market):
                        market.append(["SELL", good, int(rec["qty"])])
                        _ORCL_REPORT["orcl_reissues"] += 1
                    del pending[good]
            _ORCL_REPORT["orcl_gate_off"] = _ORCL_REPORT.get("orcl_gate_off", 0) + 1
    except Exception:
        _ORCL_REPORT["orcl_errors"] += 1
    _ORCL_REPORT.update(getattr(_ORCL_PARENT, "telemetry", {}) or {})
    return action


agent.telemetry = _ORCL_REPORT

# The Kaggle loader runs get_last_callable(): it returns the LAST callable
# inserted into this namespace by insertion order. Rebinding `agent` above
# kept lime's original dict slot, so the wrapper must be re-inserted as a
# FRESH key placed after every other callable in the file.
kaggle_agent = agent
