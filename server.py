# -*- coding: utf-8 -*-
"""
Сервер прогноза погоды v2 — только маршруты.
Логика вынесена в core/, data/, analysis/, templates.py.
"""

import os
import json
import urllib.parse
from datetime import datetime, timedelta
from collections import OrderedDict

from flask import (
    Flask, jsonify, render_template_string,
    request, send_from_directory, redirect,
)

# ── core ──
from core.config import (
    STATIONS, MODELS, DEFAULT_LOCATION, MAPS_DIR, FORECAST_DAYS,
    MIN_VERIFY_DATE, VERIFY_HISTORY_DAYS, METEOSTAT_AVAILABLE,
    MAX_STATION_DISTANCE_KM, log,
)
from core.cache import _forecast_cache, _verify_cache
from core.dictionaries import CODE_TO_TEXT
from core.utils import code_to_text, wind_dir_text
from core.http import _session

# ── data ──
from data.forecast import fetch_forecast, fetch_previous_run
from data.current import fetch_current
from data.actual import fetch_actual, check_station_availability

# ── analysis ──
from analysis.parsing import parse_hourly, prepare_forecast_for_render
from analysis.synoptic import analyze_synoptic
from analysis.text_forecast import generate_text_forecast
from analysis.verify import verify_model, verify_model_noaa, verify_history
from analysis.statistics import analyze_period

# ── внешние ──
from aviation_verify import (
    PHENOMENA, build_contingency, build_inertial_contingency,
    build_random_contingency, build_climatological_contingency,
    build_climate_norm, evaluate_all,
    build_daily_contingency_noaa, build_inertial_contingency_noaa,
    _phenomenon_present,
)
from noaa_client import (
    find_nearest_stations, get_actuals, find_and_get_actuals,
    get_actuals_range, find_station_with_data,
)

# ── шаблоны ──
from templates import (
    INDEX_HTML, ABOUT_HTML, MODEL_HTML,
    TABLE_TEMPLATE, TEXT_TEMPLATE, SEARCH_HTML, POINT_TEMPLATE,
    VERIFY_HTML, VERIFY_HISTORY_HTML, ANALYZE_HTML, AVIATION_HTML,
    ALT_VERIFY_HTML, COMPARE_MATRICES_HTML, TEACHING_HTML,
    CHART_HTML, COMPARE_HTML, MAP_HTML, NOAA_HTML,
)


app = Flask(__name__)


# ============================================================
# ГЛАВНАЯ И СЛУЖЕБНЫЕ
# ============================================================
@app.route("/")
def index():
    return render_template_string(INDEX_HTML, models=MODELS)


@app.route("/healthz")
def healthz():
    return jsonify({
        "status": "ok",
        "version": "2.0",
        "time": datetime.now().isoformat() + "Z",
        "cache_ttl_sec": _forecast_cache.ttl,
        "stations": list(STATIONS.keys()),
        "models": list(MODELS.keys()),
        "maps_dir_exists": os.path.isdir(MAPS_DIR),
        "meteostat_available": METEOSTAT_AVAILABLE,
        "max_station_distance_km": MAX_STATION_DISTANCE_KM,
        "verify_history_days": VERIFY_HISTORY_DAYS,
        "phenomena": list(PHENOMENA.keys()),
    })


@app.route("/about")
def about_page():
    return render_template_string(ABOUT_HTML)


@app.route("/teaching")
def teaching_page():
    return render_template_string(TEACHING_HTML)


@app.route("/maps/<path:filename>")
def serve_map(filename):
    if not os.path.isdir(MAPS_DIR):
        return f"Папка '{MAPS_DIR}' не найдена.", 404
    return send_from_directory(MAPS_DIR, filename)


# ============================================================
# NOAA
# ============================================================
@app.route("/api/noaa/nearby")
def noaa_nearby():
    try:
        lat = float(request.args.get("lat", 55.85))
        lon = float(request.args.get("lon", 37.44))
        radius = float(request.args.get("radius", 50))
    except ValueError:
        return jsonify({"error": "Некорректные параметры lat/lon/radius"}), 400
    stations = find_nearest_stations(lat, lon, radius_km=radius, limit=10)
    return jsonify({
        "center": {"lat": lat, "lon": lon},
        "radius_km": radius,
        "count": len(stations),
        "stations": stations,
    })


@app.route("/api/noaa/actuals")
def noaa_actuals():
    try:
        lat = float(request.args.get("lat", 55.85))
        lon = float(request.args.get("lon", 37.44))
        days = int(request.args.get("days", 7))
        radius = float(request.args.get("radius", 50))
    except ValueError:
        return jsonify({"error": "Некорректные параметры"}), 400
    station, data = find_and_get_actuals(lat, lon, radius_km=radius, days=days)
    if station is None:
        return jsonify({"error": "Станции не найдены"}), 404
    return jsonify({"station": station, "days": days, "data": data})


