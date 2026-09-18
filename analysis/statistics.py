# -*- coding: utf-8 -*-
"""
Расширенная статистика: MAE, RMSE, корреляция, гистограммы.
"""

import math
from datetime import datetime, timedelta

from core.config import MODELS, MIN_VERIFY_DATE
from data.actual import fetch_actual
from data.forecast import fetch_previous_run


def _pearson(xs, ys):
    n = len(xs)
    if n < 2: return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0: return None
    return num / (sx * sy)


def _r_squared(xs, ys):
    n = len(xs)
    if n < 2: return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0: return None
    b = num / den
    a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    if ss_tot == 0: return None
    return 1 - ss_res / ss_tot


def _mape(fact, pred):
    pairs = [(f, p) for f, p in zip(fact, pred)
             if f is not None and p is not None and abs(f) > 0.5]
    if not pairs: return None
    return 100 * sum(abs(p - f) / abs(f) for f, p in pairs) / len(pairs)


def _quantile(values, q):
    if not values: return None
    idx = q * (len(values) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi: return values[lo]
    return values[lo] * (hi - idx) + values[hi] * (idx - lo)


def analyze_period(model_key, lat, lon, days=14):
    today = datetime.now().date()
    fact_t_all, fcst_t_all = [], []
    fact_p_all, fcst_p_all = [], []

    for d in range(days, 0, -1):
        date_str = (today - timedelta(days=d)).strftime("%Y-%m-%d")
        if date_str < MIN_VERIFY_DATE: continue
        try:
            fact, source = fetch_actual(lat, lon, date_str)
            fcst = fetch_previous_run(model_key, lat, lon, date_str)
        except Exception:
            continue

        fact_h = fact.get("hourly", {})
        fcst_h = fcst.get("hourly", {})

        f_t = dict(zip(fact_h.get("time", []), fact_h.get("temperature_2m", [])))
        f_p = dict(zip(fact_h.get("time", []), fact_h.get("precipitation", [])))
        o_t = dict(zip(fcst_h.get("time", []), fcst_h.get("temperature_2m_previous_day1", [])))
        o_p = dict(zip(fcst_h.get("time", []), fcst_h.get("precipitation", [])))

        for t in sorted(set(f_t) & set(o_t)):
            fv, ov = f_t.get(t), o_t.get(t)
            if fv is not None and ov is not None:
                fact_t_all.append(fv); fcst_t_all.append(ov)
            fp, op = f_p.get(t), o_p.get(t)
            if fp is not None and op is not None:
                fact_p_all.append(fp); fcst_p_all.append(op)

    if not fact_t_all:
        return {"error": "нет данных за выбранный период"}

    errors = [p - f for f, p in zip(fact_t_all, fcst_t_all)]

    t_mae = sum(abs(e) for e in errors) / len(errors)
    t_bias = sum(errors) / len(errors)
    t_rmse = math.sqrt(sum(e ** 2 for e in errors) / len(errors))
    t_corr = _pearson(fact_t_all, fcst_t_all)
    t_r2 = _r_squared(fact_t_all, fcst_t_all)
    t_mape = _mape(fact_t_all, fcst_t_all)

    abs_err_sorted = sorted(abs(e) for e in errors)
    p50 = _quantile(abs_err_sorted, 0.50)
    p90 = _quantile(abs_err_sorted, 0.90)
    p95 = _quantile(abs_err_sorted, 0.95)

    if errors:
        e_min, e_max = min(errors), max(errors)
        n_bins = 12
        if e_max - e_min < 0.5:
            bins = [{"x": round(e_min, 2), "count": len(errors)}]
        else:
            step = (e_max - e_min) / n_bins
            bins = []
            for i in range(n_bins):
                lo = e_min + i * step
                hi = lo + step
                cnt = sum(1 for e in errors if lo <= e < hi or
                          (i == n_bins - 1 and e == hi))
                bins.append({"x": round((lo + hi) / 2, 2), "count": cnt})
    else:
        bins = []

    step = max(1, len(fact_t_all) // 200)
    scatter = [
        {"x": round(fact_t_all[i], 2), "y": round(fcst_t_all[i], 2)}
        for i in range(0, len(fact_t_all), step)
    ]

    hits = misses = false_alarms = 0
    fact_p_hours = fcst_p_hours = 0
    for f, p in zip(fact_p_all, fcst_p_all):
        f_has = f > 0.05
        p_has = p > 0.05
        if f_has: fact_p_hours += 1
        if p_has: fcst_p_hours += 1
        if f_has and p_has: hits += 1
        elif f_has and not p_has: misses += 1
        elif p_has and not f_has: false_alarms += 1

    hit_rate = hits / (hits + misses) if (hits + misses) else None
    precision = hits / (hits + false_alarms) if (hits + false_alarms) else None
    f1 = (2 * precision * hit_rate / (precision + hit_rate)
          if precision and hit_rate and (precision + hit_rate) > 0 else None)

    return {
        "model": model_key,
        "model_name": MODELS[model_key]["name"],
        "days_requested": days,
        "hours_total": len(fact_t_all),
        "temp": {
            "mae": round(t_mae, 2),
            "rmse": round(t_rmse, 2),
            "bias": round(t_bias, 2),
            "corr": round(t_corr, 3) if t_corr is not None else None,
            "r2": round(t_r2, 3) if t_r2 is not None else None,
            "mape": round(t_mape, 2) if t_mape is not None else None,
            "p50": round(p50, 2) if p50 is not None else None,
            "p90": round(p90, 2) if p90 is not None else None,
            "p95": round(p95, 2) if p95 is not None else None,
        },
        "precip": {
            "fact_hours": fact_p_hours,
            "fcst_hours": fcst_p_hours,
            "hits": hits,
            "misses": misses,
            "false_alarms": false_alarms,
            "hit_rate": round(hit_rate, 3) if hit_rate is not None else None,
            "precision": round(precision, 3) if precision is not None else None,
            "f1": round(f1, 3) if f1 is not None else None,
        },
        "scatter": scatter,
        "histogram": bins,
    }