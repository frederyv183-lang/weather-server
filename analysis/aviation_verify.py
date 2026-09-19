# -*- coding: utf-8 -*-
"""
Бинарная верификация явлений по критериям Хандожко.
Матрица 2×2: прогноз ДА/НЕТ vs факт ДА/НЕТ.
"""

from datetime import datetime, timedelta

from core.config import MODELS, MIN_VERIFY_DATE, log
from data.actual import fetch_actual
from data.forecast import fetch_previous_run


# ============================================================
# ОПРЕДЕЛЕНИЕ ЯВЛЕНИЙ
# ============================================================

def detect_phenomenon(hour_data, phenomenon):
    """
    Определяет, наблюдается ли явление в данный час.
    hour_data — dict с ключами:
        weather_code, temperature_2m, wind_speed_10m, precipitation
    Возвращает: True / False / None (нет данных)
    """
    if hour_data is None:
        return None

    code = hour_data.get("weather_code")
    temp = hour_data.get("temperature_2m")
    wind = hour_data.get("wind_speed_10m")
    precip = hour_data.get("precipitation")

    if phenomenon == "fog":
        if code is None: return None
        return code in (45, 48)

    if phenomenon == "thunder":
        if code is None: return None
        return code in (95, 96, 99)

    if phenomenon == "frost":
        if temp is None: return None
        return temp < 0

    if phenomenon == "wind":
        if wind is None: return None
        return wind > 15  # м/с

    if phenomenon == "rain":
        if precip is None: return None
        return precip > 0.1  # мм

    return None


# ============================================================
# МАТРИЦА 2×2
# ============================================================

def build_contingency(fact_hourly, fcst_hourly, phenomenon):
    """
    Строит матрицу сопряжённости 2×2 для бинарного явления.
    
    fact_hourly — dict: time → {weather_code, temperature_2m, ...}
    fcst_hourly — dict: time → {...}
    
    Возвращает:
    {
        "hits": int,             # прогноз ДА, факт ДА
        "misses": int,           # прогноз НЕТ, факт ДА
        "false_alarms": int,     # прогноз ДА, факт НЕТ
        "correct_negatives": int,# прогноз НЕТ, факт НЕТ
        "total": int,
        "fact_yes": int,
        "fact_no": int,
        "fcst_yes": int,
        "fcst_no": int,
    }
    """
    fact_times = set(fact_hourly.keys())
    fcst_times = set(fcst_hourly.keys())
    common = sorted(fact_times & fcst_times)

    hits = misses = false_alarms = correct_negatives = 0
    skipped = 0

    for t in common:
        f = detect_phenomenon(fact_hourly[t], phenomenon)
        o = detect_phenomenon(fcst_hourly[t], phenomenon)

        if f is None or o is None:
            skipped += 1
            continue

        if f and o:
            hits += 1
        elif f and not o:
            misses += 1
        elif not f and o:
            false_alarms += 1
        else:
            correct_negatives += 1

    total = hits + misses + false_alarms + correct_negatives

    return {
        "hits": hits,
        "misses": misses,
        "false_alarms": false_alarms,
        "correct_negatives": correct_negatives,
        "total": total,
        "fact_yes": hits + misses,
        "fact_no": false_alarms + correct_negatives,
        "fcst_yes": hits + false_alarms,
        "fcst_no": misses + correct_negatives,
        "skipped": skipped,
    }


# ============================================================
# КРИТЕРИИ ХАНДОЖКО
# ============================================================

def evaluate_criteria(ct):
    """
    Вычисляет критерии успешности по матрице 2×2.
    
    p  — общая оправдываемость: (Hits + Correct) / Total
    H  — точность попаданий: Hits / (Hits + False alarms)
    Q  — критерий Пирси-Обухова
    v  — критерий Хайдке: (Hits − False) / (Hits + False)
    τ  — критерий Обухова: Hits / (Hits + Misses)
    A  — критерий успешности: (Hits + Correct) / Total
    S  — критерий Хайдке (S = p − v)
    """
    H = ct["hits"]
    M = ct["misses"]
    F = ct["false_alarms"]
    C = ct["correct_negatives"]
    N = ct["total"]

    if N == 0:
        return {
            "p": None, "H": None, "Q": None, "v": None,
            "tau": None, "A": None, "S": None,
            "hit_rate": None, "precision": None,
            "false_alarm_rate": None, "f1": None,
        }

    p = (H + C) / N
    A = p  # совпадает с общей оправдываемостью

    H_crit = H / (H + F) if (H + F) > 0 else None  # точность попаданий

    denom_Q = (H + M) * (F + C)
    Q = ((H * C - F * M) / denom_Q) if denom_Q > 0 else None

    v = ((H - F) / (H + F)) if (H + F) > 0 else None

    tau = (H / (H + M)) if (H + M) > 0 else None

    S = (p - v) if v is not None else None

    # Стандартные метрики
    hit_rate = tau  # чувствительность
    precision = H_crit
    false_alarm_rate = F / (F + C) if (F + C) > 0 else None
    f1 = (2 * precision * hit_rate / (precision + hit_rate)
          if precision and hit_rate and (precision + hit_rate) > 0 else None)

    return {
        "p": round(p, 3),
        "H": round(H_crit, 3) if H_crit is not None else None,
        "Q": round(Q, 3) if Q is not None else None,
        "v": round(v, 3) if v is not None else None,
        "tau": round(tau, 3) if tau is not None else None,
        "A": round(A, 3),
        "S": round(S, 3) if S is not None else None,
        "hit_rate": round(hit_rate, 3) if hit_rate is not None else None,
        "precision": round(precision, 3) if precision is not None else None,
        "false_alarm_rate": round(false_alarm_rate, 3) if false_alarm_rate is not None else None,
        "f1": round(f1, 3) if f1 is not None else None,
    }


