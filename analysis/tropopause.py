# -*- coding: utf-8 -*-
"""
Расчёт EPV (Ertel Potential Vorticity) и поиск складок тропопаузы.

Формула EPV (упрощённая, в изобарических координатах):
    PV ≈ -g * (ζ + f) * (Δθ / Δp)

где:
    g  — ускорение свободного падения (9.81 м/с²)
    ζ  — относительная завихрённость (из поля ветра)
    f  — параметр Кориолиса = 2 * Ω * sin(φ)
    Δθ — разница потенциальных температур между уровнями
    Δp — разница давлений (Па)

Единицы: 1 PVU = 10^-6 м²·К·кг⁻¹·с⁻¹
"""

import math
from core.config import TROPOPAUSE_LEVELS, PVU_THRESHOLD
from core.utils import calculate_potential_temperature


# ============================================================
# ФИЗИЧЕСКИЕ КОНСТАНТЫ
# ============================================================
G = 9.81           # м/с²
OMEGA = 7.2921e-5  # рад/с — угловая скорость Земли


def coriolis_parameter(lat):
    """Параметр Кориолиса f = 2Ω·sin(φ)."""
    return 2 * OMEGA * math.sin(math.radians(lat))


def relative_vorticity(wind_speed_ms, wind_dir_deg, lat, lon, dlat=0.5):
    """
    Приблизительная относительная завихрённость ζ.
    
    В идеале требует пространственных производных поля ветра.
    Здесь используем упрощение: ζ ≈ (V / R), где R — характерный
    радиус кривизны. Для глобального масштаба это даёт лишь оценку.
    
    Более точный метод — численное дифференцирование поля ветра
    по широте и долготе (требует запроса соседних точек).
    """
    if wind_speed_ms is None or lat is None:
        return 0.0
    # Характерный радиус синоптического масштаба ~ 500 км
    R_char = 500_000  # м
    return wind_speed_ms / R_char


def compute_epv_profile(hourly_data, lat, lon, hour_index):
    """
    Вычисляет профиль EPV по уровням давления для одного часа.
    
    hourly_data: dict из fetch_pressure_level_data
    hour_index: индекс часа в массиве time
    Возвращает список dict:
        [{level, pressure_pa, theta_k, pv_pv u, is_stratosphere}, ...]
    """
    hourly = hourly_data.get("hourly", {})
    profile = []

    f = coriolis_parameter(lat)

    for i, level in enumerate(TROPOPAUSE_LEVELS):
        temp_key = f"temperature_{level}hPa"
        wind_key = f"wind_speed_{level}hPa"
        wdir_key = f"wind_direction_{level}hPa"
        height_key = f"geopotential_height_{level}hPa"

        temp_arr = hourly.get(temp_key, [])
        wind_arr = hourly.get(wind_key, [])
        wdir_arr = hourly.get(wdir_key, [])
        height_arr = hourly.get(height_key, [])

        t = temp_arr[hour_index] if hour_index < len(temp_arr) else None
        ws_raw = wind_arr[hour_index] if hour_index < len(wind_arr) else None
        # Open-Meteo отдаёт wind_speed в км/ч → перевод в м/с
        ws = (ws_raw / 3.6) if ws_raw is not None else None
        wd = wdir_arr[hour_index] if hour_index < len(wdir_arr) else None
        h = height_arr[hour_index] if hour_index < len(height_arr) else None

        pressure_pa = level * 100  # гПа → Па
        theta_k = calculate_potential_temperature(t, level) if t is not None else None

        profile.append({
            "level": level,
            "pressure_pa": pressure_pa,
            "temp_c": t,
            "wind_ms": ws,
            "wind_dir": wd,
            "height_m": h,
            "theta_k": theta_k,
            "pv_pvu": None,
            "is_stratosphere": None,
        })

    # Считаем PV между соседними уровнями
    for i in range(len(profile) - 1):
        upper = profile[i]      # меньшее давление (выше)
        lower = profile[i + 1]  # большее давление (ниже)

        if upper["theta_k"] is None or lower["theta_k"] is None:
            upper["pv_pvu"] = None
            continue

        d_theta = upper["theta_k"] - lower["theta_k"]  # К
        d_p = upper["pressure_pa"] - lower["pressure_pa"]  # Па (отрицательно)

        if d_p == 0:
            upper["pv_pvu"] = None
            continue

        # ζ — оценка
        zeta = relative_vorticity(upper["wind_ms"], upper["wind_dir"], lat, lon)

        # PV в СИ: -g * (ζ + f) * (Δθ / Δp)  [K·m²·кг⁻¹·с⁻¹]
        pv_si = -G * (zeta + f) * (d_theta / d_p)

        # Перевод в PVU: 1 PVU = 10^-6
        pv_pvu = pv_si * 1e6
        upper["pv_pvu"] = round(pv_pvu, 2)

    # Помечаем стратосферу/тропосферу
    for p in profile:
        pv = p.get("pv_pvu")
        if pv is None:
            p["is_stratosphere"] = None
        else:
            p["is_stratosphere"] = pv >= PVU_THRESHOLD

    # Оценка высоты динамической тропопаузы
    # (первый уровень сверху, где PV >= 2 PVU)
    tropopause_level = None
    for p in profile:
        if p.get("is_stratosphere"):
            tropopause_level = p
            break

    return {
        "profile": profile,
        "tropopause_level_hPa": tropopause_level["level"] if tropopause_level else None,
        "tropopause_height_m": tropopause_level["height_m"] if tropopause_level else None,
    }


