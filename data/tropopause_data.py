# -*- coding: utf-8 -*-
"""
Получение данных для анализа тропопаузы.
Использует Open-Meteo API — изобарические поверхности.
"""

from core.config import TROPOPAUSE_LEVELS
from core.http import _session
from core.cache import _verify_cache


def fetch_pressure_level_data(lat, lon, target_date):
    """
    Запрашивает температуру, ветер и геопотенциал на изобарических
    поверхностях за указанную дату.
    
    target_date: 'YYYY-MM-DD'
    Возвращает dict с массивами по уровням давления.
    """
    cache_key = ("tropopause", round(lat, 3), round(lon, 3), target_date)
    cached = _verify_cache.get(cache_key)
    if cached is not None:
        return cached

    # Формируем список переменных для каждого уровня
    hourly_vars = []
    for level in TROPOPAUSE_LEVELS:
        hourly_vars.extend([
            f"temperature_{level}hPa",
            f"wind_speed_{level}hPa",
            f"wind_direction_{level}hPa",
            f"geopotential_height_{level}hPa",
            f"relative_humidity_{level}hPa",
        ])
    hourly_str = ",".join(hourly_vars)

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly={hourly_str}"
        f"&start_date={target_date}&end_date={target_date}"
        f"&timezone=Europe/Moscow"
    )

    r = _session.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    _verify_cache.set(cache_key, data)
    return data


def fetch_pressure_level_data_batch(lat, lon, start_date, end_date):
    """
    Запрашивает данные за диапазон дат (для карт по нескольким дням).
    """
    cache_key = ("tropopause_batch", round(lat, 3), round(lon, 3),
                 start_date, end_date)
    cached = _verify_cache.get(cache_key)
    if cached is not None:
        return cached

    hourly_vars = []
    for level in TROPOPAUSE_LEVELS:
        hourly_vars.extend([
            f"temperature_{level}hPa",
            f"wind_speed_{level}hPa",
            f"wind_direction_{level}hPa",
            f"geopotential_height_{level}hPa",
        ])
    hourly_str = ",".join(hourly_vars)

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly={hourly_str}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&timezone=Europe/Moscow"
    )

    r = _session.get(url, timeout=60)
    r.raise_for_status()
    data = r.json()
    _verify_cache.set(cache_key, data)
    return data