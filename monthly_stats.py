# -*- coding: utf-8 -*-
"""
Сводная статистика сравнения прогнозов с фактом.

Сравниваем по трём блокам:
  1. Температура  — MAE, RMSE, Bias
  2. Осадки       — MAE, RMSE, Bias
  3. Явления      — часы с осадками: факт / прогноз / совпало /
                    пропуск / ложная тревога

Важно: ERA5 (архив) обновляется с задержкой ~5 дней,
поэтому по умолчанию окно сдвинуто назад:
берём дни [сегодня-5-N] ... [сегодня-5].

Запуск:
    python monthly_stats.py                     # 30 дней, все станции
    python monthly_stats.py --days 60           # 60 дней
    python monthly_stats.py --station tushino   # только Тушино
    python monthly_stats.py --export stats.csv  # CSV для Excel
    python monthly_stats.py --lag 0             # без сдвига (для теста)
"""

import csv
import json
import math
import time
import argparse
import logging
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from server import (
    fetch_actual,
    fetch_previous_run,
    _align_by_time,
    STATIONS,
    MODELS,
    MIN_VERIFY_DATE,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("monthly_stats")

# Сдвиг назад от сегодняшнего дня — ERA5 обновляется с задержкой
DEFAULT_LAG_DAYS = 5


# ============================================================
# СРАВНЕНИЕ ОДНОГО ДНЯ
# ============================================================
def compare_day(model_key, lat, lon, date_str):
    """Сравнивает прогноз (за сутки) с фактом за конкретный день."""
    if date_str < MIN_VERIFY_DATE:
        return {"error": f"данные доступны только с {MIN_VERIFY_DATE}"}

    try:
        fact, source = fetch_actual(lat, lon, date_str)
    except Exception as e:
        return {"error": f"факт: {e}"}

    try:
        fcst = fetch_previous_run(model_key, lat, lon, date_str)
    except Exception as e:
        return {"error": f"прогноз: {e}"}

    fact_h = fact.get("hourly", {})
    fcst_h = fcst.get("hourly", {})

    if not fact_h.get("time"):
        return {"error": "факт пуст", "source": source}
    if not fcst_h.get("time"):
        return {"error": "прогноз пуст", "source": source}

    t_err, p_err, n_common = _align_by_time(fact_h, fcst_h)
    if not t_err:
        return {"error": f"нет общих часов (факт={len(fact_h.get('time', []))}, "
                         f"прогноз={len(fcst_h.get('time', []))})",
                "source": source}

    t_mae  = sum(abs(e) for e in t_err) / len(t_err)
    t_bias = sum(t_err) / len(t_err)
    t_rmse = math.sqrt(sum(e**2 for e in t_err) / len(t_err))

    p_mae  = sum(abs(e) for e in p_err) / len(p_err) if p_err else None
    p_bias = sum(p_err) / len(p_err) if p_err else None
    p_rmse = math.sqrt(sum(e**2 for e in p_err) / len(p_err)) if p_err else None

    fact_prec = dict(zip(fact_h.get("time", []),
                         fact_h.get("precipitation", [])))
    fcst_prec = dict(zip(fcst_h.get("time", []),
                         fcst_h.get("precipitation", [])))

    fact_precip_hours = 0
    fcst_precip_hours = 0
    both_precip = 0
    fact_only_precip = 0
    fcst_only_precip = 0

    for t in sorted(set(fact_prec) & set(fcst_prec)):
        fp = fact_prec.get(t)
        op = fcst_prec.get(t)
        if fp is None or op is None:
            continue
        f_has = fp > 0.05
        o_has = op > 0.05
        if f_has: fact_precip_hours += 1
        if o_has: fcst_precip_hours += 1
        if f_has and o_has: both_precip += 1
        elif f_has and not o_has: fact_only_precip += 1
        elif o_has and not f_has: fcst_only_precip += 1

    return {
        "date": date_str,
        "source": source,
        "temp_mae":  round(t_mae, 2),
        "temp_rmse": round(t_rmse, 2),
        "temp_bias": round(t_bias, 2),
        "prec_mae":  round(p_mae, 2) if p_mae is not None else None,
        "prec_rmse": round(p_rmse, 2) if p_rmse is not None else None,
        "prec_bias": round(p_bias, 2) if p_bias is not None else None,
        "hours": len(t_err),
        "fact_precip_hours": fact_precip_hours,
        "fcst_precip_hours": fcst_precip_hours,
        "both_precip": both_precip,
        "fact_only_precip": fact_only_precip,
        "fcst_only_precip": fcst_only_precip,
    }


# ============================================================
# СБОР ЗА ПЕРИОД
# ============================================================
def collect_stats(days=30, station_filter=None, lag_days=DEFAULT_LAG_DAYS):
    """
    Собирает статистику за `days` дней, сдвинутых на `lag_days` назад
    от сегодняшнего дня (из-за задержки ERA5).
    """
    today = datetime.now(timezone.utc).date()
    end_date = today - timedelta(days=lag_days)

    def new_bucket():
        return {
            "temp_mae": [], "temp_rmse": [], "temp_bias": [],
            "prec_mae": [], "prec_rmse": [], "prec_bias": [],
            "hours": [], "days_count": 0,
            "sources": defaultdict(int),
            "fact_precip_hours": 0,
            "fcst_precip_hours": 0,
            "both_precip": 0,
            "fact_only_precip": 0,
            "fcst_only_precip": 0,
            "errors": [],
        }

    results = defaultdict(lambda: defaultdict(new_bucket))

    stations = STATIONS if not station_filter else {
        station_filter: STATIONS[station_filter]
    }

    total = days * len(stations) * len(MODELS)
    done = 0

    log.info("Диапазон дат: %s … %s (сдвиг %d дн.)",
             (end_date - timedelta(days=days - 1)).isoformat(),
             end_date.isoformat(), lag_days)

    for d in range(days, 0, -1):
        date_str = (end_date - timedelta(days=d - 1)).strftime("%Y-%m-%d")
        if date_str < MIN_VERIFY_DATE:
            continue

        for station_key, info in stations.items():
            for model_key in MODELS.keys():
                done += 1
                if done % 20 == 0:
                    log.info("Прогресс: %d/%d", done, total)
                r = compare_day(model_key, info["lat"], info["lon"], date_str)

                if r.get("error"):
                    msg = f"{station_key}/{model_key}/{date_str} — {r['error']}"
                    log.warning("SKIP %s", msg)
                    results[station_key][model_key]["errors"].append(msg)
                    continue

                b = results[station_key][model_key]
                for key in ("temp_mae", "temp_rmse", "temp_bias",
                            "prec_mae", "prec_rmse", "prec_bias"):
                    if r.get(key) is not None:
                        b[key].append(r[key])
                if r.get("hours"):
                    b["hours"].append(r["hours"])
                b["days_count"] += 1
                b["sources"][r.get("source", "—")] += 1
                b["fact_precip_hours"] += r.get("fact_precip_hours", 0)
                b["fcst_precip_hours"] += r.get("fcst_precip_hours", 0)
                b["both_precip"] += r.get("both_precip", 0)
                b["fact_only_precip"] += r.get("fact_only_precip", 0)
                b["fcst_only_precip"] += r.get("fcst_only_precip", 0)

    return results


# ============================================================
# ВЫВОД
# ============================================================
def avg(values):
    return round(sum(values) / len(values), 2) if values else None


def _fmt_bias(v):
    if v is None:
        return "—"
    return f"+{v}" if v > 0 else str(v)


def print_report(results, days, lag_days):
    line = "=" * 78
    print("\n" + line)
    print(f"📊 СРАВНЕНИЕ ПРОГНОЗА С ФАКТОМ ЗА {days} ДНЕЙ")
    print(f"   Сдвиг назад: {lag_days} дн. (задержка ERA5)")
    print(f"   Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print(line)

    any_data = False

    for station_key, models in results.items():
        station_name = STATIONS[station_key]["name"]
        print(f"\n📍 {station_name}")
        print("-" * 78)

        # --- Температура ---
        print("🌡  ТЕМПЕРАТУРА (°C)")
        print(f"   {'Модель':<22} {'MAE':>7} {'RMSE':>7} {'Bias':>8} {'Дней':>6}")
        print("   " + "-" * 56)
        for model_key, m in models.items():
            if m["days_count"] == 0:
                continue
            any_data = True
            print(f"   {MODELS[model_key]['name']:<22} "
                  f"{avg(m['temp_mae']) or '—':>7} "
                  f"{avg(m['temp_rmse']) or '—':>7} "
                  f"{_fmt_bias(avg(m['temp_bias'])):>8} "
                  f"{m['days_count']:>6}")

        # --- Осадки ---
        print("\n💧 ОСАДКИ (мм/час)")
        print(f"   {'Модель':<22} {'MAE':>7} {'RMSE':>7} {'Bias':>8}")
        print("   " + "-" * 56)
        for model_key, m in models.items():
            if m["days_count"] == 0:
                continue
            print(f"   {MODELS[model_key]['name']:<22} "
                  f"{avg(m['prec_mae']) or '—':>7} "
                  f"{avg(m['prec_rmse']) or '—':>7} "
                  f"{_fmt_bias(avg(m['prec_bias'])):>8}")

        # --- Явления ---
        print("\n🌧  ЯВЛЕНИЯ — ЧАСЫ С ОСАДКАМИ (>0.05 мм)")
        print(f"   {'Модель':<22} {'Факт':>7} {'Прогноз':>9} {'Совпало':>9} "
              f"{'Пропуск':>9} {'Ложных':>8}")
        print("   " + "-" * 74)
        for model_key, m in models.items():
            if m["days_count"] == 0:
                continue
            print(f"   {MODELS[model_key]['name']:<22} "
                  f"{m['fact_precip_hours']:>7} "
                  f"{m['fcst_precip_hours']:>9} "
                  f"{m['both_precip']:>9} "
                  f"{m['fact_only_precip']:>9} "
                  f"{m['fcst_only_precip']:>8}")

        # --- Итоги ---
        valid = {k: v for k, v in models.items() if v["days_count"] > 0}
        if valid:
            best_t = min(valid.items(),
                         key=lambda kv: avg(kv[1]["temp_mae"]) or 999)
            best_p = min(valid.items(),
                         key=lambda kv: avg(kv[1]["prec_mae"]) or 999)

            print(f"\n  🏆 Температура: {MODELS[best_t[0]]['name']} "
                  f"(MAE = {avg(best_t[1]['temp_mae'])}°C)")
            print(f"  🏆 Осадки:      {MODELS[best_p[0]]['name']} "
                  f"(MAE = {avg(best_p[1]['prec_mae'])} мм)")

            src_total = defaultdict(int)
            for m in models.values():
                for src, cnt in m["sources"].items():
                    src_total[src] += cnt
            if src_total:
                print("  📌 Источник факта: " +
                      ", ".join(f"{k}={v}" for k, v in src_total.items()))

        # --- Ошибки (короткая сводка) ---
        err_set = set()
        for m in models.values():
            for e in m["errors"]:
                # убираем станцию/модель/дату — оставляем только причину
                parts = e.split(" — ", 1)
                if len(parts) == 2:
                    err_set.add(parts[1])
        if err_set:
            print(f"\n  ⚠️  Причины пропусков:")
            for e in sorted(err_set)[:5]:
                print(f"     • {e}")

    if not any_data:
        print("\n⚠️  Ни одной строки с данными!")
        print("    Возможные причины:")
        print("    • ERA5 ещё не подтянул архив за выбранный период")
        print("      → попробуйте: python monthly_stats.py --days 14 --lag 7")
        print("    • Previous Runs API не отдал прогноз за эти даты")
        print("    • Проблемы с сетью / API Open-Meteo")

    print("\n" + line)


# ============================================================
# CSV
# ============================================================
def export_csv(results, path):
    rows = []
    for station_key, models in results.items():
        station_name = STATIONS[station_key]["name"]
        for model_key, m in models.items():
            if m["days_count"] == 0:
                continue
            rows.append({
                "station": station_name,
                "model": MODELS[model_key]["name"],
                "days": m["days_count"],
                "temp_mae": avg(m["temp_mae"]),
                "temp_rmse": avg(m["temp_rmse"]),
                "temp_bias": avg(m["temp_bias"]),
                "prec_mae": avg(m["prec_mae"]),
                "prec_rmse": avg(m["prec_rmse"]),
                "prec_bias": avg(m["prec_bias"]),
                "fact_precip_hours": m["fact_precip_hours"],
                "fcst_precip_hours": m["fcst_precip_hours"],
                "both_precip": m["both_precip"],
                "fact_only_precip": m["fact_only_precip"],
                "fcst_only_precip": m["fcst_only_precip"],
                "avg_hours_per_day": avg(m["hours"]),
                "sources": json.dumps(dict(m["sources"]), ensure_ascii=False),
            })

    if not rows:
        log.warning("Нет данных для экспорта")
        return

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    log.info("CSV сохранён: %s (%d строк)", path, len(rows))


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Сравнение прогноза с фактом")
    parser.add_argument("--days", type=int, default=30,
                        help="Сколько дней назад (по умолчанию 30)")
    parser.add_argument("--station", choices=list(STATIONS.keys()),
                        help="Только одна станция")
    parser.add_argument("--lag", type=int, default=DEFAULT_LAG_DAYS,
                        help=f"Сдвиг назад от сегодня (по умолчанию {DEFAULT_LAG_DAYS})")
    parser.add_argument("--export", type=str, help="Путь для CSV")
    args = parser.parse_args()

    log.info("Сбор статистики: %d дней, сдвиг %d", args.days, args.lag)
    t0 = time.time()

    results = collect_stats(
        days=args.days,
        station_filter=args.station,
        lag_days=args.lag,
    )

    print_report(results, args.days, args.lag)

    if args.export:
        export_csv(results, args.export)

    log.info("Готово за %.1f сек", time.time() - t0)


if __name__ == "__main__":
    main()