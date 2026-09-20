# -*- coding: utf-8 -*-
"""
Синоптический анализ по изобарическим уровням.

Уровни: 925, 850, 700, 500, 300 гПа.
Для каждого часа:
  - профиль T, Td, θ, RH, ветра, геопотенциала;
  - высоты уровней (из Open-Meteo, fallback — ISA);
  - LCL (уровень конденсации);
  - тропопауза (высота + тип: polar/tropical);
  - фронтальные зоны (градиент θ + разворот ветра);
  - струйное течение (макс. ветер на 300 гПа);
  - адвекция температуры (по ветру и ΔT);
  - индексы неустойчивости (LI, K-Index, ΔT850-500);
  - сдвиг ветра 850→300 гПа.
"""

import math
import json
from datetime import datetime

from core.utils import calculate_potential_temperature, wind_dir_text


# ============================================================
# УРОВНИ
# ============================================================
SYNOPTIC_LEVELS = [925, 850, 700, 500, 300]

LEVEL_NAMES = {
    925: "925 гПа (~750 м)",
    850: "850 гПа (~1500 м)",
    700: "700 гПа (~3000 м)",
    500: "500 гПа (~5500 м)",
    300: "300 гПа (~9000 м)",
}

TROPOPAUSE_TYPICAL = {
    "winter": 300,
    "spring": 300,
    "summer": 250,
    "autumn": 300,
}

# Физические константы
_G = 9.80665          # м/с²
_R = 287.05           # Дж/(кг·К)
_P0 = 1013.25         # гПа
_CP = 1004.0          # Дж/(кг·К)


# ============================================================
# ФИЗИЧЕСКИЕ РАСЧЁТЫ
# ============================================================
def pressure_to_height(p_hPa):
    """Приблизительная высота изобарической поверхности по ISA."""
    if p_hPa is None or p_hPa <= 0:
        return None
    return round(44330.0 * (1.0 - (p_hPa / _P0) ** 0.1903), 1)


def geopotential_height(t_c, p_hPa, p0=1000.0):
    """Толщина слоя между p0 и p_hPa по средней температуре."""
    if t_c is None or p_hPa is None or p_hPa <= 0:
        return None
    t_k = t_c + 273.15
    return round(_R * t_k / _G * math.log(p0 / p_hPa), 1)


def saturation_vapor_pressure(t_c):
    """Давление насыщенного пара (Магнус), гПа."""
    if t_c is None:
        return None
    return 6.112 * math.exp(17.67 * t_c / (t_c + 243.5))


def relative_humidity(t_c, td_c):
    """RH, %."""
    if t_c is None or td_c is None:
        return None
    e = saturation_vapor_pressure(td_c)
    es = saturation_vapor_pressure(t_c)
    if not es:
        return None
    return round(max(0.0, min(100.0, 100.0 * e / es)), 1)


def mixing_ratio(t_c, td_c, p_hPa):
    """Отношение смеси, г/кг."""
    if t_c is None or td_c is None or p_hPa is None:
        return None
    e = saturation_vapor_pressure(td_c)
    if e is None or p_hPa <= e:
        return None
    return round(622.0 * e / (p_hPa - e), 2)


def lcl_height(t2m, td2m):
    """Высота уровня конденсации (LCL), м."""
    if t2m is None or td2m is None:
        return None
    return round(max(0.0, 125.0 * (t2m - td2m)), 1)


def lifted_index(t850, td850, t500):
    """Упрощённый LI."""
    if t850 is None or td850 is None or t500 is None:
        return None
    lcl = lcl_height(t850, td850)
    if lcl is None:
        return None
    dz1 = lcl / 1000.0
    dz2 = max(0.0, (5500.0 - lcl) / 1000.0)
    t_particle = t850 - 9.8 * dz1 - 6.0 * dz2
    return round(t500 - t_particle, 1)


def k_index(t850, td850, t700, td700, t500):
    """K-Index."""
    if None in (t850, td850, t700, td700, t500):
        return None
    return round((t850 - t500) + td850 - (t700 - td700), 1)


