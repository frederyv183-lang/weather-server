# -*- coding: utf-8 -*-
"""
Матрица сопряжённости альтернативных прогнозов и критерии успешности.

По учебнику: Дробжева Я.В., Волобуева О.В. «Метеорологические прогнозы
и их экономическая полезность», глава 2 (метод Л.А. Хандожко).
"""

import math


# ============================================================
# ПОРОГИ ДЛЯ ЯВЛЕНИЙ
# ============================================================
PHENOMENA = {
    "thunder": {
        "name": "Гроза",
        "unit": "код WMO",
        "check": lambda h: h.get("weather_code") in (95, 96, 99),
    },
    "rain": {
        "name": "Дождь",
        "unit": "мм/ч",
        "check": lambda h: (h.get("precipitation_mm") or 0) >= 0.5,
    },
    "heavy_rain": {
        "name": "Сильный дождь",
        "unit": "мм/ч",
        "check": lambda h: (h.get("precipitation_mm") or 0) >= 5.0,
    },
    "fog": {
        "name": "Туман",
        "unit": "код WMO",
        "check": lambda h: h.get("weather_code") in (45, 48),
    },
    "snow": {
        "name": "Снег",
        "unit": "код WMO",
        "check": lambda h: h.get("weather_code") in (71, 73, 75, 77, 85, 86),
    },
    "wind": {
        "name": "Сильный ветер",
        "unit": "м/с",
        "check": lambda h: (h.get("wind_ms") or 0) >= 12.0,
    },
    "frost": {
        "name": "Заморозок",
        "unit": "°C",
        "check": lambda h: (h.get("temp_c") is not None and h.get("temp_c") <= 0),
    },
    "heat": {
        "name": "Сильная жара",
        "unit": "°C",
        "check": lambda h: (h.get("temp_c") is not None and h.get("temp_c") >= 25),
    },
}


# ============================================================
# МАТРИЦА СОПРЯЖЁННОСТИ МЕТОДИЧЕСКОГО ПРОГНОЗА
# ============================================================
def build_contingency(fact_hours, fcst_hours, phenomenon_key):
    """Строит матрицу сопряжённости 2×2 для альтернативного прогноза."""
    ph = PHENOMENA[phenomenon_key]
    check = ph["check"]

    fact_map = {h["time"]: h for h in fact_hours}
    fcst_map = {h["time"]: h for h in fcst_hours}
    common = sorted(set(fact_map) & set(fcst_map))

    n11 = n12 = n21 = n22 = 0
    for t in common:
        f_has = check(fact_map[t])
        p_has = check(fcst_map[t])
        if f_has and p_has:       n11 += 1
        elif f_has and not p_has: n12 += 1
        elif not f_has and p_has: n21 += 1
        else:                     n22 += 1

    n10 = n11 + n12
    n20 = n21 + n22
    n01 = n11 + n21
    n02 = n12 + n22
    N = n11 + n12 + n21 + n22

    return {
        "n11": n11, "n12": n12, "n21": n21, "n22": n22,
        "n10": n10, "n20": n20, "n01": n01, "n02": n02,
        "N": N,
    }


# ============================================================
# ИНЕРЦИОННАЯ МАТРИЦА
# ============================================================
def build_inertial_contingency(fact_hours, phenomenon_key):
    """Инерционный прогноз: прогноз на час t = факт в час t-1."""
    ph = PHENOMENA[phenomenon_key]
    check = ph["check"]

    fact_sorted = sorted(fact_hours, key=lambda h: h["time"])
    n11 = n12 = n21 = n22 = 0

    for i in range(1, len(fact_sorted)):
        prev_has = check(fact_sorted[i - 1])
        cur_has = check(fact_sorted[i])
        if cur_has and prev_has:       n11 += 1
        elif cur_has and not prev_has: n12 += 1
        elif not cur_has and prev_has: n21 += 1
        else:                          n22 += 1

    n10 = n11 + n12
    n20 = n21 + n22
    n01 = n11 + n21
    n02 = n12 + n22
    N = n11 + n12 + n21 + n22

    return {
        "n11": n11, "n12": n12, "n21": n21, "n22": n22,
        "n10": n10, "n20": n20, "n01": n01, "n02": n02,
        "N": N,
    }


