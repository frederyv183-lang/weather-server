# -*- coding: utf-8 -*-
"""
Фактические данные: Meteostat + ERA5.
"""

from datetime import datetime

from core.config import (
    METEOSTAT_AVAILABLE, MAX_STATION_DISTANCE_KM,
)
from core.cache import _verify_cache
from core.http import _session
from core.config import log


def _nearest_station_distance(lat, lon):
    if not METEOSTAT_AVAILABLE:
        return None, None
    try:
        from meteostat import Stations, Point
        nearby = Stations().nearby(Point(lat, lon)).fetch(1)
        if nearby.empty: return None, None
        row = nearby.iloc[0]
        return row, float(row.get("distance", 0.0))
    except Exception as e:
        log.warning("Meteostat Stations error: %s", e)
        return None, None


def fetch_station_actual(lat, lon, target_date, force=False):
    if not METEOSTAT_AVAILABLE: return None
    station_row, distance_km = _nearest_station_distance(lat, lon)
    if station_row is None: return None
    limit = MAX_STATION_DISTANCE_KM if not force else 200.0
    if distance_km is None or distance_km > limit:
        log.info("Станция слишком далеко (%.1f км > %.1f) — fallback на ERA5",
                 distance_km or -1, limit)
        return None
    try:
        from meteostat import Point, hourly
        start = datetime.strptime(target_date, "%Y-%m-%d")
        end = start.replace(hour=23, minute=59)
        location = Point(lat, lon, 100)
        df = hourly(location, start, end).fetch()
        if df.empty: return None
        return {
            "hourly": {
                "time": [t.strftime("%Y-%m-%dT%H:%M") for t in df.index],
                "temperature_2m": df["temp"].tolist(),
                "precipitation": df["prcp"].fillna(0).tolist(),
                "wind_speed_10m": (df["wspd"] / 3.6).tolist(),
                "wind_direction_10m": df["wdir"].tolist(),
                "relative_humidity_2m": df["rhum"].tolist(),
                "pressure_msl": df["pres"].tolist(),
                "weather_code": [None] * len(df.index),
            },
            "_source": "станция",
            "_station": str(station_row.get("name", "")),
            "_distance_km": round(distance_km, 1),
        }
    except Exception as e:
        log.warning("Meteostat hourly error: %s", e)
        return None


def check_station_availability(lat, lon, force=False):
    result = {
        "available": False,
        "name": None,
        "distance_km": None,
        "reason": None,
        "max_distance_km": MAX_STATION_DISTANCE_KM if not force else 200.0,
        "meteostat_available": METEOSTAT_AVAILABLE,
    }
    if not METEOSTAT_AVAILABLE:
        result["reason"] = "библиотека meteostat не установлена"
        return result
    try:
        station_row, distance_km = _nearest_station_distance(lat, lon)
        if station_row is None:
            result["reason"] = "станция не найдена в радиусе поиска"
            return result
        result["name"] = str(station_row.get("name", "—"))
        result["distance_km"] = round(distance_km, 1) if distance_km else None
        limit = result["max_distance_km"]
        if distance_km is None or distance_km > limit:
            result["reason"] = (
                f"станция «{result['name']}» слишком далеко "
                f"({result['distance_km']} км > {limit} км)"
            )
            return result
        result["available"] = True
        return result
    except Exception as e:
        result["reason"] = f"ошибка Meteostat: {e}"
        return result


def fetch_archive(lat, lon, start_date, end_date):
    """Факт из ERA5 с weather_code и wind_speed_10m."""
    cache_key = ("archive", round(lat, 4), round(lon, 4), start_date, end_date)
    cached = _verify_cache.get(cache_key)
    if cached is not None: return cached
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly=temperature_2m,precipitation,weather_code,wind_speed_10m"
        f"&timezone=Europe/Moscow"
    )
    r = _session.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    data["_source"] = "ERA5"
    _verify_cache.set(cache_key, data)
    return data


def fetch_actual(lat, lon, target_date, force_station=False):
    station_data = fetch_station_actual(lat, lon, target_date, force=force_station)
    if station_data is not None:
        label = f"станция {station_data.get('_station', '')}".strip()
        return station_data, label
    era5_data = fetch_archive(lat, lon, target_date, target_date)
    return era5_data, "ERA5"