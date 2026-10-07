# -*- coding: utf-8 -*-
"""
Синоптический анализ: фронты, циклоны, складки.
"""

from core.utils import calculate_potential_temperature


def analyze_synoptic(forecast):
    events = []
    for i in range(1, len(forecast)):
        h = forecast[i]
        prev = forecast[i - 1]
        p_now = h.get("pressure_hpa"); p_prev = prev.get("pressure_hpa")
        t_now = h.get("temp_c"); t_prev = prev.get("temp_c")
        th_now = h.get("theta_k"); th_prev = prev.get("theta_k")

        if None not in (p_now, p_prev, t_now, t_prev):
            dp = p_now - p_prev
            dt = t_now - t_prev
            if dp < -1.5 and dt < -2:
                events.append({"time": h["time"], "type": "cold_front",
                               "text": f"Холодный фронт (ΔP={dp:+.1f} гПа, ΔT={dt:+.1f} °C)"})
            elif dp < -1.5 and dt > 1.5:
                events.append({"time": h["time"], "type": "warm_front",
                               "text": f"Тёплый фронт (ΔP={dp:+.1f} гПа, ΔT={dt:+.1f} °C)"})
        if p_now is not None:
            if p_now < 995:
                events.append({"time": h["time"], "type": "cyclone",
                               "text": f"Циклон: {p_now:.0f} гПа"})
            elif p_now > 1025:
                events.append({"time": h["time"], "type": "anticyclone",
                               "text": f"Антициклон: {p_now:.0f} гПа"})
        if None not in (th_now, th_prev):
            d_theta = th_now - th_prev
            if d_theta > 1.5:
                events.append({"time": h["time"], "type": "fold",
                               "text": f"Складка: Δθ={d_theta:+.1f} K"})
    return events


# ============================================================
# СВОДКА ЗА СУТКИ
# ============================================================
# [PATCH analysis.synoptic.summarize_day]
def summarize_day(rows):
    """
    Возвращает сводку за сутки:
      {
        "situation": "циклон" | "антициклон" | ...,
        "phenomena": "туман, дождь" | "без существенных явлений",
        "phenomena_list": [...],
      }
    """
    if not rows:
        return {
            "situation": "нет данных",
            "phenomena": "нет данных",
            "phenomena_list": [],
        }

    # --- Обстановка: по среднему давлению ---
    pressures = [r.get("pressure_hpa") for r in rows if r.get("pressure_hpa") is not None]
    if pressures:
        p_avg = sum(pressures) / len(pressures)
        p_min = min(pressures)
        p_max = max(pressures)
        if p_avg < 1005:
            situation = "циклон"
        elif p_avg > 1020:
            situation = "антициклон"
        elif p_max - p_min > 10:
            situation = "гребень/ложбина"
        else:
            situation = "поле пониженного/повышенного давления"
    else:
        situation = "нет данных"

    # --- Явления: по weather_code и осадкам ---
    phenomena = set()
    for r in rows:
        code = r.get("weather_code")
        precip = r.get("precipitation_mm") or 0
        if code in (45, 48):
            phenomena.add("туман")
        if code in (95, 96, 99):
            phenomena.add("гроза")
        if code in (71, 73, 75, 77, 85, 86):
            phenomena.add("снег")
        elif precip > 0.1:
            phenomena.add("дождь")
        wind = r.get("wind_ms")
        if wind is not None and wind >= 12:
            phenomena.add("сильный ветер")

    phenomena_list = sorted(phenomena)
    phenomena_text = ", ".join(phenomena_list) if phenomena_list else "без существенных явлений"

    return {
        "situation": situation,
        "phenomena": phenomena_text,
        "phenomena_list": phenomena_list,
    }