# ============================================================
# СЛУЧАЙНАЯ МАТРИЦА
# ============================================================
def build_random_contingency(fact_hours, phenomenon_key):
    """
    Случайный прогноз по Хандожко.

    Формула (см. учебник, раздел 2.1.1):
      n11 = n10 * n01 / N
      n12 = n10 * n02 / N
      n21 = n20 * n01 / N
      n22 = n20 * n02 / N
    """
    ph = PHENOMENA[phenomenon_key]
    check = ph["check"]

    n10 = sum(1 for h in fact_hours if check(h))
    n20 = len(fact_hours) - n10
    N = len(fact_hours)

    if N == 0:
        return {"n11": 0, "n12": 0, "n21": 0, "n22": 0,
                "n10": 0, "n20": 0, "n01": 0, "n02": 0, "N": 0}

    p1 = n10 / N
    n01 = round(N * p1)
    n02 = N - n01

    n11 = round(n10 * n01 / N) if N else 0
    n12 = n10 - n11
    n21 = n01 - n11
    n22 = n20 - n21

    return {
        "n11": n11, "n12": n12, "n21": n21, "n22": n22,
        "n10": n10, "n20": n20, "n01": n01, "n02": n02,
        "N": N,
    }


# ============================================================
# КЛИМАТОЛОГИЧЕСКАЯ МАТРИЦА (5-летняя норма)
# ============================================================
def build_climatological_contingency(fact_hours, phenomenon_key,
                                     norm_map=None, threshold=0.5):
    """
    Климатологический прогноз по Хандожко (раздел 2.1.1).

    Прогноз = «явление ожидается», если в этот день года за последние
    5 лет оно наблюдалось чаще, чем в threshold доле часов.
    """
    ph = PHENOMENA[phenomenon_key]
    check = ph["check"]

    n11 = n12 = n21 = n22 = 0

    for h in fact_hours:
        t = h.get("time", "")
        if len(t) < 13:
            continue
        try:
            month = int(t[5:7])
            day = int(t[8:10])
            hour = int(t[11:13])
        except (ValueError, IndexError):
            continue

        if norm_map:
            prob = norm_map.get((month, day, hour), 0.0)
            p_has = prob >= threshold
        else:
            p_has = True

        f_has = check(h)

        if f_has and p_has:       n11 += 1
        elif f_has and not p_has: n12 += 1
        elif not f_has and p_has: n21 += 1
        else:                     n22 += 1

    n10 = n11 + n12
    n20 = n21 + n22
    n01 = n11 + n21
    n02 = n12 + n22
    N = n11 + n12 + n21 + n22

    return {
        "n11": n11, "n12": n12, "n21": n21, "n22": n22,
        "n10": n10, "n20": n20, "n01": n01, "n02": n02,
        "N": N,
    }


def build_climate_norm(fact_hours_by_year, phenomenon_key, years=5):
    """
    Строит карту климатических норм на основе данных за N лет.
    Возвращает dict {(month, day, hour): probability 0..1}.
    """
    ph = PHENOMENA[phenomenon_key]
    check = ph["check"]

    counts = {}
    totals = {}

    for year, hours in fact_hours_by_year.items():
        seen_this_year = set()
        for h in hours:
            t = h.get("time", "")
            if len(t) < 13:
                continue
            try:
                month = int(t[5:7])
                day = int(t[8:10])
                hour = int(t[11:13])
            except (ValueError, IndexError):
                continue

            key = (month, day, hour)
            totals[key] = totals.get(key, 0) + 1

            year_key = (year, key)
            if year_key in seen_this_year:
                continue
            seen_this_year.add(year_key)

            if check(h):
                counts[key] = counts.get(key, 0) + 1

    norm_map = {}
    for key, total in totals.items():
        if total == 0:
            norm_map[key] = 0.0
        else:
            norm_map[key] = counts.get(key, 0) / total

    return norm_map


# ============================================================
# КРИТЕРИИ УСПЕШНОСТИ
# ============================================================
def criterion_p(m):
    N = m["N"]
    if N == 0: return None
    return (m["n11"] + m["n22"]) / N


def criterion_H(m):
    n10 = m["n10"]
    if n10 == 0: return None
    return m["n11"] / n10