@app.route("/api/noaa/historical")
def noaa_historical():
    try:
        lat = float(request.args.get("lat", 55.85))
        lon = float(request.args.get("lon", 37.44))
        start = request.args.get("start")
        end = request.args.get("end")
        radius = float(request.args.get("radius", 100))

        if not start or not end:
            return jsonify({"error": "Укажите параметры start и end (YYYY-MM-DD)"}), 400

        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()

        if start_date > end_date:
            return jsonify({"error": "Дата начала позже даты конца"}), 400

    except ValueError:
        return jsonify({"error": "Неверный формат даты или координат"}), 400

    station, data = find_station_with_data(
        lat, lon, start_date, end_date, radius_km=radius
    )

    if station is None:
        return jsonify({
            "error": "Нет станций NOAA с данными за этот период",
            "hint": "Попробуйте период 2020–2022 или увеличьте радиус поиска",
        }), 404

    return jsonify({
        "station": station,
        "period": {"start": start, "end": end},
        "data": data,
    })


@app.route("/noaa")
def noaa_page():
    return render_template_string(NOAA_HTML)


# ============================================================
# ТЕКУЩАЯ ПОГОДА И ГЕОКОДЕР
# ============================================================
@app.route("/api/current")
def api_current():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    if lat is None or lon is None:
        lat = DEFAULT_LOCATION["lat"]
        lon = DEFAULT_LOCATION["lon"]
    try:
        return jsonify(fetch_current(lat, lon))
    except Exception as e:
        log.exception("api_current error")
        return jsonify({"error": str(e)}), 500


@app.route("/api/geocode")
def api_geocode():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "Пустой запрос"}), 400
    try:
        url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={urllib.parse.quote(q)}"
            "&count=5&language=ru&format=json"
        )
        r = _session.get(url, timeout=10)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        log.exception("api_geocode error")
        return jsonify({"error": str(e)}), 500


# ============================================================
# ПРОГНОЗЫ
# ============================================================
@app.route("/model/<model>")
def model_page(model):
    if model not in MODELS:
        return f"Модель '{model}' не найдена.", 404
    return render_template_string(
        MODEL_HTML, model=model, model_name=MODELS[model]["name"],
        stations=STATIONS, first_station=list(STATIONS.keys())[0],
    )


@app.route("/forecast/<model>/<station>")
def forecast_table(model, station):
    if model not in MODELS:
        return f"Модель '{model}' не найдена.", 404
    if station not in STATIONS:
        return f"Станция '{station}' не найдена.", 404
    info = STATIONS[station]
    try:
        data = fetch_forecast(model, info["lat"], info["lon"])
        forecast = parse_hourly(data)
        by_day = prepare_forecast_for_render(forecast)
        synoptic = analyze_synoptic(forecast)
        return render_template_string(
            TABLE_TEMPLATE,
            station=info["name"], station_key=station,
            model=model, model_name=MODELS[model]["name"],
            lat=info["lat"], lon=info["lon"],
            days=FORECAST_DAYS, by_day=by_day, view="table",
            synoptic=synoptic,
            updated=datetime.now().strftime("%d.%m.%Y %H:%M"),
        )
    except Exception as e:
        log.exception("forecast_table error")
        return f"Ошибка: {e}", 500


@app.route("/text/<model>/<station>")
def text_forecast(model, station):
    if model not in MODELS:
        return f"Модель '{model}' не найдена.", 404
    if station not in STATIONS:
        return f"Станция '{station}' не найдена.", 404
    info = STATIONS[station]
    try:
        data = fetch_forecast(model, info["lat"], info["lon"])
        forecast = parse_hourly(data)
        for h in forecast:
            h["code_text"] = code_to_text(h["weather_code"])
            h["wind_dir_text"] = wind_dir_text(h["wind_dir"])
        text = generate_text_forecast(MODELS[model]["name"], info["name"], forecast)
        synoptic = analyze_synoptic(forecast)
        return render_template_string(
            TEXT_TEMPLATE,
            station=info["name"], station_key=station,
            model=model, model_name=MODELS[model]["name"],
            lat=info["lat"], lon=info["lon"],
            days=FORECAST_DAYS, text=text, view="text",
            synoptic=synoptic,
        )
    except Exception as e:
        log.exception("text_forecast error")
        return f"Ошибка: {e}", 500


@app.route("/search")
def search_page():
    return render_template_string(SEARCH_HTML, models=MODELS)


