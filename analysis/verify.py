# -*- coding: utf-8 -*-
"""
Верификация моделей: сравнение прогноза с фактом.
"""

import math
from datetime import datetime, timedelta

from core.config import MODELS, MIN_VERIFY_DATE, VERIFY_HISTORY_DAYS, log
from data.actual import fetch_actual
from data.forecast import fetch_previous_run


def _align_by_time(fact_hourly, fcst_hourly):
    f_t = dict(zip(fact_hourly.get("time", []),
                   fact_hourly.get("temperature_2m", [])))
    f_p = dict(zip(fact_hourly.get("time", []),
                   fact_hourly.get("precipitation", [])))
    o_t = dict(zip(fcst_hourly.get("time", []),
                   fcst_hourly.get("temperature_2m_previous_day1", [])))
    o_p = dict(zip(fcst_hourly.get("time", []),
                   fcst_hourly.get("precipitation", [])))
    common = sorted(set(f_t) & set(o_t))
    t_err, p_err = [], []
    for t in common:
        fv, ov = f_t.get(t), o_t.get(t)
        if fv is not None and ov is not None:
            t_err.append(ov - fv)
        fp, op = f_p.get(t), o_p.get(t)
        if fp is not None and op is not None:
            p_err.append(op - fp)
    return t_err, p_err, len(common)


def verify_model(model, lat, lon, target_date):
    if target_date < MIN_VERIFY_DATE:
        return {"model": model,
                "error": f"данные доступны только с {MIN_VERIFY_DATE}"}
    try:
        fact, fact_source = fetch_actual(lat, lon, target_date)
        fcst = fetch_previous_run(model, lat, lon, target_date)
    except Exception as e:
        log.warning("verify_model(%s) error: %s", model, e)
        return {"model": model, "error": str(e)}

    t_err, p_err, n_common = _align_by_time(
        fact.get("hourly", {}), fcst.get("hourly", {}))

    if not t_err:
        return {"model": model, "error": "нет данных",
                "source": fact_source, "common_hours": n_common}

    t_mae = sum(abs(e) for e in t_err) / len(t_err)
    t_bias = sum(t_err) / len(t_err)
    t_rmse = math.sqrt(sum(e**2 for e in t_err) / len(t_err))
    p_mae = sum(abs(e) for e in p_err) / len(p_err) if p_err else None
    p_bias = sum(p_err) / len(p_err) if p_err else None
    p_rmse = math.sqrt(sum(e**2 for e in p_err) / len(p_err)) if p_err else None

    return {
        "model": model,
        "name": MODELS[model]["name"],
        "date": target_date,
        "source": fact_source,
        "temp_mae": round(t_mae, 2),
        "temp_rmse": round(t_rmse, 2),
        "temp_bias": round(t_bias, 2),
        "prec_mae": round(p_mae, 2) if p_mae is not None else None,
        "prec_rmse": round(p_rmse, 2) if p_rmse is not None else None,
        "prec_bias": round(p_bias, 2) if p_bias is not None else None,
        "hours": len(t_err),
        "common_hours": n_common,
    }


def verify_history(lat, lon, days=VERIFY_HISTORY_DAYS):
    today = datetime.now().date()
    results = []
    for d in range(days, 0, -1):
        date_str = (today - timedelta(days=d)).strftime("%Y-%m-%d")
        day_result = {"date": date_str, "models": {}}
        for model_key in MODELS.keys():
            try:
                r = verify_model(model_key, lat, lon, date_str)
                day_result["models"][model_key] = r
            except Exception as e:
                day_result["models"][model_key] = {"error": str(e)}
        results.append(day_result)
    return results


def verify_model_noaa(model, lat, lon, target_date):
    """
    Верификация модели на исторических данных NOAA.
    target_date — строка 'YYYY-MM-DD'.
    """
    from noaa_client import find_station_with_data

    try:
        target = datetime.strptime(target_date, '%Y-%m-%d').date()
    except ValueError:
        return {"model": model, "error": "Неверный формат даты"}

    if target < datetime.strptime(MIN_VERIFY_DATE, '%Y-%m-%d').date():
        return {"model": model,
                "error": f"данные доступны только с {MIN_VERIFY_DATE}"}

    station, noaa_data = find_station_with_data(
        lat, lon, target, target, radius_km=200
    )
    if station is None:
        return {"model": model,
                "error": "нет станции NOAA с данными за эту дату"}

    try:
        fcst = fetch_previous_run(model, lat, lon, target_date)
    except Exception as e:
        return {"model": model, "error": str(e)}

    results = noaa_data.get('results', [])
    noaa_by_date = {}
    for r in results:
        d = r['date'][:10]
        dt = r['datatype']
        noaa_by_date.setdefault(d, {})[dt] = r['value']

    if target_date not in noaa_by_date:
        return {"model": model, "error": "нет данных NOAA за эту дату"}

    day = noaa_by_date[target_date]
    tmax = day.get('TMAX')
    tmin = day.get('TMIN')
    prcp = day.get('PRCP', 0)

    if tmax is None or tmin is None:
        return {"model": model, "error": "нет TMAX/TMIN в данных NOAA"}

    fh = fcst.get('hourly', {})
    f_times = fh.get('time', [])
    f_temp = fh.get('temperature_2m_previous_day1', [])
    f_prec = fh.get('precipitation', [])

    day_temps = []
    day_precs = []
    for i, t in enumerate(f_times):
        if t.startswith(target_date):
            if i < len(f_temp) and f_temp[i] is not None:
                day_temps.append(f_temp[i])
            if i < len(f_prec) and f_prec[i] is not None:
                day_precs.append(f_prec[i])

    if not day_temps:
        return {"model": model, "error": "нет прогноза за эту дату"}

    fcst_tavg = sum(day_temps) / len(day_temps)
    fcst_tmax = max(day_temps)
    fcst_tmin = min(day_temps)
    fcst_prcp = sum(day_precs) if day_precs else 0

    noaa_tavg = (tmax + tmin) / 2

    t_err = fcst_tavg - noaa_tavg
    p_err = fcst_prcp - prcp

    return {
        "model": model,
        "name": MODELS[model]["name"],
        "date": target_date,
        "source": f"NOAA · {station.get('name', '—')}",
        "temp_mae": round(abs(t_err), 2),
        "temp_rmse": round(abs(t_err), 2),
        "temp_bias": round(t_err, 2),
        "prec_mae": round(abs(p_err), 2),
        "prec_rmse": round(abs(p_err), 2),
        "prec_bias": round(p_err, 2),
        "hours": len(day_temps),
        "common_hours": len(day_temps),
        "detail": {
            "noaa_tmax": tmax,
            "noaa_tmin": tmin,
            "noaa_tavg": round(noaa_tavg, 2),
            "noaa_prcp": prcp,
            "fcst_tmax": round(fcst_tmax, 2),
            "fcst_tmin": round(fcst_tmin, 2),
            "fcst_tavg": round(fcst_tavg, 2),
            "fcst_prcp": round(fcst_prcp, 2),
        }
    }