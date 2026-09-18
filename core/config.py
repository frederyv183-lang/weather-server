# -*- coding: utf-8 -*-
"""
Настройки, станции, модели, константы.
"""

import os
import logging

log = logging.getLogger("weather")

# ============================================================
# ПУТИ И ПАРАМЕТРЫ
# ============================================================
MAPS_DIR = "maps"
FORECAST_DAYS = 3
MIN_VERIFY_DATE = "2024-01-01"
MAX_STATION_DISTANCE_KM = 50.0
VERIFY_HISTORY_DAYS = 7

DEFAULT_LOCATION = {"name": "Москва", "lat": 55.7558, "lon": 37.6173}

# ============================================================
# СТАНЦИИ
# ============================================================
STATIONS = {
    "domodedovo": {"name": "Домодедово", "lat": 55.4100, "lon": 37.9000},
    "tushino":    {"name": "Тушино",     "lat": 55.8500, "lon": 37.4300},
}

# ============================================================
# МОДЕЛИ
# ============================================================
MODELS = {
    "gfs":   {"name": "GFS (США)",      "desc": "Глобальная модель NOAA, ~13 км",
              "endpoint": "https://api.open-meteo.com/v1/gfs"},
    "ecmwf": {"name": "ECMWF (Европа)", "desc": "Эталонная европейская модель, ~9–25 км",
              "endpoint": "https://api.open-meteo.com/v1/ecmwf"},
    "icon":  {"name": "ICON (Германия)", "desc": "Модель DWD, ~11 км",
              "endpoint": "https://api.open-meteo.com/v1/dwd-icon"},
}

API_MODEL_NAMES = {
    "gfs":   "gfs_seamless",
    "ecmwf": "ecmwf_ifs025",
    "icon":  "icon_seamless",
}

# ============================================================
# METEOSTAT
# ============================================================
# ============================================================
# ТРОПОПАУЗА
# ============================================================
TROPOPAUSE_LEVELS = [500, 400, 300, 250, 200, 150, 100]  # гПа
PVU_THRESHOLD = 2.0  # PVU — граница динамической тропопаузы
try:
    from meteostat import Point, hourly
    METEOSTAT_AVAILABLE = True
except ImportError:
    METEOSTAT_AVAILABLE = False
    log.warning("Meteostat не установлен. Установите: pip install meteostat")