@app.route("/forecast/point")
def forecast_point():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    name = request.args.get("name", "Точка")
    model = request.args.get("model", "gfs")
    view = request.args.get("view", "table")
    if lat is None or lon is None:
        return "Не указаны координаты. Вернитесь на /search.", 400
    if model not in MODELS:
        model = "gfs"
    try:
        data = fetch_forecast(model, lat, lon)
        forecast = parse_hourly(data)
        by_day = prepare_forecast_for_render(forecast)
        text = generate_text_forecast(MODELS[model]["name"], name, forecast)
        synoptic = analyze_synoptic(forecast)
        labels = [h["time"][5:16].replace("T", " ") for h in forecast]
        chart_data = {
            "temp":     [h["temp_c"] for h in forecast],
            "theta":    [h["theta_k"] for h in forecast],
            "wind":     [h["wind_ms"] for h in forecast],
            "precip":   [h["precipitation_mm"] for h in forecast],
            "pressure": [h["pressure_hpa"] for h in forecast],
        }
        return render_template_string(
            POINT_TEMPLATE,
            point_name=name, lat=lat, lon=lon,
            model=model, model_name=MODELS[model]["name"],
            view=view, by_day=by_day, text=text, synoptic=synoptic,
            labels_json=json.dumps(labels, ensure_ascii=False),
            data_json=json.dumps(chart_data, ensure_ascii=False),
        )
    except Exception as e:
        log.exception("forecast_point error")
        return f"Ошибка: {e}", 500


# ============================================================
# ВЕРИФИКАЦИЯ
# ============================================================
@app.route("/verify/<station>")
def verify_page(station):
    if station not in STATIONS:
        return f"Станция '{station}' не найдена", 404
    default_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    return render_template_string(
        VERIFY_HTML,
        station_key=station,
        station_name=STATIONS[station]["name"],
        default_date=default_date,
        min_date=MIN_VERIFY_DATE,
        history_days=VERIFY_HISTORY_DAYS,
    )


@app.route("/api/verify/<station>")
def verify_api(station):
    if station not in STATIONS:
        return jsonify({"error": f"Станция '{station}' не найдена"}), 404
    info = STATIONS[station]
    source = request.args.get("source", "default")

    date_param = request.args.get("date")
    if date_param:
        try:
            datetime.strptime(date_param, "%Y-%m-%d")
            target_date = date_param
        except ValueError:
            return jsonify({"error": "Неверный формат даты. YYYY-MM-DD"}), 400
    else:
        target_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    if source == "noaa":
        results = [verify_model_noaa(k, info["lat"], info["lon"], target_date)
                   for k in MODELS.keys()]
    else:
        results = [verify_model(k, info["lat"], info["lon"], target_date)
                   for k in MODELS.keys()]

    return jsonify({
        "station": info["name"],
        "date": target_date,
        "source": source,
        "results": results,
    })


@app.route("/verify/<station>/history")
def verify_history_page(station):
    if station not in STATIONS:
        return f"Станция '{station}' не найдена", 404
    return render_template_string(
        VERIFY_HISTORY_HTML,
        station_key=station,
        station_name=STATIONS[station]["name"],
        history_days=VERIFY_HISTORY_DAYS,
    )


@app.route("/api/verify/<station>/history")
def verify_history_api(station):
    if station not in STATIONS:
        return jsonify({"error": f"Станция '{station}' не найдена"}), 404
    try:
        days = int(request.args.get("days", VERIFY_HISTORY_DAYS))
        days = max(1, min(days, 14))
    except ValueError:
        days = VERIFY_HISTORY_DAYS
    info = STATIONS[station]
    raw = verify_history(info["lat"], info["lon"], days)
    series = {k: {"mae": [], "bias": []} for k in MODELS.keys()}
    for day in raw:
        for model_key in MODELS.keys():
            r = day["models"].get(model_key, {})
            series[model_key]["mae"].append(r.get("temp_mae"))
            series[model_key]["bias"].append(r.get("temp_bias"))
    return jsonify({
        "station": info["name"],
        "days": raw,
        "models": {k: v["name"] for k, v in MODELS.items()},
        "series": series,
    })


# ============================================================
# АНАЛИЗ
# ============================================================
@app.route("/analyze/<station>")
def analyze_page(station):
    if station not in STATIONS:
        return f"Станция '{station}' не найдена", 404
    return render_template_string(
        ANALYZE_HTML,
        station_key=station,
        station_name=STATIONS[station]["name"],
        models=MODELS,
    )


@app.route("/api/analyze/<station>")
def analyze_api(station):
    if station not in STATIONS:
        return jsonify({"error": f"Станция '{station}' не найдена"}), 404
    model = request.args.get("model", "gfs")
    if model not in MODELS:
        return jsonify({"error": f"Модель '{model}' не найдена"}), 400
    try:
        days = int(request.args.get("days", 14))
        days = max(3, min(days, 30))
    except ValueError:
        days = 14
    info = STATIONS[station]
    result = analyze_period(model, info["lat"], info["lon"], days)
    result["station"] = info["name"]
    return jsonify(result)


