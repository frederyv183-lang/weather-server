# -*- coding: utf-8 -*-
"""
Расчёты климатических индексов и построение SVG-графиков.

Использует data/climate_indices.py как источник сырых данных.
Экспортирует:
  - analyze_climate()  -> единый dict со всеми индексами + SVG
  - build_enso_svg()   -> график ONI
  - build_ssw_svg()    -> график T на 10 гПа
  - build_pv_svg()     -> график геопотенциала 10 гПа
"""

import logging
import math
from statistics import mean

from data.climate_indices import (
    build_climate_report,
    classify_enso,
    pv_classify,
    pv_strength_index,
)


log = logging.getLogger("weather.climate")


# ============================================================
# УТИЛИТЫ
# ============================================================

def _fmt(v, dec=1):
    if v is None:
        return "—"
    return f"{v:.{dec}f}"


def _svg_header(width, height):
    return (
        f'<svg viewBox="0 0 {width} {height}" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'style="width:100%;height:auto;display:block;">'
    )


def _draw_axes(parts, pad_left, pad_top, plot_w, plot_h,
               vmin, vmax, x_labels, unit, decimals=1):
    """Рисует рамку + горизонтальные уровни + подписи по X."""
    parts.append(
        f'<rect x="{pad_left}" y="{pad_top}" '
        f'width="{plot_w}" height="{plot_h}" '
        f'fill="rgba(15,21,36,0.6)" stroke="rgba(120,160,255,0.15)" '
        f'stroke-width="0.5" rx="6"/>'
    )

    vspan = (vmax - vmin) or 1
    for i in range(6):
        yy = pad_top + plot_h * i / 5
        val = vmax - vspan * i / 5
        parts.append(
            f'<line x1="{pad_left}" y1="{yy:.2f}" '
            f'x2="{pad_left + plot_w}" y2="{yy:.2f}" '
            f'stroke="rgba(120,160,255,0.08)" stroke-width="0.5"/>'
        )
        parts.append(
            f'<text x="{pad_left - 10}" y="{yy + 5:.2f}" '
            f'text-anchor="end" fill="#a8b4d0" font-size="12" '
            f'font-family="JetBrains Mono, monospace">'
            f'{val:.{decimals}f}</text>'
        )

    n = len(x_labels)
    if n > 1:
        step = max(1, n // 12)
        for i in range(0, n, step):
            xx = pad_left + plot_w * i / (n - 1)
            parts.append(
                f'<line x1="{xx:.2f}" y1="{pad_top + plot_h}" '
                f'x2="{xx:.2f}" y2="{pad_top + plot_h + 5}" '
                f'stroke="rgba(120,160,255,0.3)" stroke-width="0.5"/>'
            )
            parts.append(
                f'<text x="{xx:.2f}" y="{pad_top + plot_h + 20}" '
                f'text-anchor="middle" fill="#a8b4d0" font-size="11" '
                f'font-family="JetBrains Mono, monospace">'
                f'{x_labels[i]}</text>'
            )

    parts.append(
        f'<text x="8" y="{pad_top - 4}" '
        f'fill="#6b7694" font-size="12" '
        f'font-family="Inter, sans-serif">{unit}</text>'
    )


def _draw_polyline(parts, values, x_fn, y_fn, color,
                   width=2, dash=None, opacity=1.0):
    pts = []
    for i, v in enumerate(values):
        if v is None:
            continue
        pts.append(f"{x_fn(i):.2f},{y_fn(v):.2f}")
    if not pts:
        return
    dash_attr = f'stroke-dasharray="{dash}"' if dash else ""
    parts.append(
        f'<polyline fill="none" stroke="{color}" '
        f'stroke-width="{width}" stroke-linejoin="round" '
        f'stroke-linecap="round" stroke-opacity="{opacity}" '
        f'{dash_attr} points="{" ".join(pts)}"/>'
    )


def _draw_zero_line(parts, pad_left, pad_top, plot_w, plot_h, vmin, vmax):
    """Рисует горизонтальную линию y=0."""
    if vmin <= 0 <= vmax:
        vspan = (vmax - vmin) or 1
        y0 = pad_top + plot_h * (vmax - 0) / vspan
        parts.append(
            f'<line x1="{pad_left}" y1="{y0:.2f}" '
            f'x2="{pad_left + plot_w}" y2="{y0:.2f}" '
            f'stroke="rgba(168,180,208,0.4)" stroke-width="1" '
            f'stroke-dasharray="3 3"/>'
        )


# ============================================================
# SVG — ENSO (ONI)
# ============================================================

def build_enso_svg(oni_series, width=1400, height=280):
    """
    График ONI (3-месячное скользящее SST-аномалии).
    Красные/синие полосы за порогами, чёрная линия значений.
    """
    if not oni_series:
        return '<div class="empty-note">Нет данных для графика ONI.</div>'

    values = [row.get("oni") for row in oni_series]
    valid = [v for v in values if v is not None]
    if not valid:
        return '<div class="empty-note">Нет значений ONI.</div>'

    vmin = min(min(valid), -2.0)
    vmax = max(max(valid), 2.0)
    vspan = (vmax - vmin) or 1

    pad_left = 70
    pad_right = 30
    pad_top = 20
    pad_bottom = 60
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    n = len(values)
    dx = plot_w / (n - 1) if n > 1 else plot_w

    def x(i):
        return pad_left + dx * i

    def y(v):
        return pad_top + plot_h * (vmax - v) / vspan

    x_labels = [f"{r.get('month', '?')}/{str(r.get('year', ''))[-2:]}"
                for r in oni_series]

    parts = [_svg_header(width, height)]
    _draw_axes(parts, pad_left, pad_top, plot_w, plot_h,
               vmin, vmax, x_labels, "ONI, °C", decimals=1)
    _draw_zero_line(parts, pad_left, pad_top, plot_w, plot_h, vmin, vmax)

    # Полосы El Niño / La Niña
    for i, v in enumerate(values):
        if v is None:
            continue
        if v >= 0.5:
            color = "rgba(255,84,112,0.25)"
        elif v <= -0.5:
            color = "rgba(77,171,255,0.25)"
        else:
            continue
        x0 = x(i) - dx * 0.4
        x1 = x(i) + dx * 0.4
        y0 = y(v)
        y_zero = y(0)
        parts.append(
            f'<rect x="{x0:.2f}" y="{min(y0, y_zero):.2f}" '
            f'width="{(x1 - x0):.2f}" height="{abs(y0 - y_zero):.2f}" '
            f'fill="{color}"/>'
        )

    _draw_polyline(parts, values, x, y, "#ff5470", width=2.2)

    parts.append('</svg>')
    return "".join(parts)


# ============================================================
# SVG — SSW (T на 10 гПа)
# ============================================================

def build_ssw_svg(t_series, width=1400, height=280):
    """График температуры 10 гПа в Арктике."""
    if not t_series:
        return '<div class="empty-note">Нет данных для графика T 10 гПа.</div>'

    by_day = {}
    for r in t_series:
        d = r["time"][:10]
        if r.get("t_c") is not None:
            by_day.setdefault(d, []).append(r["t_c"])

    days = sorted(by_day.keys())
    if not days:
        return '<div class="empty-note">Нет значений T 10 гПа.</div>'

    values = [round(mean(by_day[d]), 1) for d in days]

    vmin = min(values) - 5
    vmax = max(values) + 5
    vspan = (vmax - vmin) or 1

    pad_left = 70
    pad_right = 30
    pad_top = 20
    pad_bottom = 60
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    n = len(values)
    dx = plot_w / (n - 1) if n > 1 else plot_w

    def x(i):
        return pad_left + dx * i

    def y(v):
        return pad_top + plot_h * (vmax - v) / vspan

    x_labels = [d[5:] for d in days]

    parts = [_svg_header(width, height)]
    _draw_axes(parts, pad_left, pad_top, plot_w, plot_h,
               vmin, vmax, x_labels, "T 10 гПа, °C", decimals=1)

    avg_t = mean(values)
    y_avg = y(avg_t)
    parts.append(
        f'<line x1="{pad_left}" y1="{y_avg:.2f}" '
        f'x2="{pad_left + plot_w}" y2="{y_avg:.2f}" '
        f'stroke="rgba(255,181,71,0.5)" stroke-width="1" '
        f'stroke-dasharray="4 3"/>'
    )
    parts.append(
        f'<text x="{pad_left + 6}" y="{y_avg - 6:.2f}" '
        f'fill="#ffb547" font-size="11" '
        f'font-family="JetBrains Mono, monospace">'
        f'средняя: {_fmt(avg_t)} °C</text>'
    )

    _draw_polyline(parts, values, x, y, "#4dabff", width=2.0)

    parts.append('</svg>')
    return "".join(parts)


# ============================================================
# SVG — PV (геопотенциал 10 гПа)
# ============================================================

def build_pv_svg(pv_series, width=1400, height=280):
    """График геопотенциала 10 гПа в Арктике."""
    if not pv_series:
        return '<div class="empty-note">Нет данных для графика PV.</div>'

    by_day = {}
    for r in pv_series:
        d = r["time"][:10]
        if r.get("gph_m") is not None:
            by_day.setdefault(d, []).append(r["gph_m"])

    days = sorted(by_day.keys())
    if not days:
        return '<div class="empty-note">Нет значений PV.</div>'

    values = [round(mean(by_day[d])) for d in days]

    vmin = min(values) - 300
    vmax = max(values) + 300
    vspan = (vmax - vmin) or 1

    pad_left = 70
    pad_right = 30
    pad_top = 20
    pad_bottom = 60
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    n = len(values)
    dx = plot_w / (n - 1) if n > 1 else plot_w

    def x(i):
        return pad_left + dx * i

    def y(v):
        return pad_top + plot_h * (vmax - v) / vspan

    x_labels = [d[5:] for d in days]

    parts = [_svg_header(width, height)]
    _draw_axes(parts, pad_left, pad_top, plot_w, plot_h,
               vmin, vmax, x_labels, "H 10 гПа, м", decimals=0)

    if vmin <= 31000 <= vmax:
        y_ssw = y(31000)
        parts.append(
            f'<line x1="{pad_left}" y1="{y_ssw:.2f}" '
            f'x2="{pad_left + plot_w}" y2="{y_ssw:.2f}" '
            f'stroke="rgba(255,84,112,0.4)" stroke-width="1" '
            f'stroke-dasharray="4 3"/>'
        )
        parts.append(
            f'<text x="{pad_left + 6}" y="{y_ssw - 6:.2f}" '
            f'fill="#ff5470" font-size="11" '
            f'font-family="JetBrains Mono, monospace">'
            f'порог SSW: 31000 м</text>'
        )

    _draw_polyline(parts, values, x, y, "#a78bfa", width=2.0)

    parts.append('</svg>')
    return "".join(parts)


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def analyze_climate(days_back=365):
    """
    Собирает всё: индексы + SVG + текстовые summary.
    """
    report = build_climate_report(days_back=days_back)

    result = {
        "period": report.get("period"),
        "enso": None,
        "ssw": None,
        "pv": None,
        "error": report.get("error"),
    }

    # ---------- ENSO ----------
    enso_raw = report.get("enso") or {}
    if enso_raw.get("error"):
        result["enso"] = {"error": enso_raw["error"]}
    else:
        oni_series = enso_raw.get("recent") or []
        current_oni = enso_raw.get("current_oni")
        classification = enso_raw.get("classification", "нет данных")
        svg = build_enso_svg(oni_series)

        if current_oni is None:
            summary = "Недостаточно данных для расчёта ONI."
        else:
            summary = (
                f"Текущий ONI: {current_oni:+.2f} °C. "
                f"Классификация: {classification}."
            )

        result["enso"] = {
            "current_oni": current_oni,
            "classification": classification,
            "svg": svg,
            "summary_text": summary,
            "recent": oni_series,
        }

    # ---------- SSW ----------
    ssw_raw = report.get("ssw") or {}
    if ssw_raw.get("error"):
        result["ssw"] = {"error": ssw_raw["error"]}
    else:
        events = ssw_raw.get("events") or []
        t_series = ssw_raw.get("recent_t") or []
        svg = build_ssw_svg(t_series)

        n = len(events)
        if n == 0:
            summary = (
                "За выбранный период событий SSW не обнаружено. "
                "Стратосфера стабильна."
            )
        else:
            last = events[-1]
            summary = (
                f"Обнаружено событий SSW: {n}. "
                f"Последнее: {last['date']} — {last['description']}."
            )

        result["ssw"] = {
            "n_events": n,
            "events": events,
            "svg": svg,
            "summary_text": summary,
        }

    # ---------- PV ----------
    pv_raw = report.get("pv") or {}
    if pv_raw.get("error"):
        result["pv"] = {"error": pv_raw["error"]}
    else:
        gph_mean = pv_raw.get("gph_mean")
        classification = pv_raw.get("classification", "нет данных")
        series = pv_raw.get("recent") or []
        svg = build_pv_svg(series)

        if gph_mean is None:
            summary = "Недостаточно данных для расчёта PV."
        else:
            summary = (
                f"Средний геопотенциал 10 гПа: {gph_mean:.0f} м. "
                f"Состояние полярного вихря: {classification}."
            )

        result["pv"] = {
            "gph_mean": gph_mean,
            "classification": classification,
            "svg": svg,
            "summary_text": summary,
        }

    return result