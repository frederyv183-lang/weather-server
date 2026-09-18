# -*- coding: utf-8 -*-
"""
Генерация текстового прогноза.
"""

from collections import OrderedDict
from datetime import datetime

from core.utils import wind_dir_text


def _describe_clouds(cc):
    if cc is None: return "облачность не определена"
    if cc < 10: return "ясно"
    if cc < 30: return "малооблачно"
    if cc < 60: return "облачно с прояснениями"
    if cc < 85: return "переменная облачность"
    return "сплошная облачность"


def _describe_precip(p, code):
    if p is None or p < 0.05: return None
    if code in (71, 73, 75, 77, 85, 86):
        return "небольшой снег" if p < 0.5 else ("снег" if p < 2 else "сильный снег")
    if code in (66, 67): return "переохлаждённый дождь"
    if code in (51, 53, 55): return "слабая морось" if p < 0.3 else "морось"
    if code in (80, 81, 82):
        return "небольшие ливни" if p < 1 else ("ливни" if p < 5 else "сильные ливни")
    if code in (95, 96, 99): return "гроза"
    return "небольшой дождь" if p < 0.5 else ("дождь" if p < 2 else "сильный дождь")


def _wind_text(w):
    if w is None: return None
    if w < 1: return "штиль"
    if w < 4: return "слабый ветер"
    if w < 8: return "умеренный ветер"
    if w < 12: return "свежий ветер"
    if w < 16: return "сильный ветер"
    return "очень сильный ветер"


def _temp_range(temps):
    if not temps: return None
    tmin, tmax = min(temps), max(temps)
    def fmt(t): return f"+{int(round(t))}" if t >= 0 else f"{int(round(t))}"
    if int(round(tmin)) == int(round(tmax)): return f"{fmt(tmin)}°"
    return f"{fmt(tmin)}…{fmt(tmax)}°"


def _part_of_day(hour):
    if 0 <= hour < 6: return "Ночью"
    if 6 <= hour < 12: return "Утром"
    if 12 <= hour < 18: return "Днём"
    return "Вечером"


def _warnings(hours):
    warnings = []
    codes = [h["weather_code"] for h in hours if h["weather_code"] is not None]
    precs = [h["precipitation_mm"] for h in hours if h["precipitation_mm"] is not None]
    winds = [h["wind_ms"] for h in hours if h["wind_ms"] is not None]
    if any(c in (45, 48) for c in codes): warnings.append("ожидается туман")
    if any(c in (95, 96, 99) for c in codes): warnings.append("возможна гроза")
    if precs and max(precs) >= 5: warnings.append("сильные осадки")
    if winds and max(winds) >= 15: warnings.append("сильный ветер")
    return warnings


def generate_text_forecast(model_name, station_name, forecast):
    if not forecast: return "Нет данных для прогноза."
    by_day = OrderedDict()
    for h in forecast:
        by_day.setdefault(h["time"][:10], []).append(h)

    lines = [f"Прогноз погоды для {station_name}.", f"Модель: {model_name}.", ""]

    for day, hours in by_day.items():
        try:
            day_str = datetime.strptime(day, "%Y-%m-%d").strftime("%d.%m.%Y")
        except Exception:
            day_str = day

        warn = _warnings(hours)
        header = f"◆ {day_str}"
        if warn: header += f"  ⚠ {', '.join(warn).capitalize()}"
        lines.append(header)

        parts = OrderedDict()
        for h in hours:
            parts.setdefault(_part_of_day(int(h["time"][11:13])), []).append(h)

        for pod, pod_hours in parts.items():
            temps = [h["temp_c"] for h in pod_hours if h["temp_c"] is not None]
            winds = [h["wind_ms"] for h in pod_hours if h["wind_ms"] is not None]
            precs = [h["precipitation_mm"] for h in pod_hours if h["precipitation_mm"] is not None]
            clouds = [h["cloud_cover"] for h in pod_hours if h["cloud_cover"] is not None]
            codes = [h["weather_code"] for h in pod_hours if h["weather_code"] is not None]
            pressures = [h["pressure_hpa"] for h in pod_hours if h["pressure_hpa"] is not None]

            cloud_text = _describe_clouds(sum(clouds)/len(clouds) if clouds else None)
            precip_max = max(precs) if precs else 0
            precip_code = next((c for c in codes if c and c in
                (51,53,55,61,63,65,66,67,71,73,75,77,80,81,82,85,86,95,96,99)), None)
            precip_text = _describe_precip(precip_max, precip_code)
            temp_text = _temp_range(temps)
            wind_avg = sum(winds) / len(winds) if winds else None
            wind_desc = _wind_text(wind_avg)
            wind_dir = pod_hours[0].get("wind_dir")
            dir_text = wind_dir_text(wind_dir).split()[1] if wind_dir is not None else None
            press_mm = int(round((sum(pressures)/len(pressures)) * 0.750062)) if pressures else None

            s = f"{pod}: {cloud_text}"
            s += f", {precip_text}" if precip_text else ", без осадков"
            if temp_text: s += f", температура {temp_text}"
            if wind_desc and wind_desc != "штиль":
                s += f". Ветер {dir_text.lower()}, {wind_desc}" if dir_text else f". {wind_desc.capitalize()}"
                if wind_avg: s += f", {int(round(wind_avg))} м/с"
            elif wind_desc == "штиль":
                s += ". Штиль"
            if press_mm: s += f". Давление {press_mm} мм рт. ст."
            s += "."
            lines.append(s)
        lines.append("")

    lines.append(f"Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')} (мск).")
    return "\n".join(lines)