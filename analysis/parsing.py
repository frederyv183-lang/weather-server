# -*- coding: utf-8 -*-
"""
Парсинг hourly-данных Open-Meteo в список часов.
"""

from collections import OrderedDict

from core.utils import (
    code_to_class, code_to_text, icon_for_code,
    wind_dir_text, calculate_potential_temperature,
)
from analysis.aviation import combined_thunder_risk, fog_forecast


def parse_hourly(data):
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])

    # --- Приземные ---
    prec  = hourly.get("precipitation", [])
    code  = hourly.get("weather_code", [])
    temp  = hourly.get("temperature_2m", [])
    wind  = hourly.get("wind_speed_10m", [])
    wdir  = hourly.get("wind_direction_10m", [])
    rh    = hourly.get("relative_humidity_2m", [])
    press = hourly.get("pressure_msl", [])
    cloud = hourly.get("cloud_cover", [])
    gust  = hourly.get("wind_gusts_10m", [])
    dew2m = hourly.get("dew_point_2m", [])
    cape_arr = hourly.get("cape", [])
    li_arr   = hourly.get("lifted_index", [])

    # --- Уровни: температура ---
    t925 = hourly.get("temperature_925hPa", [])
    t850 = hourly.get("temperature_850hPa", [])
    t700 = hourly.get("temperature_700hPa", [])
    t500 = hourly.get("temperature_500hPa", [])
    t300 = hourly.get("temperature_300hPa", [])

    # --- Уровни: точка росы ---
    td925 = hourly.get("dew_point_925hPa", [])
    td850 = hourly.get("dew_point_850hPa", [])
    td700 = hourly.get("dew_point_700hPa", [])
    td500 = hourly.get("dew_point_500hPa", [])
    td300 = hourly.get("dew_point_300hPa", [])

    # --- Уровни: ветер (скорость + направление) ---
    w925  = hourly.get("wind_speed_925hPa", [])
    wd925 = hourly.get("wind_direction_925hPa", [])
    w850  = hourly.get("wind_speed_850hPa", [])
    wd850 = hourly.get("wind_direction_850hPa", [])
    w700  = hourly.get("wind_speed_700hPa", [])
    wd700 = hourly.get("wind_direction_700hPa", [])
    w500  = hourly.get("wind_speed_500hPa", [])
    wd500 = hourly.get("wind_direction_500hPa", [])
    w300  = hourly.get("wind_speed_300hPa", [])
    wd300 = hourly.get("wind_direction_300hPa", [])

    # --- Уровни: геопотенциальная высота ---
    h925 = hourly.get("geopotential_height_925hPa", [])
    h850 = hourly.get("geopotential_height_850hPa", [])
    h700 = hourly.get("geopotential_height_700hPa", [])
    h500 = hourly.get("geopotential_height_500hPa", [])
    h300 = hourly.get("geopotential_height_300hPa", [])

    def _at(arr, i):
        return arr[i] if i < len(arr) else None

    result = []
    for i, t in enumerate(times):
        c = _at(code, i)
        p = _at(prec, i) or 0
        t_c = _at(temp, i)
        pr = _at(press, i)
        rh_i = _at(rh, i)
        cloud_i = _at(cloud, i)
        wind_i = _at(wind, i)
        dew2m_i = _at(dew2m, i)
        cape_i = _at(cape_arr, i)
        li_i = _at(li_arr, i)
        hour_int = int(t[11:13])

        # Уровневые значения
        t925_i = _at(t925, i); td925_i = _at(td925, i)
        t850_i = _at(t850, i); td850_i = _at(td850, i)
        t700_i = _at(t700, i); td700_i = _at(td700, i)
        t500_i = _at(t500, i); td500_i = _at(td500, i)
        t300_i = _at(t300, i); td300_i = _at(td300, i)

        w925_i = _at(w925, i); wd925_i = _at(wd925, i)
        w850_i = _at(w850, i); wd850_i = _at(wd850, i)
        w700_i = _at(w700, i); wd700_i = _at(wd700, i)
        w500_i = _at(w500, i); wd500_i = _at(wd500, i)
        w300_i = _at(w300, i); wd300_i = _at(wd300, i)

        h925_i = _at(h925, i)
        h850_i = _at(h850, i)
        h700_i = _at(h700, i)
        h500_i = _at(h500, i)
        h300_i = _at(h300, i)

        # Авиация
        av_thunder = combined_thunder_risk(
            t850_i, td850_i, t700_i, td700_i, t500_i, li_i, cape_i
        )
        av_fog = fog_forecast(t_c, dew2m_i, wind_i, cloud_i, hour_int, rh_i)

        result.append({
            "time": t,
            "precipitation_mm": p,
            "weather_code": c,
            "temp_c": t_c,
            "dew_point_c": dew2m_i,
            "wind_ms": wind_i,
            "wind_dir": _at(wdir, i),
            "humidity": rh_i,
            "pressure_hpa": pr,
            "theta_k": calculate_potential_temperature(t_c, pr),
            "cloud_cover": cloud_i,
            "wind_gust": _at(gust, i),
            "is_fog": c in (45, 48),
            "is_thunder": c in (95, 96, 99),
            "is_precip": p is not None and p > 0,
            "av_thunder": av_thunder,
            "av_fog": av_fog,

            # ==================================================
            # УРОВНИ — для синоптического анализа
            # ==================================================
            # Температура и точка росы
            "t925": t925_i, "td925": td925_i,
            "t850": t850_i, "td850": td850_i,
            "t700": t700_i, "td700": td700_i,
            "t500": t500_i, "td500": td500_i,
            "t300": t300_i, "td300": td300_i,

            # Ветер на уровнях (м/с)
            "wind925_ms": w925_i, "wind925_dir": wd925_i,
            "wind850_ms": w850_i, "wind850_dir": wd850_i,
            "wind700_ms": w700_i, "wind700_dir": wd700_i,
            "wind500_ms": w500_i, "wind500_dir": wd500_i,
            "wind300_ms": w300_i, "wind300_dir": wd300_i,

            # Геопотенциальная высота (м)
            "height925_m": h925_i,
            "height850_m": h850_i,
            "height700_m": h700_i,
            "height500_m": h500_i,
            "height300_m": h300_i,
        })
    return result