# ============================================================
# АГРЕГАЦИЯ ПО ПЕРИОДУ
# ============================================================

def _to_hourly_dict(hourly):
    """Преобразует hourly-массив Open-Meteo в dict: time → {fields}."""
    times = hourly.get("time", [])
    result = {}
    for i, t in enumerate(times):
        result[t] = {
            "weather_code": (hourly.get("weather_code") or [None])[i]
                            if i < len(hourly.get("weather_code") or []) else None,
            "temperature_2m": (hourly.get("temperature_2m") or [None])[i]
                              if i < len(hourly.get("temperature_2m") or []) else None,
            "wind_speed_10m": (hourly.get("wind_speed_10m") or [None])[i]
                              if i < len(hourly.get("wind_speed_10m") or []) else None,
            "precipitation": (hourly.get("precipitation") or [None])[i]
                             if i < len(hourly.get("precipitation") or []) else None,
        }
    return result


def _fcst_to_hourly_dict(hourly):
    """Аналогично, но с суффиксом _previous_day1 для T и weather_code."""
    times = hourly.get("time", [])
    result = {}
    for i, t in enumerate(times):
        def _get(key, default_key=None):
            arr = hourly.get(key) or hourly.get(default_key or key)
            if not arr or i >= len(arr):
                return None
            return arr[i]
        result[t] = {
            "weather_code": _get("weather_code_previous_day1", "weather_code"),
            "temperature_2m": _get("temperature_2m_previous_day1", "temperature_2m"),
            "wind_speed_10m": _get("wind_speed_10m_previous_day1", "wind_speed_10m"),
            "precipitation": _get("precipitation", "precipitation"),
        }
    return result


def evaluate_all(model_key, lat, lon, phenomenon="fog", days=14):
    """
    Верифицирует одну модель по одному явлению за N дней.
    
    Возвращает:
    {
        "model_key": ..., "model_name": ...,
        "phenomenon": "fog", "days": 14,
        "contingency": {hits, misses, ...},
        "criteria": {p, H, Q, v, tau, A, S, ...},
        "by_day": [{"date": ..., "contingency": {...}}, ...],
        "error": None | "..."
    }
    """
    today = datetime.now().date()
    total_ct = {
        "hits": 0, "misses": 0, "false_alarms": 0, "correct_negatives": 0,
        "total": 0, "fact_yes": 0, "fact_no": 0,
        "fcst_yes": 0, "fcst_no": 0, "skipped": 0,
    }
    by_day = []

    for d in range(days, 0, -1):
        date_str = (today - timedelta(days=d)).strftime("%Y-%m-%d")
        if date_str < MIN_VERIFY_DATE:
            continue

        try:
            fact, source = fetch_actual(lat, lon, date_str)
            fcst = fetch_previous_run(model_key, lat, lon, date_str)
        except Exception as e:
            log.warning("evaluate_all: %s %s error: %s", model_key, date_str, e)
            by_day.append({"date": date_str, "error": str(e)})
            continue

        fact_dict = _to_hourly_dict(fact.get("hourly", {}))
        fcst_dict = _fcst_to_hourly_dict(fcst.get("hourly", {}))

        ct = build_contingency(fact_dict, fcst_dict, phenomenon)

        by_day.append({
            "date": date_str,
            "contingency": ct,
            "criteria": evaluate_criteria(ct) if ct["total"] > 0 else None,
        })

        for k in total_ct:
            total_ct[k] += ct.get(k, 0)

    criteria_total = evaluate_criteria(total_ct) if total_ct["total"] > 0 else None

    return {
        "model_key": model_key,
        "model_name": MODELS[model_key]["name"],
        "phenomenon": phenomenon,
        "days": days,
        "contingency": total_ct,
        "criteria": criteria_total,
        "by_day": by_day,
        "error": None if total_ct["total"] > 0 else "нет данных за период",
    }


def compare_all_models(lat, lon, phenomenon="fog", days=14):
    """Верифицирует все модели по одному явлению."""
    results = []
    for model_key in MODELS:
        try:
            r = evaluate_all(model_key, lat, lon, phenomenon, days)
        except Exception as e:
            log.exception("compare_all_models: %s error: %s", model_key, e)
            r = {
                "model_key": model_key,
                "model_name": MODELS[model_key]["name"],
                "error": str(e),
            }
        results.append(r)
    return results