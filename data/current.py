# -*- coding: utf-8 -*-
"""
Текущая погода (Open-Meteo).
"""

from core.cache import _current_cache
from core.http import _session


def fetch_current(lat, lon):
    cache_key = ("current", round(lat, 3), round(lon, 3))
    cached = _current_cache.get(cache_key)
    if cached is not None: return cached
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"is_day,precipitation,weather_code,cloud_cover,pressure_msl,"
        f"wind_speed_10m,wind_direction_10m,wind_gusts_10m"
        f"&hourly=temperature_2m,weather_code,precipitation_probability"
        f"&forecast_hours=6"
        f"&timezone=Europe/Moscow"
    )
    r = _session.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    _current_cache.set(cache_key, data)
    return data