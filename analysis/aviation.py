# -*- coding: utf-8 -*-
"""
Авиационные методы по Богаткину.
"""


def waiting_index(t850, td850, t700, td700, t500):
    if None in (t850, td850, t700, td700, t500):
        return None
    d850 = t850 - td850
    d700 = t700 - td700
    return round(2 * t850 - t500 - d850 - d700, 1)


def waiting_forecast(k):
    if k is None: return ("нет данных", "—", 0)
    if k < 20:   return ("нет", "Гроз нет", 5)
    if k < 25:   return ("слабая", "Слабые грозы", 20)
    if k < 30:   return ("умеренная", "Умеренные грозы", 40)
    if k < 35:   return ("сильная", "Многочисленные грозы", 70)
    return ("очень сильная", "Повсеместные грозы, град", 90)


def lifted_index_forecast(li):
    if li is None: return ("нет данных", "—", 0)
    if li > 0:    return ("устойчиво", "Гроз нет", 5)
    if li > -2:   return ("слабая", "Слабая неустойчивость", 15)
    if li > -4:   return ("умеренная", "Отдельные грозы", 40)
    if li > -6:   return ("сильная", "Многочисленные грозы", 70)
    return ("очень сильная", "Ливни, град", 90)


def cape_forecast(cape):
    if cape is None: return ("нет данных", "—", 0)
    if cape < 300:  return ("нет", "Гроз нет", 5)
    if cape < 800:  return ("слабая", "Слабые грозы", 20)
    if cape < 1500: return ("умеренная", "Умеренные грозы", 40)
    if cape < 2500: return ("сильная", "Сильные грозы", 70)
    return ("очень сильная", "Очень сильные, град", 90)


def combined_thunder_risk(t850, td850, t700, td700, t500, li, cape):
    k = waiting_index(t850, td850, t700, td700, t500)
    w_level, w_text, w_prob = waiting_forecast(k)
    l_level, l_text, l_prob = lifted_index_forecast(li)
    c_level, c_text, c_prob = cape_forecast(cape)

    combined_prob = round(w_prob * 0.25 + l_prob * 0.40 + c_prob * 0.35)

    if combined_prob < 10:   level, text = "нет", "Гроз нет"
    elif combined_prob < 30: level, text = "слабая", "Слабая вероятность"
    elif combined_prob < 50: level, text = "умеренная", "Умеренная вероятность"
    elif combined_prob < 75: level, text = "сильная", "Высокая вероятность"
    else:                    level, text = "очень сильная", "Очень высокая вероятность"

    return {
        "k": k, "waiting_text": w_text, "waiting_prob": w_prob,
        "li": li, "lifted_text": l_text, "lifted_prob": l_prob,
        "cape": cape, "cape_text": c_text, "cape_prob": c_prob,
        "combined_level": level,
        "combined_text": text,
        "combined_prob": combined_prob,
    }


def fog_forecast(temp_2m, dew_2m, wind_ms, cloud_cover, hour, rh=None):
    if temp_2m is None or dew_2m is None or wind_ms is None:
        return {"level": "нет данных", "text": "—", "probability": 0,
                "checks": {}, "td_deficit": None, "score": 0}

    td_def = temp_2m - dew_2m
    check_sat = td_def <= 2.0
    check_wind = 0.5 <= wind_ms <= 3.0
    check_cloud = (cloud_cover is None) or (cloud_cover < 30)
    check_night = 0 <= hour <= 9
    check_rh = (rh is None) or (rh >= 90)

    score = sum([check_sat, check_wind, check_cloud, check_night, check_rh])

    if score <= 1:   level, text, prob = "нет", "Туман не ожидается", 5
    elif score == 2: level, text, prob = "слабая", "Слабая вероятность", 20
    elif score == 3: level, text, prob = "умеренная", "Умеренная вероятность", 40
    elif score == 4: level, text, prob = "высокая", "Высокая вероятность", 70
    else:            level, text, prob = "очень высокая", "Туман очень вероятен", 90

    return {
        "level": level, "text": text, "probability": prob,
        "checks": {
            "saturation": check_sat,
            "wind": check_wind,
            "cloud": check_cloud,
            "night": check_night,
            "humidity": check_rh,
        },
        "td_deficit": round(td_def, 1),
        "score": score,
    }