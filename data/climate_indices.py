# -*- coding: utf-8 -*-
"""
Климатические индексы: ENSO, SSW, PV.

Источники данных:
  - Open-Meteo Archive API (ERA5 reanalysis, 1940 — настоящее) — для ENSO (приземные)
  - Open-Meteo Historical Forecast API — для SSW и PV (высотные уровни, с 2021)

Что считается:
  - ENSO: SST в Niño 3.4, ONI, классификация El Niño / La Niña / нейтраль
  - SSW: T и U на 10 гПа в Арктике, обнаружение внезапных стратосферных потеплений
  - PV: геопотенциал 10 гПа, зональный ветер на 60°N, интенсивность полярного вихря
"""

import logging
from datetime import date, timedelta
from statistics import mean

from core.http import _session


log = logging.getLogger("weather.climate")


# ============================================================
# КОНСТАНТЫ
# ============================================================

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
HISTORICAL_FORECAST_URL = "https://historical-forecast-api.open-meteo.com/v1/forecast"

# Niño 3.4: 5°N–5°S, 120°W–170°W
NINO34 = {
    "lat": 0.0,
    "lon": -150.0,
    "name": "Niño 3.4",
}

# Арктика — 60°N, для стратосферных индексов
ARCTIC = {
    "lat": 60.0,
    "lon": 0.0,
    "name": "Арктика (60°N, 0°)",
}

# Климатический период для аномалий
CLIMATE_START = "1991-01-01"
CLIMATE_END = "2020-12-31"

# Пороги ONI (Oceanic Niño Index), 3-месячное скользящее среднее
ONI_EL_NINO = 0.5
ONI_LA_NINA = -0.5
ONI_STRONG = 1.5

# Пороги SSW (Sudden Stratospheric Warming)
SSW_TEMP_ANOMALY = 25.0
SSW_WIND_THRESHOLD = 0.0

# Модель для высотных уровней (Historical Forecast API)
PRESSURE_MODEL = "gfs_pressure_levels"


# ============================================================
# ЗАПРОСЫ К API
# ============================================================

