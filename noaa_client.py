# -*- coding: utf-8 -*-
"""
Модуль для работы с NOAA NCEI.
Поиск станций по координатам и получение фактических данных.
"""

import os
import requests
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()

# Токен хранится в файле .env (см. .env.example)
NOAA_TOKEN = os.environ.get("NOAA_TOKEN", "")

BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2"


def _headers():
    return {'token': NOAA_TOKEN}


def haversine(lat1, lon1, lat2, lon2):
    """Расстояние между двумя точками на Земле в километрах."""
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def find_nearest_stations(lat, lon, radius_km=50, limit=10):
    """
    Находит ближайшие станции NOAA к заданным координатам.
    Возвращает список словарей с полями: id, name, latitude, longitude, distance_km.
    """
    delta = radius_km / 111.0
    extent = f"{lat - delta},{lon - delta},{lat + delta},{lon + delta}"

    url = f"{BASE_URL}/stations"
    params = {
        'datasetid': 'GHCND',
        'extent': extent,
        'limit': limit
    }

    try:
        response = requests.get(url, params=params, headers=_headers(), timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[NOAA] Ошибка поиска станций: {e}")
        return []

    stations = data.get('results', [])
    for station in stations:
        station['distance_km'] = haversine(lat, lon, station['latitude'], station['longitude'])

    stations.sort(key=lambda s: s['distance_km'])
    return stations


def get_actuals(station_id, days=7):
    """
    Получает фактические данные (TMAX, TMIN, PRCP) с NOAA NCEI.
    station_id: ID в формате NOAA, например 'GHCND:RSM00027612'.
    """
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    url = f"{BASE_URL}/data"
    params = {
        'datasetid': 'GHCND',
        'stationid': station_id,
        'startdate': start_date,
        'enddate': end_date,
        'datatypeid': 'TMAX,TMIN,PRCP',
        'units': 'metric',
        'limit': 1000
    }

    try:
        response = requests.get(url, params=params, headers=_headers(), timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[NOAA] Ошибка получения данных: {e}")
        return None


def get_actuals_range(station_id, start_date, end_date):
    """
    Получает данные с NOAA NCEI за указанный период.
    start_date, end_date — объекты datetime.date.
    """
    url = f"{BASE_URL}/data"
    params = {
        'datasetid': 'GHCND',
        'stationid': station_id,
        'startdate': start_date.isoformat(),
        'enddate': end_date.isoformat(),
        'datatypeid': 'TMAX,TMIN,PRCP',
        'units': 'metric',
        'limit': 1000
    }
    try:
        response = requests.get(url, params=params, headers=_headers(), timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[NOAA] Ошибка получения данных: {e}")
        return None


def find_and_get_actuals(lat, lon, radius_km=50, days=7):
    """
    Удобная обёртка: находит ближайшую станцию и сразу тянет с неё данные.
    """
    stations = find_nearest_stations(lat, lon, radius_km=radius_km, limit=5)
    if not stations:
        return None, []

    nearest = stations[0]
    actuals = get_actuals(nearest['id'], days=days)
    return nearest, actuals


def find_station_with_data(lat, lon, start_date, end_date, radius_km=100):
    """
    Находит ближайшую станцию NOAA, у которой есть данные за указанный период.
    Возвращает (station, data) или (None, None).
    """
    stations = find_nearest_stations(lat, lon, radius_km=radius_km, limit=20)

    for station in stations:
        maxdate_str = station.get('maxdate')
        mindate_str = station.get('mindate')

        if not maxdate_str or not mindate_str:
            continue

        try:
            maxdate = datetime.strptime(maxdate_str, '%Y-%m-%d').date()
            mindate = datetime.strptime(mindate_str, '%Y-%m-%d').date()
        except ValueError:
            continue

        if mindate <= start_date and maxdate >= end_date:
            data = get_actuals_range(station['id'], start_date, end_date)
            if data:
                return station, data

    return None, None