# ============================================================
# АВИАЦИЯ
# ============================================================
@app.route("/aviation/<model>/<station>")
def aviation_page(model, station):
    if model not in MODELS:
        return f"Модель '{model}' не найдена.", 404
    if station not in STATIONS:
        return f"Станция '{station}' не найдена.", 404
    return render_template_string(
        AVIATION_HTML,
        station_key=station,
        station_name=STATIONS[station]["name"],
        models=MODELS,
    )


@app.route("/api/aviation/<model>/<station>")
def aviation_api(model, station):
    if model not in MODELS:
        return jsonify({"error": f"Модель '{model}' не найдена"}), 404
    if station not in STATIONS:
        return jsonify({"error": f"Станция '{station}' не найдена"}), 404
    info = STATIONS[station]
    try:
        data = fetch_forecast(model, info["lat"], info["lon"])
        forecast = parse_hourly(data)
    except Exception as e:
        log.exception("aviation_api error")
        return jsonify({"error": str(e)}), 500

    hourly = data.get("hourly", {})
    t500  = hourly.get("temperature_500hPa", [])
    t700  = hourly.get("temperature_700hPa", [])
    td700 = hourly.get("dew_point_700hPa", [])
    t850  = hourly.get("temperature_850hPa", [])
    td850 = hourly.get("dew_point_850hPa", [])

    hours_out = []
    for i, h in enumerate(forecast):
        hours_out.append({
            "time": h["time"][5:16].replace("T", " "),
            "t850":  t850[i] if i < len(t850) else None,
            "td850": td850[i] if i < len(td850) else None,
            "t700":  t700[i] if i < len(t700) else None,
            "td700": td700[i] if i < len(td700) else None,
            "t500":  t500[i] if i < len(t500) else None,
            "av_thunder": h.get("av_thunder", {}),
            "av_fog":     h.get("av_fog", {}),
        })

    by_day = OrderedDict()
    for h in hours_out:
        day = h["time"][:5]
        by_day.setdefault(day, []).append(h)

    days_summary = []
    for day, hours in by_day.items():
        ks    = [h["av_thunder"].get("k") for h in hours if h["av_thunder"].get("k") is not None]
        lis   = [h["av_thunder"].get("li") for h in hours if h["av_thunder"].get("li") is not None]
        capes = [h["av_thunder"].get("cape") for h in hours if h["av_thunder"].get("cape") is not None]
        thunder_count = sum(1 for h in hours if h["av_thunder"].get("combined_prob", 0) >= 40)
        fog_count     = sum(1 for h in hours if h["av_fog"].get("probability", 0) >= 40)
        days_summary.append({
            "date": day,
            "thunder_count": thunder_count,
            "fog_count": fog_count,
            "max_k": round(max(ks), 1) if ks else None,
            "min_li": round(min(lis), 1) if lis else None,
            "max_cape": round(max(capes)) if capes else None,
        })

    return jsonify({
        "station": info["name"],
        "model": model,
        "model_name": MODELS[model]["name"],
        "hours": hours_out,
        "days_summary": days_summary,
    })


# ============================================================
# МАТРИЦЫ
# ============================================================
@app.route("/alt-verify/<station>")
def alt_verify_page_station(station):
    if station not in STATIONS:
        return f"Станция '{station}' не найдена", 404
    info = STATIONS[station]
    today = datetime.now().date()
    return render_template_string(
        ALT_VERIFY_HTML,
        station_key=station, title=info["name"],
        lat=info["lat"], lon=info["lon"],
        phenomena=PHENOMENA, models=MODELS, phenomenon="rain",
        start_date=(today - timedelta(days=14)).isoformat(),
        end_date=(today - timedelta(days=1)).isoformat(),
    )


@app.route("/alt-verify")
def alt_verify_page_point():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    name = request.args.get("name", "Точка")
    if lat is None or lon is None:
        return redirect("/search")
    today = datetime.now().date()
    return render_template_string(
        ALT_VERIFY_HTML,
        station_key="", title=name, lat=lat, lon=lon,
        phenomena=PHENOMENA, models=MODELS, phenomenon="rain",
        start_date=(today - timedelta(days=14)).isoformat(),
        end_date=(today - timedelta(days=1)).isoformat(),
    )