def wind_shear(levels, lvl_low=850, lvl_high=300):
    """Векторный сдвиг ветра между двумя уровнями."""
    lo = levels.get(lvl_low, {})
    hi = levels.get(lvl_high, {})
    if lo.get("wind_ms") is None or hi.get("wind_ms") is None:
        return None
    if lo.get("wind_dir") is None or hi.get("wind_dir") is None:
        return None

    def to_uv(speed, direction_deg):
        rad = math.radians(direction_deg)
        return -speed * math.sin(rad), -speed * math.cos(rad)

    u_lo, v_lo = to_uv(lo["wind_ms"], lo["wind_dir"])
    u_hi, v_hi = to_uv(hi["wind_ms"], hi["wind_dir"])
    du = u_hi - u_lo
    dv = v_hi - v_lo
    speed = math.hypot(du, dv)
    direction = (math.degrees(math.atan2(-du, -dv)) + 360) % 360
    return round(speed, 1), round(direction, 1)


def temperature_advection(t_prev, t_next, wind_dir, wind_ms):
    """Грубая оценка адвекции температуры."""
    if t_prev is None or t_next is None or wind_dir is None:
        return None
    dt = t_next - t_prev
    if abs(dt) < 0.5:
        return None
    if 315 <= wind_dir or wind_dir <= 45:
        return "cold"
    if 135 <= wind_dir <= 225:
        return "warm"
    return None


def classify_front(t_850, t_700, wind_dir_850, wind_dir_700):
    """Классификация фронта."""
    if None in (t_850, t_700, wind_dir_850, wind_dir_700):
        return None
    dt = t_700 - t_850
    diff = (wind_dir_700 - wind_dir_850 + 360) % 360
    veer = "clockwise" if diff < 180 else "counterclockwise"
    if dt > 5 and veer == "clockwise":
        return "warm"
    if dt < -5 and veer == "counterclockwise":
        return "cold"
    if abs(dt) < 3 and veer == "clockwise":
        return "occluded"
    return None


def sanitize_levels(levels):
    """Убирает физически невозможные значения."""
    for lvl, d in levels.items():
        t = d.get("t")
        td = d.get("td")
        w = d.get("wind_ms")
        if t is not None and (t < -90 or t > 60):
            d["t"] = None
        if td is not None and (td < -100 or td > 40):
            d["td"] = None
        if w is not None and (w < 0 or w > 150):
            d["wind_ms"] = None
    return levels


def detect_tropopause(levels):
    """Возвращает (hPa, type) или (None, None)."""
    order = [925, 850, 700, 500, 300]
    for lvl in order:
        t = levels.get(lvl, {}).get("t")
        if t is None:
            continue
        if t < -70:
            return lvl, "tropical"
        if t < -55:
            return lvl, "polar"
    return None, None