def _fetch_archive(lat, lon, start_date, end_date, daily_vars=None, hourly_vars=None):
    """Запрос к Open-Meteo Archive API (ERA5). Только приземные переменные."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "UTC",
    }
    if daily_vars:
        params["daily"] = ",".join(daily_vars)
    if hourly_vars:
        params["hourly"] = ",".join(hourly_vars)

    try:
        r = _session.get(ARCHIVE_URL, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.exception("climate: archive fetch error: %s", e)
        return None


def _fetch_historical_forecast(lat, lon, start_date, end_date, hourly_vars):
    """
    Запрос к Open-Meteo Historical Forecast API.
    Поддерживает высотные уровни давления (в отличие от Archive API/ERA5).
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(hourly_vars),
        "models": PRESSURE_MODEL,
        "timezone": "UTC",
    }

    try:
        r = _session.get(HISTORICAL_FORECAST_URL, params=params, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.exception("climate: historical forecast fetch error: %s", e)
        return None


def _fetch_pressure_level(lat, lon, start_date, end_date, level_hpa=10):
    """
    Запрос давления на конкретном уровне через Historical Forecast API.

    Open-Meteo использует суффикс hPa, а не Pa:
      temperature_10hPa, geopotential_height_10hPa,
      wind_speed_10hPa, wind_direction_10hPa
    """
    hourly = [
        f"temperature_{level_hpa}hPa",
        f"geopotential_height_{level_hpa}hPa",
        f"wind_speed_{level_hpa}hPa",
        f"wind_direction_{level_hpa}hPa",
    ]
    return _fetch_historical_forecast(lat, lon, start_date, end_date, hourly)


# ============================================================
# ENSO — Niño 3.4
# ============================================================

def fetch_nino34_sst(start_date, end_date):
    """
    Возвращает список (date, sst_c) — суточные значения SST в Niño 3.4.
    Open-Meteo не отдаёт SST напрямую, используем T2m над океаном как прокси.
    """
    data = _fetch_archive(
        NINO34["lat"], NINO34["lon"],
        start_date, end_date,
        daily_vars=["temperature_2m_mean"],
    )
    if not data:
        return []

    daily = data.get("daily", {})
    times = daily.get("time", [])
    temps = daily.get("temperature_2m_mean", [])

    out = []
    for t, v in zip(times, temps):
        if v is not None:
            out.append((t, v))
    return out


def fetch_nino34_climate_mean(month):
    """Климатическое среднее SST в Niño 3.4 для данного месяца (1-12)."""
    data = _fetch_archive(
        NINO34["lat"], NINO34["lon"],
        CLIMATE_START, CLIMATE_END,
        daily_vars=["temperature_2m_mean"],
    )
    if not data:
        return None

    daily = data.get("daily", {})
    times = daily.get("time", [])
    temps = daily.get("temperature_2m_mean", [])

    vals = []
    for t, v in zip(times, temps):
        if v is None:
            continue
        try:
            m = int(t[5:7])
            if m == month:
                vals.append(v)
        except Exception:
            continue

    return round(mean(vals), 2) if vals else None


def calculate_oni_monthly(sst_series, climate_means_by_month):
    """Считает ONI — 3-месячное скользящее среднее аномалии SST в Niño 3.4."""
    by_month = {}
    for date_str, v in sst_series:
        try:
            m = int(date_str[5:7])
            y = int(date_str[:4])
            key = (y, m)
            by_month.setdefault(key, []).append(v)
        except Exception:
            continue

    monthly_anomalies = []
    for (y, m), vals in sorted(by_month.items()):
        clim = climate_means_by_month.get(m)
        if clim is None:
            continue
        anom = mean(vals) - clim
        monthly_anomalies.append({
            "year": y,
            "month": m,
            "anomaly": round(anom, 2),
        })

    result = []
    for i in range(len(monthly_anomalies) - 2):
        a = monthly_anomalies[i]["anomaly"]
        b = monthly_anomalies[i + 1]["anomaly"]
        c = monthly_anomalies[i + 2]["anomaly"]
        oni = round((a + b + c) / 3.0, 2)
        result.append({
            "year": monthly_anomalies[i + 2]["year"],
            "month": monthly_anomalies[i + 2]["month"],
            "anomaly": monthly_anomalies[i + 2]["anomaly"],
            "oni": oni,
        })
    return result


def classify_enso(oni):
    """Классификация по ONI."""
    if oni is None:
        return "нет данных"
    if oni >= ONI_STRONG:
        return "сильный Эль-Ниньо"
    if oni >= ONI_EL_NINO:
        return "Эль-Ниньо"
    if oni <= -ONI_STRONG:
        return "сильный Ла-Нинья"
    if oni <= ONI_LA_NINA:
        return "Ла-Нинья"
    return "нейтральная фаза"


# ============================================================
# SSW — Sudden Stratospheric Warming
# ============================================================

def fetch_stratosphere(lat, lon, start_date, end_date, level_hpa=10):
    """Возвращает список dict с полями time, t_c, gph_m, wind_ms, wind_dir."""
    data = _fetch_pressure_level(lat, lon, start_date, end_date, level_hpa)
    if not data:
        return []

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])

    # ВАЖНО: суффикс hPa, а не Pa
    t_key = f"temperature_{level_hpa}hPa"
    gph_key = f"geopotential_height_{level_hpa}hPa"
    ws_key = f"wind_speed_{level_hpa}hPa"
    wd_key = f"wind_direction_{level_hpa}hPa"

    ts = hourly.get(t_key, [])
    gph = hourly.get(gph_key, [])
    ws = hourly.get(ws_key, [])
    wd = hourly.get(wd_key, [])

    n = len(times)
    out = []
    for i in range(n):
        out.append({
            "time": times[i],
            "t_c": ts[i] if i < len(ts) else None,
            "gph_m": gph[i] if i < len(gph) else None,
            "wind_ms": ws[i] if i < len(ws) else None,
            "wind_dir": wd[i] if i < len(wd) else None,
        })
    return out


