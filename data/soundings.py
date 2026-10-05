# -*- coding: utf-8 -*-
"""Зондирование атмосферы: Wyoming + MetPy. Рендер Skew-T в SVG (v3)."""

import io
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import metpy.calc as mpcalc
from metpy.plots import SkewT
from metpy.units import units, pandas_dataframe_to_unit_arrays

from siphon.simplewebservice.wyoming import WyomingUpperAir


# v3: SVG + tooltip
# На этих уровнях давления tooltip будет активен (иначе — «шум»)
TOOLTIP_LEVELS = {1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100}


# FALLBACK v2 (много сроков)
def fetch_sounding(station, ts=None):
    """
    Получить данные зондирования Wyoming.

    Если ts не задан — перебираем последние сроки (0Z и 12Z)
    до 5 дней назад, пока не найдём доступные данные.
    Это нужно потому, что Wyoming часто отдаёт данные с задержкой
    1–3 дня, а для некоторых станций — до 5.

    Args:
        station: код станции (например, 'ALB', '27730')
        ts: конкретное время UTC. Если None — автопоиск.

    Returns:
        pandas.DataFrame или None
    """
    station = station.upper()

    # Список кандидатов времени: если ts задан — только он;
    # если нет — 0Z и 12Z за последние 5 дней, от свежих к старым.
    if ts is not None:
        candidates = [ts]
    else:
        now = datetime.utcnow()
        candidates = []
        for days_ago in range(0, 6):
            day = (now - timedelta(days=days_ago)).replace(
                minute=0, second=0, microsecond=0)
            for hour in (12, 0):
                cand = day.replace(hour=hour)
                if cand > now:
                    continue
                candidates.append(cand)

    last_error = None
    for cand in candidates:
        try:
            df = WyomingUpperAir.request_data(cand, station)
            if df is not None and not df.empty:
                print("[soundings] %s: got %s (%d rows)"
                      % (station, cand, len(df)))
                return df
        except Exception as e:
            last_error = e
            continue

    if last_error:
        print("[soundings] %s: no data, last error: %s" % (station, last_error))
    else:
        print("[soundings] %s: no data in last 5 days" % station)
    return None


def render_skewt_svg(df, station=None, ts=None):
    """
    Рисует Skew-T и возвращает (svg_str, points).
    Координаты hotspot-точек вычисляются через ax.transData — точно.
    """
    sounding = pandas_dataframe_to_unit_arrays(df)

    p  = sounding["pressure"]
    T  = sounding["temperature"]
    Td = sounding["dewpoint"]
    ws = sounding["speed"]
    wd = sounding["direction"]
    h  = sounding.get("height")

    rh = mpcalc.relative_humidity_from_dewpoint(T, Td).to("percent")
    theta = mpcalc.potential_temperature(p, T).to("kelvin")
    mixr = mpcalc.mixing_ratio_from_relative_humidity(p, T, rh).to("g/kg")

    u, v = mpcalc.wind_components(ws, wd)
    ws_ms = ws.to("m/s")
    ws_kts = ws.to("knots")

    def wind_text(i):
        try:
            return "%d\u00b0 %.1f \u043c/\u0441 (%.0f \u0443\u0437)" % (
                float(wd[i].m), float(ws_ms[i].m), float(ws_kts[i].m)
            )
        except Exception:
            return "\u2014"

    fig = plt.figure(figsize=(11, 11))
    skew = SkewT(fig, rotation=45)

    skew.plot(p, T,  "r", linewidth=2.0,
              label="\u0422\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430")
    skew.plot(p, Td, "g", linewidth=2.0,
              label="\u0422\u043e\u0447\u043a\u0430 \u0440\u043e\u0441\u044b")

    step = max(1, len(p) // 12)
    skew.plot_barbs(p[::step], u[::step], v[::step], length=6, linewidth=0.8)

    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlim(-40, 40)
    skew.ax.set_xlabel("\u0422\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430, \u00b0C", fontsize=11)
    skew.ax.set_ylabel("\u0414\u0430\u0432\u043b\u0435\u043d\u0438\u0435, \u0433\u041f\u0430", fontsize=11)
    skew.ax.tick_params(labelsize=10)
    skew.ax.grid(True, linewidth=0.4, alpha=0.4)

    lcl_p, lcl_t = mpcalc.lcl(p[0], T[0], Td[0])
    skew.plot(lcl_p, lcl_t, "ko", markerfacecolor="black", markersize=6,
              label="\u0423\u0440\u043e\u0432\u0435\u043d\u044c \u043a\u043e\u043d\u0434\u0435\u043d\u0441\u0430\u0446\u0438\u0438 (LCL)")

    prof = mpcalc.parcel_profile(p, T[0], Td[0]).to("degC")
    skew.plot(p, prof, "k", linewidth=2.0,
              label="\u041f\u0443\u0442\u044c \u0447\u0430\u0441\u0442\u0438\u0446\u044b")

    skew.shade_cape(p, T, prof, alpha=0.15, label="CAPE")
    skew.shade_cin(p, T, prof, Td, alpha=0.15, label="CIN")

    skew.plot_dry_adiabats(alpha=0.25, linewidth=0.6)
    skew.plot_moist_adiabats(alpha=0.25, linewidth=0.6)
    skew.plot_mixing_lines(alpha=0.25, linewidth=0.6)

    title = "Skew-T"
    if station:
        title += " \u2014 " + station.upper()
    if ts is not None:
        title += " \u2014 " + ts.strftime("%Y-%m-%d %HZ")
    skew.ax.set_title(title, fontsize=13, pad=12)
    skew.ax.legend(loc="upper right", fontsize=9, framealpha=0.9)

    # --- Важно: canvas.draw ДО transData и ДО savefig ---
    fig.canvas.draw()

    # Собираем точки
    points = []
    try:
        bbox = skew.ax.get_window_extent()
        x0, y0 = bbox.x0, bbox.y0
        w, h_px = bbox.width, bbox.height

        for i in range(len(p)):
            try:
                p_hpa = round(float(p[i].m))
            except Exception:
                continue
            if p_hpa not in TOOLTIP_LEVELS:
                continue

            try:
                T_val = float(T[i].m)
                p_val = float(p[i].m)
                x_px, y_px = skew.ax.transData.transform((T_val, p_val))
                x_pct = (x_px - x0) / w * 100
                # Y инвертируем: у CSS 0% — верх, 100% — низ
                y_pct = (y0 + h_px - y_px) / h_px * 100

                points.append({
                    "p": int(p_hpa),
                    "h": int(h[i].m) if h is not None else None,
                    "T": round(float(T[i].m), 1),
                    "Td": round(float(Td[i].m), 1),
                    "RH": round(float(rh[i].m), 1),
                    "theta": round(float(theta[i].m), 1),
                    "mixr": round(float(mixr[i].m), 2),
                    "wind": wind_text(i),
                    "x_pct": round(x_pct, 2),
                    "y_pct": round(y_pct, 2),
                })
            except Exception as e:
                print("[soundings] point %d: %s" % (i, e))

    except Exception as e:
        print("[soundings] transData error: %s" % e)

    # --- SVG ---
    buf = io.BytesIO()
    plt.savefig(buf, format="svg", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    svg_str = buf.read().decode("utf-8")

    return svg_str, points