# ============================================================
# ИЗВЛЕЧЕНИЕ ДАННЫХ ПО УРОВНЯМ
# ============================================================
def extract_levels(forecast):
    """Из списка часов вытаскивает данные по уровням."""
    result = []
    for h in forecast:
        t2m = h.get("temp_c")
        td2m = h.get("dew_point_c")

        levels = {}

        t925 = h.get("t925")
        td925 = h.get("td925")
        if t925 is None:
            t925 = t2m
        if td925 is None:
            td925 = td2m

        levels[925] = {
            "t": t925,
            "td": td925,
            "theta": calculate_potential_temperature(t925, 925),
            "rh": relative_humidity(t925, td925),
            "mr": mixing_ratio(t925, td925, 925),
            "wind_ms": h.get("wind925_ms"),
            "wind_dir": h.get("wind925_dir"),
            "height_m": h.get("height925_m") or pressure_to_height(925),
            "geopot_h_m": 0.0,
            "lcl_m": lcl_height(t2m, td2m),
        }

        for lvl, (t_key, td_key, w_key, wd_key, h_key) in {
            850: ("t850", "td850", "wind850_ms", "wind850_dir", "height850_m"),
            700: ("t700", "td700", "wind700_ms", "wind700_dir", "height700_m"),
            500: ("t500", "td500", "wind500_ms", "wind500_dir", "height500_m"),
            300: ("t300", "td300", "wind300_ms", "wind300_dir", "height300_m"),
        }.items():
            t = h.get(t_key)
            td = h.get(td_key)
            height = h.get(h_key)
            if height is None:
                height = pressure_to_height(lvl)
            levels[lvl] = {
                "t": t,
                "td": td,
                "theta": calculate_potential_temperature(t, lvl),
                "rh": relative_humidity(t, td),
                "mr": mixing_ratio(t, td, lvl),
                "wind_ms": h.get(w_key),
                "wind_dir": h.get(wd_key),
                "height_m": height,
                "geopot_h_m": geopotential_height(t, lvl),
                "lcl_m": None,
            }

        levels = sanitize_levels(levels)

        tropopause_hPa, tropopause_type = detect_tropopause(levels)

        jet = None
        w300 = levels[300]["wind_ms"]
        if w300 is not None and w300 > 30:
            jet = {
                "level": 300,
                "speed": round(w300, 1),
                "dir": levels[300]["wind_dir"],
                "text": wind_dir_text(levels[300]["wind_dir"]),
            }

        frontal_zone = False
        front_type = None
        if levels[850]["theta"] is not None and levels[700]["theta"] is not None:
            d_theta = abs(levels[850]["theta"] - levels[700]["theta"])
            if d_theta > 15:
                frontal_zone = True
                front_type = classify_front(
                    levels[850]["t"], levels[700]["t"],
                    levels[850]["wind_dir"], levels[700]["wind_dir"],
                )

        indices = {
            "li": lifted_index(levels[850]["t"], levels[850]["td"], levels[500]["t"]),
            "k_index": k_index(
                levels[850]["t"], levels[850]["td"],
                levels[700]["t"], levels[700]["td"],
                levels[500]["t"],
            ),
            "dt_850_500": (
                round(levels[850]["t"] - levels[500]["t"], 1)
                if levels[850]["t"] is not None and levels[500]["t"] is not None
                else None
            ),
        }

        shear = wind_shear(levels, 850, 300)

        result.append({
            "time": h["time"],
            "temp_c": t2m,
            "dew_point_c": td2m,
            "wind_ms": h.get("wind_ms"),
            "wind_dir": h.get("wind_dir"),
            "levels": levels,
            "tropopause_hPa": tropopause_hPa,
            "tropopause_type": tropopause_type,
            "jet": jet,
            "frontal_zone": frontal_zone,
            "front_type": front_type,
            "indices": indices,
            "shear": shear,
        })

    for i in range(1, len(result)):
        prev = result[i - 1]["levels"][850]
        cur = result[i]["levels"][850]
        result[i]["advection"] = temperature_advection(
            prev["t"], cur["t"], cur["wind_dir"], cur["wind_ms"],
        )
    if result:
        result[0]["advection"] = None

    return result


