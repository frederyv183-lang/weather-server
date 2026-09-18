# -*- coding: utf-8 -*-
"""
Получение прогнозов от Open-Meteo.
"""

from core.config import MODELS, API_MODEL_NAMES, FORECAST_DAYS
from core.cache import _forecast_cache, _verify_cache
from core.http import _session


def fetch_forecast(model, lat, lon, days=FORECAST_DAYS):
    if model not in MODELS:
        raise ValueError(f"Неизвестная модель: {model}")
    cache_key = (model, round(lat, 4), round(lon, 4), days)
    cached = _forecast_cache.get(cache_key)
    if cached is not None: return cached
    endpoint = MODELS[model]["endpoint"]
    url = (
        f"{endpoint}"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly=precipitation,weather_code,"
        f"temperature_2m,dew_point_2m,wind_speed_10m,wind_direction_10m,"
        f"relative_humidity_2m,pressure_msl,cloud_cover,wind_gusts_10m,"
        f"cape,lifted_index,"
        f"temperature_500hPa,temperature_700hPa,dew_point_700hPa,"
        f"temperature_850hPa,dew_point_850hPa"
        f"&forecast_days={days}"
        f"&timezone=Europe/Moscow"
    )
    r = _session.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    _forecast_cache.set(cache_key, data)
    return data


def fetch_previous_run(model, lat, lon, target_date):
    """Прогноз модели за сутки (Previous Runs API)."""
    api_model = API_MODEL_NAMES.get(model, model)
    cache_key = ("prevrun", api_model, round(lat, 4), round(lon, 4), target_date)
    cached = _verify_cache.get(cache_key)
    if cached is not None: return cached
    url = (
        f"https://previous-runs-api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={target_date}&end_date={target_date}"
        f"&hourly=temperature_2m_previous_day1,precipitation,"
        f"weather_code_previous_day1,wind_speed_10m_previous_day1"
        f"&models={api_model}"
        f"&timezone=Europe/Moscow"
    )
    r = _session.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    _verify_cache.set(cache_key, data)
    return data