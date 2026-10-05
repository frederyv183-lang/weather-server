# -*- coding: utf-8 -*-
"""Зондирование атмосферы: данные Wyoming + рендер Skew-T через MetPy."""

import io
import base64
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import metpy.calc as mpcalc
from metpy.plots import SkewT
from metpy.units import pandas_dataframe_to_unit_arrays

from siphon.simplewebservice.wyoming import WyomingUpperAir


def fetch_sounding(station, ts=None):
    """
    Получить данные зондирования для станции Wyoming.

    Args:
        station: код станции (например, 'ALB', 'BUF', 'OUN')
        ts: время UTC (по умолчанию последний срок 00Z/12Z)

    Returns:
        pandas.DataFrame или None при ошибке
    """
    if ts is None:
        now = datetime.utcnow()
        if now.hour > 13:
            ts = now.replace(hour=12, minute=0, second=0, microsecond=0)
        elif now.hour > 1:
            ts = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            ts = (now - timedelta(days=1)).replace(
                hour=12, minute=0, second=0, microsecond=0
            )

    try:
        df = WyomingUpperAir.request_data(ts, station.upper())
        if df is None or df.empty:
            return None
        return df
    except Exception as e:
        print("[soundings] %s: %s" % (station, e))
        return None


def render_skewt(df):
    """
    Нарисовать Skew-T, вернуть PNG в base64 (без префикса data:image).
    """
    sounding = pandas_dataframe_to_unit_arrays(df)

    p  = sounding["pressure"]
    T  = sounding["temperature"]
    Td = sounding["dewpoint"]
    ws = sounding["speed"]
    wd = sounding["direction"]

    u, v = mpcalc.wind_components(ws, wd)

    fig = plt.figure(figsize=(9, 9))
    skew = SkewT(fig, rotation=45)

    skew.plot(p, T,  "r", linewidth=2)
    skew.plot(p, Td, "g", linewidth=2)
    skew.plot_barbs(p, u, v)

    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlim(-40, 40)

    lcl_p, lcl_t = mpcalc.lcl(p[0], T[0], Td[0])
    skew.plot(lcl_p, lcl_t, "ko", markerfacecolor="black")

    prof = mpcalc.parcel_profile(p, T[0], Td[0]).to("degC")
    skew.plot(p, prof, "k", linewidth=2)

    skew.shade_cape(p, T, prof, alpha=0.2)
    skew.shade_cin(p, T, prof, Td, alpha=0.2)

    skew.plot_dry_adiabats(alpha=0.3)
    skew.plot_moist_adiabats(alpha=0.3)
    skew.plot_mixing_lines(alpha=0.3)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