def criterion_Q(m):
    n01 = m["n01"]
    if n01 == 0: return None
    return m["n11"] / n01


def criterion_entropy(m):
    N = m["N"]
    if N == 0: return None
    p1 = m["n10"] / N
    p2 = m["n20"] / N
    H = 0.0
    for p in (p1, p2):
        if p > 0:
            H -= p * math.log(p)
    return H


def criterion_conditional_entropy(m):
    N = m["N"]
    if N == 0: return None

    def h_cond(n_ij, n_i0):
        if n_i0 == 0: return 0.0
        h = 0.0
        for n in n_ij:
            p = n / n_i0
            if p > 0:
                h -= p * math.log(p)
        return h

    h_yes = h_cond([m["n11"], m["n21"]], m["n01"])
    h_no  = h_cond([m["n12"], m["n22"]], m["n02"])
    p_yes = m["n01"] / N
    p_no  = m["n02"] / N
    return p_yes * h_yes + p_no * h_no


def criterion_v(m):
    H0 = criterion_entropy(m)
    H1 = criterion_conditional_entropy(m)
    if H0 is None or H1 is None or H0 == 0:
        return None
    return 1 - H1 / H0


def criterion_S_haidke(m, m_std):
    N = m["N"]
    E_std = m_std["n11"] + m_std["n22"]
    if N == E_std: return None
    return ((m["n11"] + m["n22"]) - E_std) / (N - E_std)


def criterion_tau_goodman_kruskal(m):
    N = m["N"]
    if N == 0: return None

    cells = [
        (m["n11"], m["n10"], m["n01"]),
        (m["n12"], m["n10"], m["n02"]),
        (m["n21"], m["n20"], m["n01"]),
        (m["n22"], m["n20"], m["n02"]),
    ]
    sum1 = 0.0
    sum2 = 0.0
    for n_ij, n_i0, n_0j in cells:
        diff = N * n_ij - n_i0 * n_0j
        if n_0j != 0: sum1 += diff * diff / n_0j
        if n_i0 != 0: sum2 += diff * diff / n_i0

    num = sum1 + sum2
    den = (2 * N ** 3
           - N * (m["n10"] ** 2 + m["n20"] ** 2
                  + m["n01"] ** 2 + m["n02"] ** 2))
    if den == 0: return None
    return num / den


def criterion_A(m):
    n11, n12, n21, n22 = m["n11"], m["n12"], m["n21"], m["n22"]
    d = (n11 + n12) * (n21 + n22) * (n11 + n21) * (n12 + n22)
    if d <= 0: return None
    return (n11 * n22 - n12 * n21) / math.sqrt(d)


# ============================================================
# СВОДНАЯ ОЦЕНКА
# ============================================================
def evaluate_all(m, m_inertial=None, m_random=None, m_climat=None):
    result = {
        "contingency": m,
        "p":  criterion_p(m),
        "H":  criterion_H(m),
        "Q":  criterion_Q(m),
        "H_entropy": criterion_entropy(m),
        "v":  criterion_v(m),
        "tau": criterion_tau_goodman_kruskal(m),
        "A":  criterion_A(m),
    }
    if m_inertial is not None:
        result["inertial"] = {
            "contingency": m_inertial,
            "p":  criterion_p(m_inertial),
            "H":  criterion_H(m_inertial),
            "Q":  criterion_Q(m_inertial),
            "v":  criterion_v(m_inertial),
            "tau": criterion_tau_goodman_kruskal(m_inertial),
            "A":  criterion_A(m_inertial),
        }
        result["S_haidke"] = criterion_S_haidke(m, m_inertial)
    if m_random is not None:
        result["random"] = {
            "contingency": m_random,
            "p":  criterion_p(m_random),
            "H":  criterion_H(m_random),
            "Q":  criterion_Q(m_random),
            "v":  criterion_v(m_random),
            "tau": criterion_tau_goodman_kruskal(m_random),
            "A":  criterion_A(m_random),
        }
    if m_climat is not None:
        result["climatological"] = {
            "contingency": m_climat,
            "p":  criterion_p(m_climat),
            "H":  criterion_H(m_climat),
            "Q":  criterion_Q(m_climat),
            "v":  criterion_v(m_climat),
            "tau": criterion_tau_goodman_kruskal(m_climat),
            "A":  criterion_A(m_climat),
        }
    return result
    

