# -*- coding: utf-8 -*-
"""
Flask-приложение weather-msk.
Маршруты и API. Шаблоны берутся из templates.py.
"""

import json
from datetime import date, timedelta

from flask import Flask, render_template_string, request, jsonify

from templates import (
    INDEX_HTML, MAP_HTML, ABOUT_HTML,
    FORECAST_HUB_HTML, ANALYSIS_HUB_HTML, THEORY_HUB_HTML,
    TROPOPAUSE_HTML, TEACHING_HTML,
    VERIFY_HTML, VERIFY_HISTORY_HTML, ANALYZE_HTML,
    AVIATION_HTML, ALT_VERIFY_HTML, COMPARE_MATRICES_HTML,
    CHART_HTML, COMPARE_HTML, MODEL_HTML,
    TABLE_TEMPLATE, TEXT_TEMPLATE, SEARCH_HTML, POINT_TEMPLATE,
    build_current_card_js,
)
from core.dictionaries import CODE_TO_TEXT
from core.config import DEFAULT_LOCATION

app = Flask(__name__)

# ------------------------------------------------------------------
# Конфигурация станций (пример — подставь свои)
# ------------------------------------------------------------------
STATIONS = {
    "tushino": {"name": "Тушино",   "lat": 55.85, "lon": 37.44, "key": "tushino"},
    "ufa":     {"name": "Уфа",      "lat": 54.74, "lon": 55.97, "key": "ufa"},
    "murmansk":{"name": "Мурманск", "lat": 68.96, "lon": 33.08, "key": "murmansk"},
}

MODELS = {
    "gfs":   {"name": "GFS (США)"},
    "ecmwf": {"name": "ECMWF (Европа)"},
    "icon":  {"name": "ICON (Германия)"},
}

PHENOMENA = {
    "frost":   {"name": "Заморозок",      "unit": "°C"},
    "wind":    {"name": "Сильный ветер",  "unit": "м/с"},
    "rain":    {"name": "Сильный дождь",  "unit": "мм"},
    "fog":     {"name": "Туман",          "unit": "км"},
    "thunder": {"name": "Гроза",          "unit": "—"},
}

HISTORY_DAYS = 14


# ------------------------------------------------------------------
# Страницы
# ------------------------------------------------------------------
@app.route("/")
def index():
    return render_template_string(INDEX_HTML)


@app.route("/about")
def about():
    return render_template_string(ABOUT_HTML)


@app.route("/forecast")
def forecast_hub():
    return render_template_string(FORECAST_HUB_HTML)


@app.route("/analysis")
def analysis_hub():
    return render_template_string(ANALYSIS_HUB_HTML)


@app.route("/theory")
def theory_hub():
    return render_template_string(THEORY_HUB_HTML)


@app.route("/map")
def map_page():
    return render_template_string(
        MAP_HTML,
        stations_json=json.dumps(list(STATIONS.values()), ensure_ascii=False),
        code_to_text_json=json.dumps(CODE_TO_TEXT, ensure_ascii=False),
    )


@app.route("/teaching")
def teaching():
    return render_template_string(TEACHING_HTML)


@app.route("/search")
def search():
    return render_template_string(SEARCH_HTML, models=MODELS)


# ------------------------------------------------------------------
# Модели и станции
# ------------------------------------------------------------------
@app.route("/model/<model_key>")
def model_page(model_key):
    if model_key not in MODELS:
        return "Модель не найдена", 404
    first = next(iter(STATIONS))
    return render_template_string(
        MODEL_HTML,
        model=model_key,
        model_name=MODELS[model_key]["name"],
        stations=STATIONS,
        first_station=first,
    )


@app.route("/forecast/<model_key>/<station_key>")
def forecast_table(model_key, station_key):
    # Здесь должна быть логика получения прогноза.
    # Для демонстрации — пустая заготовка.
    return render_template_string(
        TABLE_TEMPLATE,
        model=model_key,
        model_name=MODELS.get(model_key, {}).get("name", model_key),
        station=STATIONS.get(station_key, {}).get("name", station_key),
        station_key=station_key,
        lat=STATIONS.get(station_key, {}).get("lat", 0),
        lon=STATIONS.get(station_key, {}).get("lon", 0),
        days=5,
        by_day={},       # заполнить реальными данными
        synoptic=[],
        updated="—",
        view="table",
    )


@app.route("/text/<model_key>/<station_key>")
def forecast_text(model_key, station_key):
    return render_template_string(
        TEXT_TEMPLATE,
        model=model_key,
        model_name=MODELS.get(model_key, {}).get("name", model_key),
        station=STATIONS.get(station_key, {}).get("name", station_key),
        station_key=station_key,
        lat=STATIONS.get(station_key, {}).get("lat", 0),
        lon=STATIONS.get(station_key, {}).get("lon", 0),
        days=5,
        text="Текстовый прогноз будет здесь.",
        synoptic=[],
        view="text",
    )


@app.route("/chart/<station_key>")
def chart_page(station_key):
    return render_template_string(
        CHART_HTML,
        station_name=STATIONS.get(station_key, {}).get("name", station_key),
        lat=STATIONS.get(station_key, {}).get("lat", 0),
        lon=STATIONS.get(station_key, {}).get("lon", 0),
        days=5,
        labels_json="[]",
        series_json="{}",
    )


