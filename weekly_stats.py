# -*- coding: utf-8 -*-
"""
Еженедельный расчёт матриц и метрик для всех станций и явлений.
Сохраняет CSV в ./stats/.

Запуск:
    python weekly_stats.py                    # все станции, все явления
    python weekly_stats.py --days 7           # за 7 дней
    python weekly_stats.py --out stats/       # куда сохранять

Для cron (каждую пятницу в 03:00):
    0 3 * * 5 cd /path/to/weather-server && python weekly_stats.py >> stats/cron.log 2>&1
"""

import os
import csv
import time
import argparse
import logging
from datetime import datetime, timedelta

from server import (
    STATIONS, MODELS, MIN_VERIFY_DATE,
    fetch_actual, fetch_previous_run,
)
from aviation_verify import (
    PHENOMENA, build_contingency, build_inertial_contingency,
    build_random_contingency, evaluate_all,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("weekly_stats")


def collect_hours(lat, lon, d_start, d_end, model=None):
    """Собирает часы факта (и, если model задан, прогноза)."""
    fact_hours = []
    fcst_hours = []
    dates_used = 0

    d = d_start
    while d <= d_end:
        date_str = d.strftime("%Y-%m-%d")
        if date_str < MIN_VERIFY_DATE:
            d += timedelta(days=1)
            continue
        try:
            fact, _ = fetch_actual(lat, lon, date_str)
        except Exception as e:
            log.warning("fact %s: %s", date_str, e)
            d += timedelta(days=1)
            continue

        fh = fact.get("hourly", {})
        f_times = fh.get("time", [])
        f_temp = fh.get("temperature_2m", [None] * len(f_times))
        f_prec = fh.get("precipitation", [0] * len(f_times))
        f_code = fh.get("weather_code", [None] * len(f_times))
        f_wind = fh.get("wind_speed_10m", [None] * len(f_times))

        for i, t in enumerate(f_times):
            wv = f_wind[i] if i < len(f_wind) else None
            fact_hours.append({
                "time": t,
                "temp_c": f_temp[i] if i < len(f_temp) else None,
                "precipitation_mm": f_prec[i] if i < len(f_prec) else 0,
                "weather_code": f_code[i] if i < len(f_code) else None,
                "wind_ms": wv / 3.6 if wv is not None else None,
            })

        if model:
            try:
                fcst = fetch_previous_run(model, lat, lon, date_str)
                ph = fcst.get("hourly", {})
                p_times = ph.get("time", [])
                p_temp = ph.get("temperature_2m_previous_day1", [None] * len(p_times))
                p_prec = ph.get("precipitation", [0] * len(p_times))
                p_code = ph.get("weather_code_previous_day1", [None] * len(p_times))
                p_wind = ph.get("wind_speed_10m_previous_day1", [None] * len(p_times))
                for i, t in enumerate(p_times):
                    wv = p_wind[i] if i < len(p_wind) else None
                    fcst_hours.append({
                        "time": t,
                        "temp_c": p_temp[i] if i < len(p_temp) else None,
                        "precipitation_mm": p_prec[i] if i < len(p_prec) else 0,
                        "weather_code": p_code[i] if i < len(p_code) else None,
                        "wind_ms": wv / 3.6 if wv is not None else None,
                    })
            except Exception as e:
                log.warning("fcst %s: %s", date_str, e)

        dates_used += 1
        d += timedelta(days=1)

    return fact_hours, fcst_hours, dates_used


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--out", type=str, default="stats")
    parser.add_argument("--station", type=str, default=None)
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    today = datetime.now().date()
    d_end = today - timedelta(days=1)
    d_start = d_end - timedelta(days=args.days - 1)

    stations = STATIONS if not args.station else {
        args.station: STATIONS[args.station]
    }

    rows = []
    t0 = time.time()

    for station_key, info in stations.items():
        log.info("=== Станция: %s ===", info["name"])

        fact_hours, _, dates_used = collect_hours(
            info["lat"], info["lon"], d_start, d_end, model=None
        )
        if not fact_hours:
            log.warning("нет данных для %s", station_key)
            continue

        for phenomenon_key in PHENOMENA.keys():
            for model_key in MODELS.keys():
                _, fcst_hours, _ = collect_hours(
                    info["lat"], info["lon"], d_start, d_end, model=model_key
                )
                if not fcst_hours:
                    continue

                m = build_contingency(fact_hours, fcst_hours, phenomenon_key)
                m_in = build_inertial_contingency(fact_hours, phenomenon_key)
                m_rd = build_random_contingency(fact_hours, phenomenon_key)
                ev = evaluate_all(m, m_in, m_rd)

                rows.append({
                    "station": station_key,
                    "station_name": info["name"],
                    "phenomenon": phenomenon_key,
                    "phenomenon_name": PHENOMENA[phenomenon_key]["name"],
                    "model": model_key,
                    "model_name": MODELS[model_key]["name"],
                    "date_start": d_start.isoformat(),
                    "date_end": d_end.isoformat(),
                    "dates_used": dates_used,
                    "hours": m.get("N", 0),
                    "n11": m["n11"], "n12": m["n12"],
                    "n21": m["n21"], "n22": m["n22"],
                    "p": ev.get("p"),
                    "H": ev.get("H"),
                    "Q": ev.get("Q"),
                    "v": ev.get("v"),
                    "tau": ev.get("tau"),
                    "A": ev.get("A"),
                    "S_haidke": ev.get("S_haidke"),
                    "inertial_p": (ev.get("inertial") or {}).get("p"),
                    "random_p": (ev.get("random") or {}).get("p"),
                })

    if not rows:
        log.warning("Нет данных для экспорта")
        return

    filename = os.path.join(
        args.out,
        "stats_" + d_end.strftime("%Y%m%d") + ".csv"
    )
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    log.info("CSV сохранён: %s (%d строк, %.1f сек)",
             filename, len(rows), time.time() - t0)


if __name__ == "__main__":
    main()