def build_sparkline(values, width=60, height=18, color=None):
    if not values or len(values) < 2: return ""
    clean = [(i, v) for i, v in enumerate(values) if v is not None]
    if len(clean) < 2: return ""
    xs = [i for i, _ in clean]
    ys = [v for _, v in clean]
    vmin, vmax = min(ys), max(ys)
    span = (vmax - vmin) or 1.0
    sx = lambda i: 1 + (width - 2) * (i - xs[0]) / max(xs[-1] - xs[0], 1)
    sy = lambda v: height - 1 - (height - 2) * (v - vmin) / span
    pts = " ".join(f"{sx(i):.1f},{sy(v):.1f}" for i, v in clean)
    c = color or "var(--accent)"
    return (f'<svg class="spark" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
            f'<polyline points="{pts}" fill="none" stroke="{c}" '
            f'stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>'
            f'</svg>')


def prepare_forecast_for_render(forecast):
    for h in forecast:
        h["css_class"] = code_to_class(h["weather_code"])
        h["code_text"] = code_to_text(h["weather_code"])
        h["wind_dir_text"] = wind_dir_text(h["wind_dir"])
        h["icon_svg"] = icon_for_code(h["weather_code"])

    by_day = OrderedDict()
    for h in forecast:
        by_day.setdefault(h["time"][:10], []).append(h)

    for day, rows in by_day.items():
        temp_spark = build_sparkline([r["temp_c"] for r in rows], color="var(--accent)")
        press_spark = build_sparkline([r["pressure_hpa"] for r in rows], color="#ffb547")
        for r in rows:
            r["temp_spark"] = temp_spark
            r["press_spark"] = press_spark

    return by_day