# ============================================================
# ТЕКСТОВЫЙ АНАЛИЗ
# ============================================================
def generate_synoptic_text(station_name, model_name, hours, hour_index=None):
    """
    Текстовый синоптический разбор.

    Если hour_index задан — разбор только для этого часа (вариант А).
    Если hour_index=None — сводка по дням.
    """
    if not hours:
        return "Нет данных для синоптического анализа."

    if hour_index is not None and 0 <= hour_index < len(hours):
        return _synoptic_text_for_hour(station_name, model_name, hours[hour_index])

    from collections import Counter

    lines = [
        f"Синоптический анализ для {station_name}.",
        f"Модель: {model_name}.",
        "",
    ]

    by_day = {}
    for h in hours:
        by_day.setdefault(h["time"][:10], []).append(h)

    for day, day_hours in by_day.items():
        try:
            day_str = datetime.strptime(day, "%Y-%m-%d").strftime("%d.%m.%Y")
        except Exception:
            day_str = day

        lines.append(f"◆ {day_str}")

        t850 = [h["levels"][850]["t"] for h in day_hours
                if h["levels"][850]["t"] is not None]
        t500 = [h["levels"][500]["t"] for h in day_hours
                if h["levels"][500]["t"] is not None]
        winds300 = [h["levels"][300]["wind_ms"] for h in day_hours
                    if h["levels"][300]["wind_ms"] is not None]
        jets = [h for h in day_hours if h["jet"]]
        fronts = [h for h in day_hours if h["frontal_zone"]]
        tropopauses = [h["tropopause_hPa"] for h in day_hours
                       if h["tropopause_hPa"]]

        if t850 and t500:
            avg850 = sum(t850) / len(t850)
            avg500 = sum(t500) / len(t500)
            lines.append(
                f"  Температура: T850 ≈ {avg850:.1f} °C, "
                f"T500 ≈ {avg500:.1f} °C."
            )

        if tropopauses:
            most_common = max(set(tropopauses), key=tropopauses.count)
            types = [h["tropopause_type"] for h in day_hours
                     if h.get("tropopause_type")]
            type_str = ""
            if types:
                c = Counter(types).most_common(1)[0][0]
                tname = {"polar": "полярная", "tropical": "тропическая"}
                type_str = f" ({tname.get(c, c)})"
            lines.append(f"  Тропопауза: преимущественно {most_common} гПа{type_str}.")

        if fronts:
            lines.append(f"  ⚠️ Фронтальные зоны: {len(fronts)} ч из {len(day_hours)}.")
            types = [f["front_type"] for f in fronts if f.get("front_type")]
            if types:
                c = Counter(types)
                names = {"warm": "тёплый", "cold": "холодный", "occluded": "окклюзия"}
                summary = ", ".join(f"{names.get(k, k)}×{v}" for k, v in c.items())
                lines.append(f"     Типы: {summary}.")

        if jets:
            max_jet = max(jets, key=lambda x: x["jet"]["speed"])
            lines.append(
                f"  💨 Струйное течение: {max_jet['jet']['speed']} м/с "
                f"на 300 гПа ({max_jet['jet']['dir']}°)."
            )

        if winds300:
            avg_w = sum(winds300) / len(winds300)
            lines.append(f"  Ветер на 300 гПа: в среднем {avg_w:.1f} м/с.")

        li_vals = [h["indices"]["li"] for h in day_hours
                   if h["indices"].get("li") is not None]
        k_vals = [h["indices"]["k_index"] for h in day_hours
                  if h["indices"].get("k_index") is not None]
        if li_vals:
            li_min = min(li_vals)
            mark = "⚠️" if li_min < -2 else "✓"
            lines.append(f"  {mark} LI min: {li_min:+.1f}")
        if k_vals:
            k_max = max(k_vals)
            mark = "⚠️" if k_max > 30 else "✓"
            lines.append(f"  {mark} K-Index max: {k_max:.1f}")

        shears = [h["shear"] for h in day_hours if h.get("shear")]
        if shears:
            max_shear = max(shears, key=lambda x: x[0])
            lines.append(f"  Сдвиг 850→300 гПа: до {max_shear[0]:.1f} м/с.")

        lcls = [h["levels"][925]["lcl_m"] for h in day_hours
                if h["levels"][925].get("lcl_m") is not None]
        if lcls:
            avg_lcl = sum(lcls) / len(lcls)
            lines.append(f"  LCL: в среднем {avg_lcl:.0f} м.")

        lines.append("")

    lines.append(
        f"Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')} (мск)."
    )
    return "\n".join(lines)