@app.route("/api/alt-verify")
def alt_verify_api():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    phenomenon = request.args.get("phenomenon", "rain")
    model = request.args.get("model", "gfs")
    start_param = request.args.get("start")
    end_param = request.args.get("end")
    days = request.args.get("days", 14, type=int)
    force_station = request.args.get("force_station", "0") == "1"

    if lat is None or lon is None:
        return jsonify({"error": "Не указаны координаты"}), 400
    if phenomenon not in PHENOMENA:
        return jsonify({"error": f"Явление '{phenomenon}' не поддерживается"}), 400
    if model not in MODELS:
        return jsonify({"error": f"Модель '{model}' не найдена"}), 400

    if start_param and end_param:
        try:
            d_start = datetime.strptime(start_param, "%Y-%m-%d").date()
            d_end = datetime.strptime(end_param, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Неверный формат даты. YYYY-MM-DD"}), 400
        if d_start > d_end:
            return jsonify({"error": "Дата начала позже даты конца"}), 400
        if (d_end - d_start).days > 90:
            return jsonify({"error": "Слишком большой период (макс. 90 дней)"}), 400
    else:
        d_end = datetime.now().date() - timedelta(days=1)
        d_start = d_end - timedelta(days=days - 1)

    station_info = check_station_availability(lat, lon, force=force_station)

    # ── Климатологическая норма за 5 лет ──
    current_year = datetime.now().year
    years_to_collect = list(range(current_year - 5, current_year))

    needed_days = set()
    d_iter = d_start
    while d_iter <= d_end:
        needed_days.add((d_iter.month, d_iter.day))
        d_iter += timedelta(days=1)

    fact_hours_by_year = {}
    climate_cache_key = ("climate", round(lat, 3), round(lon, 3),
                         phenomenon, tuple(sorted(needed_days)))
    cached_climate = _verify_cache.get(climate_cache_key)
    if cached_climate is not None:
        norm_map = cached_climate
    else:
        for year in years_to_collect:
            year_hours = []
            for (month, day) in needed_days:
                try:
                    target = datetime(year, month, day).date()
                except ValueError:
                    continue
                if target > datetime.now().date():
                    continue
                date_str = target.isoformat()
                if date_str < MIN_VERIFY_DATE:
                    continue
                try:
                    fact, _ = fetch_actual(lat, lon, date_str)
                except Exception:
                    continue
                fh = fact.get("hourly", {})
                f_times = fh.get("time", [])
                f_temp = fh.get("temperature_2m", [None] * len(f_times))
                f_prec = fh.get("precipitation", [0] * len(f_times))
                f_code = fh.get("weather_code", [None] * len(f_times))
                f_wind = fh.get("wind_speed_10m", [None] * len(f_times))
                for i, t in enumerate(f_times):
                    wv = f_wind[i] if i < len(f_wind) else None
                    year_hours.append({
                        "time": t,
                        "temp_c": f_temp[i] if i < len(f_temp) else None,
                        "precipitation_mm": f_prec[i] if i < len(f_prec) else 0,
                        "weather_code": f_code[i] if i < len(f_code) else None,
                        "wind_ms": wv / 3.6 if wv is not None else None,
                    })
            if year_hours:
                fact_hours_by_year[year] = year_hours
        norm_map = build_climate_norm(fact_hours_by_year, phenomenon, years=5)
        _verify_cache.set(climate_cache_key, norm_map)
        log.info("climate: norm_map построена для %d лет, %d ключей",
                 len(fact_hours_by_year), len(norm_map))

    # Сбор данных за выбранный период
    fact_hours = []
    fcst_hours = []
    dates_used = 0
    sources_used = {}

    d = d_start
    while d <= d_end:
        date_str = d.strftime("%Y-%m-%d")
        if date_str < MIN_VERIFY_DATE:
            d += timedelta(days=1)
            continue
        try:
            fact, fact_source = fetch_actual(
                lat, lon, date_str, force_station=force_station
            )
            fcst = fetch_previous_run(model, lat, lon, date_str)
        except Exception as e:
            log.warning("alt_verify: %s / %s — %s", date_str, phenomenon, e)
            d += timedelta(days=1)
            continue

        src_key = "ERA5" if fact_source == "ERA5" else fact_source
        sources_used[src_key] = sources_used.get(src_key, 0) + 1

        fh = fact.get("hourly", {})
        ph = fcst.get("hourly", {})

        f_times = fh.get("time", [])
        p_times = ph.get("time", [])

        f_temp = fh.get("temperature_2m", [None] * len(f_times))
        f_prec = fh.get("precipitation", [0] * len(f_times))
        f_code = fh.get("weather_code", [None] * len(f_times))
        f_wind = fh.get("wind_speed_10m", [None] * len(f_times))

        p_temp = ph.get("temperature_2m_previous_day1", [None] * len(p_times))
        p_prec = ph.get("precipitation", [0] * len(p_times))
        p_code = ph.get("weather_code_previous_day1", [None] * len(p_times))
        p_wind = ph.get("wind_speed_10m_previous_day1", [None] * len(p_times))

        for i, t in enumerate(f_times):
            wind_val = f_wind[i] if i < len(f_wind) else None
            wind_ms = wind_val / 3.6 if wind_val is not None else None
            fact_hours.append({
                "time": t,
                "temp_c": f_temp[i] if i < len(f_temp) else None,
                "precipitation_mm": f_prec[i] if i < len(f_prec) else 0,
                "weather_code": f_code[i] if i < len(f_code) else None,
                "wind_ms": wind_ms,
            })

        for i, t in enumerate(p_times):
            wind_val = p_wind[i] if i < len(p_wind) else None
            wind_ms = wind_val / 3.6 if wind_val is not None else None
            fcst_hours.append({
                "time": t,
                "temp_c": p_temp[i] if i < len(p_temp) else None,
                "precipitation_mm": p_prec[i] if i < len(p_prec) else 0,
                "weather_code": p_code[i] if i < len(p_code) else None,
                "wind_ms": wind_ms,
            })

        dates_used += 1
        d += timedelta(days=1)

    if not fact_hours or not fcst_hours:
        return jsonify({"error": "Нет данных за выбранный период"})

    m_method = build_contingency(fact_hours, fcst_hours, phenomenon)
    m_inertial = build_inertial_contingency(fact_hours, phenomenon)
    m_random = build_random_contingency(fact_hours, phenomenon)
    m_climat = build_climatological_contingency(
        fact_hours, phenomenon, norm_map=norm_map, threshold=0.5
    )
    ev = evaluate_all(m_method, m_inertial, m_random, m_climat)

    return jsonify({
        "phenomenon": phenomenon,
        "phenomenon_name": PHENOMENA[phenomenon]["name"],
        "model": model,
        "model_name": MODELS[model]["name"],
        "start": d_start.isoformat(),
        "end": d_end.isoformat(),
        "dates_used": dates_used,
        "hours_total": len(fact_hours),
        "station": station_info,
        "sources_used": sources_used,
        "force_station": force_station,
        "methodical": ev,
        "inertial": ev.get("inertial"),
        "random": ev.get("random"),
        "climatological": ev.get("climatological"),
        "climate_years": len(fact_hours_by_year),
        "S_haidke": ev.get("S_haidke"),
    })


@app.route("/api/alt-verify-noaa")
def alt_verify_noaa_api():
    """
    Матрица альтернативных прогнозов на исторических данных NOAA (суточные).
    """
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    phenomenon = request.args.get("phenomenon", "rain")
    model = request.args.get("model", "gfs")
    start_param = request.args.get("start")
    end_param = request.args.get("end")

    if lat is None or lon is None:
        return jsonify({"error": "Не указаны координаты"}), 400
    if phenomenon not in PHENOMENA:
        return jsonify({"error": f"Явление '{phenomenon}' не поддерживается"}), 400
    if model not in MODELS:
        return jsonify({"error": f"Модель '{model}' не найдена"}), 400
    if not (start_param and end_param):
        return jsonify({"error": "Укажите start и end"}), 400

    try:
        d_start = datetime.strptime(start_param, "%Y-%m-%d").date()
        d_end = datetime.strptime(end_param, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Неверный формат даты"}), 400
    if d_start > d_end:
        return jsonify({"error": "Дата начала позже даты конца"}), 400
    if (d_end - d_start).days > 180:
        return jsonify({"error": "Максимум 180 дней"}), 400

    station, noaa_data = find_station_with_data(
        lat, lon, d_start, d_end, radius_km=200
    )
    if station is None:
        return jsonify({
            "error": "Нет станции NOAA с данными за этот период",
            "hint": "Для Москвы данные доступны до 2022-01-15",
        }), 404

    by_date = {}
    for r in noaa_data.get("results", []):
        d = r["date"][:10]
        by_date.setdefault(d, {})[r["datatype"]] = r["value"]

    fact_daily = []
    for d in sorted(by_date.keys()):
        day = by_date[d]
        fact_daily.append({
            "date": d,
            "tmax": day.get("TMAX"),
            "tmin": day.get("TMIN"),
            "prcp": day.get("PRCP", 0) or 0,
        })

    if not fact_daily:
        return jsonify({"error": "Нет данных NOAA"}), 404

    # Собираем прогноз модели и агрегируем по дням
    fcst_daily = []
    for day in fact_daily:
        date_str = day["date"]
        try:
            fcst = fetch_previous_run(model, lat, lon, date_str)
        except Exception:
            continue
        fh = fcst.get("hourly", {})
        f_times = fh.get("time", [])
        f_temp = fh.get("temperature_2m_previous_day1", [])
        f_prec = fh.get("precipitation", [])
        day_temps, day_precs = [], []
        for i, t in enumerate(f_times):
            if t.startswith(date_str):
                if i < len(f_temp) and f_temp[i] is not None:
                    day_temps.append(f_temp[i])
                if i < len(f_prec) and f_prec[i] is not None:
                    day_precs.append(f_prec[i])
        if not day_temps:
            continue
        fcst_daily.append({
            "date": date_str,
            "tmax": max(day_temps),
            "tmin": min(day_temps),
            "prcp": sum(day_precs),
        })

    if not fcst_daily:
        return jsonify({"error": "Нет прогнозов за этот период"}), 404

    m = build_daily_contingency_noaa(fact_daily, fcst_daily, phenomenon)
    m_inertial = build_inertial_contingency_noaa(fact_daily, phenomenon)
    ev = evaluate_all(m, m_inertial)

    return jsonify({
        "phenomenon": phenomenon,
        "phenomenon_name": PHENOMENA[phenomenon]["name"],
        "model": model,
        "model_name": MODELS[model]["name"],
        "start": d_start.isoformat(),
        "end": d_end.isoformat(),
        "station": station,
        "days_fact": len(fact_daily),
        "days_fcst": len(fcst_daily),
        "methodical": m,
        "inertial": m_inertial,
        "evaluation": ev,
    })


@app.route("/compare-matrices/<station>")
def compare_matrices_page(station):
    if station not in STATIONS:
        return f"Станция '{station}' не найдена", 404
    info = STATIONS[station]
    today = datetime.now().date()
    return render_template_string(
        COMPARE_MATRICES_HTML,
        station_key=station, station_name=info["name"],
        lat=info["lat"], lon=info["lon"],
        phenomena=PHENOMENA, phenomenon="rain",
        start_date=(today - timedelta(days=14)).isoformat(),
        end_date=(today - timedelta(days=1)).isoformat(),
    )


@app.route("/api/compare-matrices")
def compare_matrices_api():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    phenomenon = request.args.get("phenomenon", "rain")
    start_param = request.args.get("start")
    end_param = request.args.get("end")

    if lat is None or lon is None:
        return jsonify({"error": "Не указаны координаты"}), 400
    if phenomenon not in PHENOMENA:
        return jsonify({"error": f"Явление '{phenomenon}' не поддерживается"}), 400
    if not (start_param and end_param):
        return jsonify({"error": "Укажите start и end"}), 400

    try:
        d_start = datetime.strptime(start_param, "%Y-%m-%d").date()
        d_end = datetime.strptime(end_param, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Неверный формат даты"}), 400
    if d_start > d_end:
        return jsonify({"error": "Дата начала позже даты конца"}), 400
    if (d_end - d_start).days > 30:
        return jsonify({"error": "Максимум 30 дней"}), 400

    # Собираем факт один раз
    fact_hours = []
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
            log.warning("compare-matrices: %s — %s", date_str, e)
            d += timedelta(days=1)
            continue

        fh = fact.get("hourly", {})
        f_times = fh.get("time", [])
        f_temp = fh.get("temperature_2m", [None] * len(f_times))
        f_prec = fh.get("precipitation", [0] * len(f_times))
        f_code = fh.get("weather_code", [None] * len(f_times))
        f_wind = fh.get("wind_speed_10m", [None] * len(f_times))

        for i, t in enumerate(f_times):
            wind_val = f_wind[i] if i < len(f_wind) else None
            wind_ms = wind_val / 3.6 if wind_val is not None else None
            fact_hours.append({
                "time": t,
                "temp_c": f_temp[i] if i < len(f_temp) else None,
                "precipitation_mm": f_prec[i] if i < len(f_prec) else 0,
                "weather_code": f_code[i] if i < len(f_code) else None,
                "wind_ms": wind_ms,
            })
        dates_used += 1
        d += timedelta(days=1)

    if not fact_hours:
        return jsonify({"error": "Нет данных за выбранный период"}), 400

    models_data = {}
    for model_key in MODELS.keys():
        fcst_hours = []
        d = d_start
        while d <= d_end:
            date_str = d.strftime("%Y-%m-%d")
            if date_str < MIN_VERIFY_DATE:
                d += timedelta(days=1)
                continue
            try:
                fcst = fetch_previous_run(model_key, lat, lon, date_str)
            except Exception:
                d += timedelta(days=1)
                continue

            ph = fcst.get("hourly", {})
            p_times = ph.get("time", [])
            p_temp = ph.get("temperature_2m_previous_day1", [None] * len(p_times))
            p_prec = ph.get("precipitation", [0] * len(p_times))
            p_code = ph.get("weather_code_previous_day1", [None] * len(p_times))
            p_wind = ph.get("wind_speed_10m_previous_day1", [None] * len(p_times))

            for i, t in enumerate(p_times):
                wind_val = p_wind[i] if i < len(p_wind) else None
                wind_ms = wind_val / 3.6 if wind_val is not None else None
                fcst_hours.append({
                    "time": t,
                    "temp_c": p_temp[i] if i < len(p_temp) else None,
                    "precipitation_mm": p_prec[i] if i < len(p_prec) else 0,
                    "weather_code": p_code[i] if i < len(p_code) else None,
                    "wind_ms": wind_ms,
                })
            d += timedelta(days=1)

        m = build_contingency(fact_hours, fcst_hours, phenomenon)
        m_inertial = build_inertial_contingency(fact_hours, phenomenon)
        ev = evaluate_all(m, m_inertial)

        models_data[model_key] = {
            "name": MODELS[model_key]["name"],
            "contingency": m,
            "p": ev.get("p"),
            "H": ev.get("H"),
            "Q": ev.get("Q"),
            "v": ev.get("v"),
            "tau": ev.get("tau"),
            "A": ev.get("A"),
            "S_haidke": ev.get("S_haidke"),
        }

    return jsonify({
        "phenomenon": phenomenon,
        "phenomenon_name": PHENOMENA[phenomenon]["name"],
        "start": d_start.isoformat(),
        "end": d_end.isoformat(),
        "dates_used": dates_used,
        "hours_total": len(fact_hours),
        "models": models_data,
    })


# ============================================================
# ГРАФИКИ И СРАВНЕНИЯ
# ============================================================
@app.route("/chart/<station>")
def chart_compare(station):
    if station not in STATIONS:
        return f"Станция '{station}' не найдена.", 404
    info = STATIONS[station]
    series = OrderedDict()
    labels_ref = None
    for model_key, model_info in MODELS.items():
        try:
            data = fetch_forecast(model_key, info["lat"], info["lon"])
            forecast = parse_hourly(data)
            if labels_ref is None:
                labels_ref = [h["time"][5:16].replace("T", " ") for h in forecast]
            series[model_key] = {
                "name": model_info["name"],
                "temp":     [h["temp_c"] for h in forecast],
                "theta":    [h["theta_k"] for h in forecast],
                "wind":     [h["wind_ms"] for h in forecast],
                "precip":   [h["precipitation_mm"] for h in forecast],
                "pressure": [h["pressure_hpa"] for h in forecast],
            }
        except Exception as e:
            log.warning("chart_compare: %s — %s", model_key, e)
            series[model_key] = {"name": model_info["name"],
                                 "temp": [], "theta": [], "wind": [],
                                 "precip": [], "pressure": []}
    if labels_ref is None:
        labels_ref = []
    return render_template_string(
        CHART_HTML,
        station_name=info["name"], station_key=station,
        lat=info["lat"], lon=info["lon"], days=FORECAST_DAYS,
        labels_json=json.dumps(labels_ref, ensure_ascii=False),
        series_json=json.dumps(series, ensure_ascii=False),
    )


@app.route("/compare/<station>")
def compare_models(station):
    if station not in STATIONS:
        return f"Станция '{station}' не найдена", 404
    info = STATIONS[station]
    rows = []
    for model_key, model_info in MODELS.items():
        try:
            data = fetch_forecast(model_key, info["lat"], info["lon"])
            forecast = parse_hourly(data)
            rows.append({
                "name": model_info["name"],
                "fog": len([x for x in forecast if x["is_fog"]]),
                "thunder": len([x for x in forecast if x["is_thunder"]]),
                "precip": len([x for x in forecast if x["is_precip"]]),
            })
        except Exception:
            rows.append({"name": model_info["name"], "fog": "—", "thunder": "—", "precip": "—"})
    return render_template_string(
        COMPARE_HTML, first_model=list(MODELS.keys())[0],
        station_name=info["name"], rows=rows, days=FORECAST_DAYS,
        updated=datetime.now().strftime("%d.%m.%Y %H:%M"),
    )


@app.route("/map")
def map_page():
    return render_template_string(
        MAP_HTML,
        stations_json=json.dumps(STATIONS, ensure_ascii=False),
        code_to_text_json=json.dumps(CODE_TO_TEXT, ensure_ascii=False),
    )


@app.route("/api/<model>/<station>")
def forecast_api(model, station):
    if model not in MODELS:
        return jsonify({"error": f"Модель '{model}' не найдена"}), 404
    if station not in STATIONS:
        return jsonify({"error": f"Станция '{station}' не найдена"}), 404
    info = STATIONS[station]
    try:
        data = fetch_forecast(model, info["lat"], info["lon"])
        forecast = parse_hourly(data)
        synoptic = analyze_synoptic(forecast)
        day_filter = request.args.get("day")
        if day_filter:
            forecast = [x for x in forecast if x["time"].startswith(day_filter)]
        return jsonify({
            "model": model, "station": info["name"],
            "day_filter": day_filter,
            "fog_hours_count": len([x for x in forecast if x["is_fog"]]),
            "thunder_hours_count": len([x for x in forecast if x["is_thunder"]]),
            "precip_hours_count": len([x for x in forecast if x["is_precip"]]),
            "synoptic": synoptic,
            "forecast": forecast,
        })
    except Exception as e:
        log.exception("forecast_api error")
        return jsonify({"error": str(e)}), 500


# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    log.info("Старт сервера v2 на порту %s (debug=%s)", port, debug)
    app.run(host="0.0.0.0", port=port, debug=debug)