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