def detect_folds(hourly_data, lat, lon, hour_index):
    """
    Ищет складки тропопаузы: аномалии PV > 2 PVU ниже типичной высоты тропопаузы.
    
    Возвращает dict:
        {
            "has_fold": bool,
            "fold_levels": [levels],
            "max_pv": float,
            "fold_depth_hPa": int,
            "description": str,
        }
    """
    result = compute_epv_profile(hourly_data, lat, lon, hour_index)
    profile = result["profile"]

    # Собираем уровни с высоким PV
    high_pv_levels = [p for p in profile if (p.get("pv_pvu") or 0) >= PVU_THRESHOLD]

    if not high_pv_levels:
        # Считаем max_pv по всем уровням (даже без складок — для графика и сводки)
        all_pvs = [p["pv_pvu"] for p in profile if p.get("pv_pvu") is not None]
        max_pv_all = max(all_pvs) if all_pvs else 0
        return {
            "has_fold": False,
            "fold_levels": [],
            "max_pv": round(max_pv_all, 2),
            "fold_depth_hPa": 0,
            "description": "Складок не обнаружено",
            "tropopause_level_hPa": result["tropopause_level_hPa"],
            "profile": profile,
        }

    # Типичная тропопауза для умеренных широт — около 250 гПа
    # Если PV > 2 PVU обнаружен ниже 300 гПа — это складка
    fold_levels = [p for p in high_pv_levels if p["level"] >= 300]

    all_pvs = [p["pv_pvu"] for p in profile if p.get("pv_pvu") is not None]
    max_pv = max(all_pvs) if all_pvs else 0

    # Глубина складки: разница между самым верхним и самым нижним уровнями с PV > 2
    if len(high_pv_levels) > 1:
        depth = high_pv_levels[-1]["level"] - high_pv_levels[0]["level"]
    else:
        depth = 0

    # Классификация глубины (по 3-D labeling подходу)
    if depth < 200:
        depth_class = "мелкая"
    elif depth < 350:
        depth_class = "средняя"
    else:
        depth_class = "глубокая"

    if fold_levels:
        description = (
            f"Обнаружена {depth_class} складка: "
            f"PV > {PVU_THRESHOLD} PVU на уровнях "
            f"{', '.join(str(p['level']) for p in fold_levels)} гПа. "
            f"Максимум PV = {max_pv:.2f} PVU."
        )
    else:
        description = (
            f"Стратосферный воздух (PV > {PVU_THRESHOLD} PVU) "
            f"обнаружен выше 300 гПа — складка отсутствует."
        )

    return {
        "has_fold": bool(fold_levels),
        "fold_levels": [p["level"] for p in fold_levels],
        "max_pv": round(max_pv, 2),
        "fold_depth_hPa": depth,
        "fold_depth_class": depth_class,
        "description": description,
        "tropopause_level_hPa": result["tropopause_level_hPa"],
        "profile": profile,
    }


def analyze_day(hourly_data, lat, lon):
    """
    Анализирует весь день: ищет складки в каждом часе.
    Возвращает список результатов по часам + сводку.
    """
    hourly = hourly_data.get("hourly", {})
    times = hourly.get("time", [])

    hours_result = []
    for i, t in enumerate(times):
        res = detect_folds(hourly_data, lat, lon, i)
        res["time"] = t
        hours_result.append(res)

    # Сводка
    folds_count = sum(1 for h in hours_result if h["has_fold"])
    max_pv_day = max(
        (h["max_pv"] for h in hours_result if h.get("max_pv") is not None),
        default=0
    )

    return {
        "hours": hours_result,
        "summary": {
            "total_hours": len(hours_result),
            "folds_count": folds_count,
            "max_pv_day": round(max_pv_day, 2),
            "has_any_fold": folds_count > 0,
        }
    }