# -*- coding: utf-8 -*-
"""
Утилиты: коды, направления ветра, потенциальная температура.
"""

from core.dictionaries import (
    CODE_TO_TEXT, WEATHER_ICONS, _WIND_SECTORS, _WIND_ARROWS,
)


def code_to_text(code):
    return CODE_TO_TEXT.get(code, "—")


def code_to_class(code):
    if code is None: return "unknown"
    if code == 0: return "clear"
    if code == 1: return "mostly-clear"
    if code == 2: return "partly-cloudy"
    if code == 3: return "overcast"
    if code in (45, 48): return "fog"
    if 51 <= code <= 67: return "rain"
    if 71 <= code <= 77: return "snow"
    if 80 <= code <= 82: return "showers"
    if code in (85, 86): return "snow-showers"
    if code in (95, 96, 99): return "thunder"
    return "unknown"


def icon_for_code(code):
    return WEATHER_ICONS.get(code_to_class(code), WEATHER_ICONS["unknown"])


def wind_dir_text(deg):
    if deg is None: return "—"
    idx = int((deg % 360) / 22.5 + 0.5) % 16
    return f"{_WIND_ARROWS[idx]} {_WIND_SECTORS[idx]} {int(deg)}°"


def calculate_potential_temperature(temp_c, pressure_hpa):
    if temp_c is None or pressure_hpa is None or pressure_hpa <= 0:
        return None
    T = temp_c + 273.15
    return round(T * (1000.0 / pressure_hpa) ** 0.286, 2)