def _synoptic_text_for_hour(station_name, model_name, h):
    """Разбор для одного часа (вариант А)."""
    lv = h["levels"]
    t850 = lv[850]["t"]
    t500 = lv[500]["t"]
    t925 = lv[925]["t"]
    td925 = lv[925]["td"]
    theta850 = lv[850]["theta"]
    theta700 = lv[700]["theta"]

    try:
        t_str = datetime.strptime(h["time"], "%Y-%m-%dT%H:%M").strftime("%d.%m.%Y %H:%M")
    except Exception:
        t_str = h["time"]

    lines = [
        f"Синоптический анализ для {station_name}.",
        f"Модель: {model_name}.",
        f"Время: {t_str} (мск).",
        "",
    ]

    if h.get("temp_c") is not None:
        if h.get("dew_point_c") is not None:
            lines.append(
                f"  У земли: T = {h['temp_c']:.1f} °C, "
                f"Td = {h['dew_point_c']:.1f} °C."
            )
        else:
            lines.append(f"  У земли: T = {h['temp_c']:.1f} °C.")

    if t925 is not None:
        lines.append(f"  925 гПа: T = {t925:.1f} °C.")
    if t850 is not None:
        lines.append(f"  850 гПа: T = {t850:.1f} °C.")
    if t500 is not None:
        lines.append(f"  500 гПа: T = {t500:.1f} °C.")

    if theta850 is not None and theta700 is not None:
        d_theta = theta850 - theta700
        lines.append(
            f"  θ850 = {theta850:.1f} K, θ700 = {theta700:.1f} K "
            f"(Δθ = {d_theta:+.1f} K)."
        )

    if h.get("tropopause_hPa"):
        tname = {"polar": "полярная", "tropical": "тропическая"}
        tt = tname.get(h.get("tropopause_type"), h.get("tropopause_type") or "")
        lines.append(
            f"  🌀 Тропопауза: {h['tropopause_hPa']} гПа"
            f"{(' (' + tt + ')') if tt else ''}."
        )

    if h.get("jet"):
        j = h["jet"]
        lines.append(
            f"  💨 Струйное течение: {j['speed']} м/с "
            f"на {j['level']} гПа ({j['dir']}°, {j.get('text', '')})."
        )
    else:
        w300 = lv[300]["wind_ms"]
        if w300 is not None:
            lines.append(f"  💨 Струя: нет (ветер на 300 гПа = {w300:.1f} м/с).")
        else:
            lines.append("  💨 Струя: нет данных на 300 гПа.")

    if h.get("frontal_zone"):
        ftype = {"warm": "тёплый", "cold": "холодный",
                 "occluded": "окклюзия"}.get(h.get("front_type"), "")
        lines.append(f"  ⚠️ Фронтальная зона{(' (' + ftype + ')') if ftype else ''}.")
    else:
        lines.append("  ✓ Фронтальная зона не обнаружена.")

    w300 = lv[300]["wind_ms"]
    if w300 is not None:
        lines.append(f"  Ветер на 300 гПа: {w300:.1f} м/с.")

    idx = h.get("indices", {})
    if idx.get("li") is not None:
        mark = "⚠️" if idx["li"] < -2 else "✓"
        lines.append(f"  {mark} LI: {idx['li']:+.1f}")
    if idx.get("k_index") is not None:
        mark = "⚠️" if idx["k_index"] > 30 else "✓"
        lines.append(f"  {mark} K-Index: {idx['k_index']:.1f}")
    if idx.get("dt_850_500") is not None:
        lines.append(f"  ΔT (850−500): {idx['dt_850_500']:.1f} °C.")

    if h.get("shear"):
        lines.append(
            f"  Сдвиг 850→300 гПа: {h['shear'][0]:.1f} м/с "
            f"({h['shear'][1]:.0f}°)."
        )

    if h.get("advection") == "warm":
        lines.append("  Адвекция на 850 гПа: тёплая.")
    elif h.get("advection") == "cold":
        lines.append("  Адвекция на 850 гПа: холодная.")

    if lv[925].get("lcl_m") is not None:
        lines.append(f"  LCL: {lv[925]['lcl_m']:.0f} м.")

    lines.append("")
    lines.append(
        f"Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')} (мск)."
    )
    return "\n".join(lines)


