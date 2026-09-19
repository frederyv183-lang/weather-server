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
    prec  = hourly.get("precipitation", [])
    code  = hourly.get("weather_code", [])
    temp  = hourly.get("temperature_2m", [])
    wind  = hourly.get("wind_speed_10m", [])
    wdir  = hourly.get("wind_direction_10m", [])
    rh    = hourly.get("relative_humidity_2m", [])
    press = hourly.get("pressure_msl", [])
    cloud = hourly.get("cloud_cover", [])
    gust  = hourly.get("wind_gusts_10m", [])

    t500  = hourly.get("temperature_500hPa", [])
    t700  = hourly.get("temperature_700hPa", [])
    td700 = hourly.get("dew_point_700hPa", [])
    t850  = hourly.get("temperature_850hPa", [])
    td850 = hourly.get("dew_point_850hPa", [])
    cape_arr = hourly.get("cape", [])
    li_arr   = hourly.get("lifted_index", [])
    dew2m = hourly.get("dew_point_2m", [])

    result = []
    for i, t in enumerate(times):
        c = code[i] if i < len(code) else None
        p = prec[i] if i < len(prec) else 0
        t_c = temp[i] if i < len(temp) else None
        pr = press[i] if i < len(press) else None
        rh_i = rh[i] if i < len(rh) else None
        cloud_i = cloud[i] if i < len(cloud) else None
        wind_i = wind[i] if i < len(wind) else None
        dew2m_i = dew2m[i] if i < len(dew2m) else None

        t500_i = t500[i] if i < len(t500) else None
        t700_i = t700[i] if i < len(t700) else None
        td700_i = td700[i] if i < len(td700) else None
        t850_i = t850[i] if i < len(t850) else None
        td850_i = td850[i] if i < len(td850) else None
        cape_i = cape_arr[i] if i < len(cape_arr) else None
        li_i = li_arr[i] if i < len(li_arr) else None
        hour_int = int(t[11:13])

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
            "wind_dir": wdir[i] if i < len(wdir) else None,
            "humidity": rh_i,
            "pressure_hpa": pr,
            "theta_k": calculate_potential_temperature(t_c, pr),
            "cloud_cover": cloud_i,
            "wind_gust": gust[i] if i < len(gust) else None,
            "is_fog": c in (45, 48),
            "is_thunder": c in (95, 96, 99),
            "is_precip": p is not None and p > 0,
            "av_thunder": av_thunder,
            "av_fog": av_fog,
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