@app.route("/compare/<station_key>")
def compare_page(station_key):
    return render_template_string(
        COMPARE_HTML,
        station_name=STATIONS.get(station_key, {}).get("name", station_key),
        days=5,
        rows=[],
        updated="—",
    )


# ------------------------------------------------------------------
# Проверка моделей
# ------------------------------------------------------------------
@app.route("/verify/<station_key>")
def verify_page(station_key):
    today = date.today()
    return render_template_string(
        VERIFY_HTML,
        station_key=station_key,
        station_name=STATIONS.get(station_key, {}).get("name", station_key),
        default_date=(today - timedelta(days=1)).isoformat(),
        min_date="2020-01-01",
        history_days=HISTORY_DAYS,
    )


@app.route("/verify/<station_key>/history")
def verify_history_page(station_key):
    return render_template_string(
        VERIFY_HISTORY_HTML,
        station_key=station_key,
        station_name=STATIONS.get(station_key, {}).get("name", station_key),
        history_days=HISTORY_DAYS,
    )


@app.route("/analyze/<station_key>")
def analyze_page(station_key):
    return render_template_string(
        ANALYZE_HTML,
        station_key=station_key,
        station_name=STATIONS.get(station_key, {}).get("name", station_key),
        models=MODELS,
    )


@app.route("/aviation/<model_key>/<station_key>")
def aviation_page(model_key, station_key):
    return render_template_string(
        AVIATION_HTML,
        station_key=station_key,
        station_name=STATIONS.get(station_key, {}).get("name", station_key),
        models=MODELS,
    )


# ------------------------------------------------------------------
# Матрица альтернативных прогнозов
# ------------------------------------------------------------------
@app.route("/alt-verify/<station_key>")
def alt_verify_station(station_key):
    s = STATIONS.get(station_key, {})
    today = date.today()
    return render_template_string(
        ALT_VERIFY_HTML,
        station_key=station_key,
        title=s.get("name", station_key),
        lat=s.get("lat", 0),
        lon=s.get("lon", 0),
        models=MODELS,
        phenomena=PHENOMENA,
        phenomenon="frost",
        start_date=(today - timedelta(days=7)).isoformat(),
        end_date=today.isoformat(),
    )


@app.route("/alt-verify")
def alt_verify_point():
    lat = request.args.get("lat", type=float, default=55.75)
    lon = request.args.get("lon", type=float, default=37.62)
    name = request.args.get("name", "Точка")
    today = date.today()
    return render_template_string(
        ALT_VERIFY_HTML,
        station_key="",
        title=name,
        lat=lat,
        lon=lon,
        models=MODELS,
        phenomena=PHENOMENA,
        phenomenon="frost",
        start_date=(today - timedelta(days=7)).isoformat(),
        end_date=today.isoformat(),
    )


@app.route("/compare-matrices/<station_key>")
def compare_matrices_page(station_key):
    s = STATIONS.get(station_key, {})
    today = date.today()
    return render_template_string(
        COMPARE_MATRICES_HTML,
        station_key=station_key,
        station_name=s.get("name", station_key),
        lat=s.get("lat", 0),
        lon=s.get("lon", 0),
        phenomena=PHENOMENA,
        phenomenon="frost",
        start_date=(today - timedelta(days=7)).isoformat(),
        end_date=today.isoformat(),
    )


# ------------------------------------------------------------------
# Тропопауза
# ------------------------------------------------------------------
@app.route("/tropopause")
def tropopause_page():
    return render_template_string(TROPOPAUSE_HTML)


# ------------------------------------------------------------------
# API заглушки (замени на реальную логику)
# ------------------------------------------------------------------
@app.route("/api/geocode")
def api_geocode():
    q = request.args.get("q", "")
    # TODO: реальный геокодер
    return jsonify({"results": [
        {"name": q, "latitude": 55.75, "longitude": 37.62,
         "admin1": "", "country": "Россия"}
    ] if q else []})


@app.route("/api/verify/<station_key>")
def api_verify(station_key):
    # TODO: реальный расчёт MAE/RMSE/Bias
    return jsonify({
        "date": request.args.get("date", date.today().isoformat()),
        "results": [],
    })


@app.route("/api/verify/<station_key>/history")
def api_verify_history(station_key):
    return jsonify({"error": "Не реализовано"})


@app.route("/api/analyze/<station_key>")
def api_analyze(station_key):
    return jsonify({"error": "Не реализовано"})


@app.route("/api/aviation/<model_key>/<station_key>")
def api_aviation(model_key, station_key):
    return jsonify({"error": "Не реализовано"})


@app.route("/api/alt-verify")
def api_alt_verify():
    return jsonify({"error": "Не реализовано"})


@app.route("/api/compare-matrices")
def api_compare_matrices():
    return jsonify({"error": "Не реализовано"})


@app.route("/api/tropopause")
def api_tropopause():
    return jsonify({"error": "Не реализовано"})


@app.route("/api/noaa/nearby")
def api_noaa_nearby():
    return jsonify({"stations": []})


@app.route("/api/noaa/historical")
def api_noaa_historical():
    return jsonify({"error": "Не реализовано"})


# ------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)