# ============================================================
# SVG-ПРОФИЛЬ (интерактивный)
# ============================================================
def build_profile_svg(hours, hour_index=12, width=600, height=400):
    """
    SVG-профиль T и θ по уровням для одного часа.
    Ось Y — давление (логарифмическая).
    Точки интерактивны: при наведении показывают tooltip.
    """
    if not hours or hour_index >= len(hours):
        return '<div class="empty-note">Нет данных для профиля.</div>'

    h = hours[hour_index]
    levels = h["levels"]
    time_str = h["time"][11:16]

    data = []
    for lvl in SYNOPTIC_LEVELS:
        d = levels.get(lvl, {})
        if d.get("t") is not None:
            data.append((lvl, d["t"], d.get("theta"), d))

    if len(data) < 2:
        return '<div class="empty-note">Недостаточно данных для профиля.</div>'

    temps = [d[1] for d in data]
    tmin = min(temps) - 5
    tmax = max(temps) + 5
    tspan = (tmax - tmin) or 1

    thetas = [d[2] for d in data if d[2] is not None]
    if thetas:
        thmin = min(thetas) - 5
        thmax = max(thetas) + 5
        thspan = (thmax - thmin) or 1
    else:
        thmin = thmax = 0
        thspan = 1

    def y_pos(p):
        p_min, p_max = 300, 925
        log_p = math.log(p)
        log_min = math.log(p_min)
        log_max = math.log(p_max)
        return 40 + (height - 80) * (log_p - log_min) / (log_max - log_min)

    pad_left = 70
    pad_right = 30
    plot_w = width - pad_left - pad_right

    def x_t(t):
        return pad_left + plot_w * (t - tmin) / tspan

    def x_theta(th):
        return pad_left + plot_w * (th - thmin) / thspan

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'style="width:100%;height:auto;display:block;">'
    )

    parts.append(
        f'<rect x="{pad_left}" y="40" '
        f'width="{plot_w}" height="{height - 80}" '
        f'fill="rgba(15,21,36,0.6)" stroke="rgba(120,160,255,0.15)" '
        f'stroke-width="0.5" rx="6"/>'
    )

    for lvl in SYNOPTIC_LEVELS:
        if not any(d[0] == lvl for d in data):
            continue
        y = y_pos(lvl)
        parts.append(
            f'<line x1="{pad_left}" y1="{y:.2f}" '
            f'x2="{pad_left + plot_w}" y2="{y:.2f}" '
            f'stroke="rgba(120,160,255,0.1)" stroke-width="0.5"/>'
        )
        parts.append(
            f'<text x="{pad_left - 8}" y="{y + 4:.2f}" '
            f'text-anchor="end" fill="#a8b4d0" font-size="12" '
            f'font-family="JetBrains Mono, monospace">{lvl}</text>'
        )

    for i in range(5):
        x = pad_left + plot_w * i / 4
        t_val = tmin + tspan * i / 4
        parts.append(
            f'<line x1="{x:.2f}" y1="40" '
            f'x2="{x:.2f}" y2="{height - 40}" '
            f'stroke="rgba(120,160,255,0.06)" stroke-width="0.5"/>'
        )
        parts.append(
            f'<text x="{x:.2f}" y="{height - 20}" '
            f'text-anchor="middle" fill="#a8b4d0" font-size="11" '
            f'font-family="JetBrains Mono, monospace">{t_val:.0f}</text>'
        )

    def _attrs(lvl, d):
        t = d.get("t")
        th = d.get("theta")
        ws = d.get("wind_ms")
        wd = d.get("wind_dir")
        rh = d.get("rh")
        mr = d.get("mr")
        hh = d.get("height_m")
        td = d.get("td")

        out = f'data-time="{time_str}" data-level="{lvl}" '
        out += f'data-t="{t:.1f}" ' if t is not None else 'data-t="—" '
        out += f'data-td="{td:.1f}" ' if td is not None else 'data-td="—" '
        out += f'data-theta="{th:.1f}" ' if th is not None else 'data-theta="—" '
        out += f'data-wind="{ws:.1f}" ' if ws is not None else 'data-wind="—" '
        out += f'data-winddir="{wd:.0f}" ' if wd is not None else 'data-winddir="—" '
        out += f'data-rh="{rh:.0f}" ' if rh is not None else 'data-rh="—" '
        out += f'data-mr="{mr:.2f}" ' if mr is not None else 'data-mr="—" '
        out += f'data-height="{hh:.0f}" ' if hh is not None else 'data-height="—" '
        return out

    pts_t = []
    for lvl, t, theta, d in data:
        pts_t.append(f"{x_t(t):.2f},{y_pos(lvl):.2f}")
    if pts_t:
        parts.append(
            f'<polyline fill="none" stroke="#ff5470" stroke-width="2.5" '
            f'stroke-linejoin="round" points="{" ".join(pts_t)}"/>'
        )
        for lvl, t, theta, d in data:
            cx = x_t(t)
            cy = y_pos(lvl)
            attrs = _attrs(lvl, d)
            parts.append(
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" '
                f'r="4" fill="#ff5470" stroke="rgba(15,21,36,0.9)" '
                f'stroke-width="1.5" style="cursor:pointer;" {attrs}/>'
            )
            parts.append(
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" '
                f'r="12" fill="transparent" style="cursor:pointer;" '
                f'data-hitbox="1" {attrs}/>'
            )

    if thetas:
        pts_th = []
        for lvl, t, theta, d in data:
            if theta is not None:
                pts_th.append(f"{x_theta(theta):.2f},{y_pos(lvl):.2f}")
        if pts_th:
            parts.append(
                f'<polyline fill="none" stroke="#4dabff" stroke-width="1.5" '
                f'stroke-dasharray="5 3" stroke-linejoin="round" '
                f'points="{" ".join(pts_th)}"/>'
            )
            for lvl, t, theta, d in data:
                if theta is None:
                    continue
                cx = x_theta(theta)
                cy = y_pos(lvl)
                parts.append(
                    f'<circle cx="{cx:.2f}" cy="{cy:.2f}" '
                    f'r="3" fill="#4dabff" stroke="rgba(15,21,36,0.9)" '
                    f'stroke-width="1" style="cursor:pointer;" '
                    f'{_attrs(lvl, d)}/>'
                )

    parts.append(
        f'<text x="{pad_left}" y="20" fill="#ff5470" font-size="13" '
        f'font-family="Inter, sans-serif" font-weight="600">T, °C</text>'
    )
    parts.append(
        f'<text x="{pad_left + 80}" y="20" fill="#4dabff" font-size="13" '
        f'font-family="Inter, sans-serif" font-weight="600">θ, K (пунктир)</text>'
    )
    parts.append(
        f'<text x="{width - 20}" y="{height - 6}" '
        f'text-anchor="end" fill="#6b7694" font-size="10" '
        f'font-family="Inter, sans-serif">наведите на точку</text>'
    )

    parts.append('</svg>')
    return "".join(parts)