# ============================================================
# NOAA — СУТОЧНЫЕ МАТРИЦЫ
# ============================================================
# Для исторических данных NOAA (TMAX/TMIN/PRCP) строим матрицу
# по суточным наблюдениям. Пороги для явлений — упрощённые,
# т.к. NOAA даёт только суточные агрегаты.

def _phenomenon_present(day, phenomenon_key):
    """
    Проверяет, есть ли явление в суточных данных NOAA.
    day: dict {date, tmax, tmin, prcp}
    phenomenon_key: ключ из PHENOMENA
    """
    tmax = day.get("tmax")
    tmin = day.get("tmin")
    prcp = day.get("prcp") or 0

    if phenomenon_key == "rain":
        return prcp >= 0.5
    if phenomenon_key == "heavy_rain":
        return prcp >= 5.0
    if phenomenon_key == "snow":
        # В NOAA нет weather_code, поэтому снег определяем
        # по осадкам при отрицательной или близкой к нулю Tmax
        return prcp >= 0.5 and tmax is not None and tmax < 1.0
    if phenomenon_key == "fog":
        # Нет данных о видимости — считаем, что тумана не было
        return False
    if phenomenon_key == "thunder":
        # Нет weather_code — считаем, что грозы не было
        return False
    if phenomenon_key == "heat":
        return tmax is not None and tmax >= 25.0
    if phenomenon_key == "frost":
        return tmin is not None and tmin <= 0.0
    if phenomenon_key == "wind":
        # Нет данных о ветре в daily-summaries
        return False

    return False


def _make_daily_matrix(n11, n12, n21, n22):
    """Собирает матрицу в формате, совместимом с build_contingency."""
    n11 = int(n11); n12 = int(n12); n21 = int(n21); n22 = int(n22)
    return {
        "n11": n11, "n12": n12, "n21": n21, "n22": n22,
        "n10": n11 + n12, "n20": n21 + n22,
        "n01": n11 + n21, "n02": n12 + n22,
        "N": n11 + n12 + n21 + n22,
    }


def build_daily_contingency_noaa(fact_daily, fcst_daily, phenomenon_key):
    """
    Строит матрицу сопряжённости по СУТОЧНЫМ данным NOAA.
    fact_daily: список dict {date, tmax, tmin, prcp}
    fcst_daily: список dict {date, tmax, tmin, prcp} — прогноз, агрегированный по дням
    phenomenon_key: ключ из PHENOMENA
    """
    if phenomenon_key not in PHENOMENA:
        raise ValueError(f"Неизвестное явление: {phenomenon_key}")

    f_by_date = {d["date"]: d for d in fact_daily}
    p_by_date = {d["date"]: d for d in fcst_daily}
    common = sorted(set(f_by_date) & set(p_by_date))

    n11 = n12 = n21 = n22 = 0
    for date in common:
        f_has = _phenomenon_present(f_by_date[date], phenomenon_key)
        p_has = _phenomenon_present(p_by_date[date], phenomenon_key)
        if f_has and p_has:       n11 += 1
        elif f_has and not p_has: n12 += 1
        elif not f_has and p_has: n21 += 1
        else:                     n22 += 1

    return _make_daily_matrix(n11, n12, n21, n22)


def build_inertial_contingency_noaa(fact_daily, phenomenon_key):
    """
    Инерционная матрица для суточных данных NOAA:
    прогноз на день t = факт в день t−1.
    """
    if phenomenon_key not in PHENOMENA:
        raise ValueError(f"Неизвестное явление: {phenomenon_key}")

    sorted_days = sorted(fact_daily, key=lambda d: d["date"])
    n11 = n12 = n21 = n22 = 0

    for i in range(1, len(sorted_days)):
        prev_has = _phenomenon_present(sorted_days[i - 1], phenomenon_key)
        cur_has = _phenomenon_present(sorted_days[i], phenomenon_key)
        if cur_has and prev_has:       n11 += 1
        elif cur_has and not prev_has: n12 += 1
        elif not cur_has and prev_has: n21 += 1
        else:                          n22 += 1

    return _make_daily_matrix(n11, n12, n21, n22)