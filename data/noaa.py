# -*- coding: utf-8 -*-
"""
Обёртка над noaa_client для единообразия.
"""

from noaa_client import (
    find_nearest_stations,
    get_actuals,
    find_and_get_actuals,
    get_actuals_range,
    find_station_with_data,
)

__all__ = [
    "find_nearest_stations",
    "get_actuals",
    "find_and_get_actuals",
    "get_actuals_range",
    "find_station_with_data",
]