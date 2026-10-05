# -*- coding: utf-8 -*-
# SOUNDING_MAP v1
"""Станции зондирования: загрузка, кэш, поиск ближайших."""

import json
import math
import time
from pathlib import Path
from urllib.request import urlopen

CACHE_PATH = Path(__file__).parent / "stations_cache.json"
CACHE_TTL_SECONDS = 24 * 3600  # обновление раз в сутки


# Встроенный fallback — если и Wyoming недоступен, и кэша нет.
# STATIONS_LIST v2 (10 рабочих станций)
BUILTIN_STATIONS = [
    # ===== США (ICAO) =====
    {"station": "ALB", "name": "Albany (NY)",       "lat": 42.75, "lon": -73.80, "elev": 89},
    {"station": "BUF", "name": "Buffalo (NY)",      "lat": 42.94, "lon": -78.73, "elev": 218},
    {"station": "OUN", "name": "Norman (OK)",       "lat": 35.23, "lon": -97.46, "elev": 357},
    {"station": "MPX", "name": "Minneapolis (MN)",  "lat": 44.85, "lon": -93.57, "elev": 288},
    {"station": "ILX", "name": "Lincoln (IL)",      "lat": 40.15, "lon": -89.33, "elev": 178},
    {"station": "TOP", "name": "Topeka (KS)",       "lat": 39.07, "lon": -95.62, "elev": 268},
    {"station": "LZK", "name": "Little Rock (AR)",  "lat": 34.83, "lon": -92.26, "elev": 88},
    # ===== Россия (WMO) =====
    {"station": "27730", "name": "Tula",            "lat": 54.20, "lon": 37.62,  "elev": 168},
    {"station": "27962", "name": "Penza",           "lat": 53.20, "lon": 45.00,  "elev": 174},
    {"station": "28661", "name": "Kazan",          "lat": 55.79, "lon": 49.11,  "elev": 116},
]



def _load_cache():
    """Читает кэш с диска, если есть."""
    if not CACHE_PATH.exists():
        return None
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        return data.get("stations"), data.get("updated_at", 0)
    except Exception:
        return None


def _save_cache(stations):
    """Сохраняет список станций на диск."""
    try:
        CACHE_PATH.write_text(
            json.dumps({"updated_at": int(time.time()), "stations": stations},
                       ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception as e:
        print("[stations] save cache error: %s" % e)


def _fetch_from_wyoming():
    """Загружает список станций с WyomingUpperAir. Возвращает list[dict] или None."""
    try:
        from siphon.simplewebservice.wyoming import WyomingUpperAir
        # Wyoming не имеет JSON-списка; используем встроенный + сохраняем.
        # Для автообновления — вызывать не будем (см. примечание в конце).
        return None
    except Exception:
        return None


def get_stations():
    """Список станций: кэш → Wyoming → fallback."""
    cache = _load_cache()
    if cache:
        stations, updated_at = cache
        if stations and (time.time() - updated_at) < CACHE_TTL_SECONDS:
            return stations

    # Пробуем обновить с Wyoming — пока нет источника, остаёмся на BUILTIN.
    fetched = _fetch_from_wyoming()
    stations = fetched or (cache[0] if cache and cache[0] else BUILTIN_STATIONS)

    _save_cache(stations)
    return stations


def haversine_km(lat1, lon1, lat2, lon2):
    """Расстояние между двумя точками на сфере (км)."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def find_nearest_stations(lat, lon, n=5):
    """Топ-N ближайших станций."""
    stations = get_stations()
    with_d = []
    for s in stations:
        try:
            d = haversine_km(lat, lon, s["lat"], s["lon"])
            item = dict(s)
            item["distance_km"] = round(d, 1)
            with_d.append(item)
        except Exception:
            continue
    with_d.sort(key=lambda x: x["distance_km"])
    return with_d[:n]