# ============================================================
# ЭКСПОРТ
# ============================================================
def synoptic_to_json(hours):
    """Сериализация для API/фронтенда."""
    def _clean(d):
        if isinstance(d, dict):
            return {k: _clean(v) for k, v in d.items()}
        if isinstance(d, (list, tuple)):
            return [_clean(x) for x in d]
        if isinstance(d, float) and (math.isnan(d) or math.isinf(d)):
            return None
        return d

    return json.dumps(_clean(hours), ensure_ascii=False, indent=2, default=str)


def synoptic_summary(hours):
    """Краткая сводка по всем часам — для дашборда."""
    if not hours:
        return {}
    tropo_vals = [h["tropopause_hPa"] for h in hours if h.get("tropopause_hPa")]
    li_vals = [h["indices"]["li"] for h in hours
               if h["indices"].get("li") is not None]
    k_vals = [h["indices"]["k_index"] for h in hours
              if h["indices"].get("k_index") is not None]
    return {
        "n_hours": len(hours),
        "n_fronts": sum(1 for h in hours if h.get("frontal_zone")),
        "n_jets": sum(1 for h in hours if h.get("jet")),
        "tropopause_range": (min(tropo_vals), max(tropo_vals)) if tropo_vals else None,
        "min_li": min(li_vals) if li_vals else None,
        "max_k": max(k_vals) if k_vals else None,
    }