def detect_ssw_events(strat_data, window_days=7):
    """Ищет события SSW: резкий скачок T на 10 гПа за N суток."""
    if not strat_data:
        return []

    by_day = {}
    for row in strat_data:
        d = row["time"][:10]
        if row["t_c"] is not None:
            by_day.setdefault(d, []).append(row["t_c"])

    days_sorted = sorted(by_day.keys())
    daily_t = {d: mean(by_day[d]) for d in days_sorted if by_day[d]}

    events = []
    for i, d in enumerate(days_sorted):
        if i < window_days:
            continue
        prev_d = days_sorted[i - window_days]
        t_now = daily_t.get(d)
        t_prev = daily_t.get(prev_d)
        if t_now is None or t_prev is None:
            continue

        anomaly = t_now - t_prev
        if anomaly >= SSW_TEMP_ANOMALY:
            events.append({
                "date": d,
                "t_anomaly_c": round(anomaly, 1),
                "wind_reversal": None,
                "description": (
                    f"Скачок температуры 10 гПа на +{anomaly:.1f} °C "
                    f"за {window_days} суток"
                ),
            })

    return events


# ============================================================
# PV — Polar Vortex
# ============================================================

def fetch_polar_vortex(start_date, end_date):
    """Индекс полярного вихря: геопотенциал и ветер 10 гПа на 60°N."""
    return fetch_stratosphere(ARCTIC["lat"], ARCTIC["lon"],
                              start_date, end_date, level_hpa=10)


def pv_strength_index(pv_data):
    """Средний геопотенциал 10 гПа за период."""
    vals = [row["gph_m"] for row in pv_data if row["gph_m"] is not None]
    if not vals:
        return None
    return round(mean(vals), 0)


def pv_classify(gph_mean):
    """Классификация по среднему геопотенциалу 10 гПа (ERA5)."""
    if gph_mean is None:
        return "нет данных"
    if gph_mean < 29000:
        return "очень сильный"
    if gph_mean < 30000:
        return "сильный"
    if gph_mean < 30500:
        return "норма"
    if gph_mean < 31000:
        return "ослабленный"
    return "разрушенный (возможен SSW)"


# ============================================================
# СВОДНЫЙ ОТЧЁТ
# ============================================================

def build_climate_report(days_back=365):
    """Собирает единый отчёт по всем трём индексам за последние N дней."""
    end = date.today()
    start = end - timedelta(days=days_back)
    start_s = start.isoformat()
    end_s = end.isoformat()

    report = {
        "period": {"start": start_s, "end": end_s},
        "enso": None,
        "ssw": None,
        "pv": None,
        "error": None,
    }

    # --- ENSO ---
    try:
        sst_series = fetch_nino34_sst(start_s, end_s)

        clim = {}
        for m in range(1, 13):
            clim[m] = fetch_nino34_climate_mean(m)

        oni_list = calculate_oni_monthly(sst_series, clim)
        current_oni = oni_list[-1]["oni"] if oni_list else None

        report["enso"] = {
            "current_oni": current_oni,
            "classification": classify_enso(current_oni),
            "recent": oni_list[-12:] if oni_list else [],
            "nino34_series": sst_series[-180:] if sst_series else [],
        }
    except Exception as e:
        log.exception("climate: ENSO error: %s", e)
        report["enso"] = {"error": str(e)}

    # --- SSW ---
    try:
        strat = fetch_stratosphere(ARCTIC["lat"], ARCTIC["lon"],
                                   start_s, end_s, level_hpa=10)
        events = detect_ssw_events(strat)
        report["ssw"] = {
            "events": events[-10:],
            "n_events": len(events),
            "recent_t": [
                {"time": r["time"], "t_c": r["t_c"]}
                for r in strat[-240:] if r["t_c"] is not None
            ],
        }
    except Exception as e:
        log.exception("climate: SSW error: %s", e)
        report["ssw"] = {"error": str(e)}

    # --- PV ---
    try:
        pv = fetch_polar_vortex(start_s, end_s)
        gph_mean = pv_strength_index(pv)
        report["pv"] = {
            "gph_mean": gph_mean,
            "classification": pv_classify(gph_mean),
            "recent": [
                {"time": r["time"], "gph_m": r["gph_m"], "wind_ms": r["wind_ms"]}
                for r in pv[-240:]
            ],
        }
    except Exception as e:
        log.exception("climate: PV error: %s", e)
        report["pv"] = {"error": str(e)}

    return report