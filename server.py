# -*- coding: utf-8 -*-
"""
Flask-приложение weather-msk.
Маршруты и API. Шаблоны берутся из templates.py.
"""

import json
import logging
from datetime import date, timedelta

from flask import Flask, render_template_string, request, jsonify
from tests_bank import TESTS
from templates import TESTS_HTML
from templates import (
    INDEX_HTML, MAP_HTML, ABOUT_HTML,
    FORECAST_HUB_HTML, ANALYSIS_HUB_HTML, THEORY_HUB_HTML,
    TROPOPAUSE_HTML, TEACHING_HTML,
    VERIFY_HTML, VERIFY_HISTORY_HTML, ANALYZE_HTML,
    AVIATION_HTML, ALT_VERIFY_HTML, COMPARE_MATRICES_HTML,
    COMPARE_POINT_HTML,
    CHART_HTML, COMPARE_HTML, MODEL_HTML,
    TABLE_TEMPLATE, TEXT_TEMPLATE, SEARCH_HTML, POINT_TEMPLATE,
    SYNOPTIC_HTML,
    CLIMATE_HTML,
    BIBLIOGRAPHY_HTML, THEORY_METHODS_HTML,
    THEORY_MATRICES_HTML, THEORY_INDICES_HTML,
)
from core.dictionaries import CODE_TO_TEXT, BIBLIOGRAPHY_ITEMS
from core.config import DEFAULT_LOCATION
from core.http import _session

# --- модули для таблицы прогноза ---
from data.forecast import fetch_forecast
from analysis.parsing import parse_hourly, prepare_forecast_for_render
from analysis.synoptic import analyze_synoptic
from analysis.text_forecast import generate_text_forecast
from analysis.synoptic_level import (
    extract_levels, generate_synoptic_text, build_profile_svg,
    SYNOPTIC_LEVELS, LEVEL_NAMES,
)
from analysis.climate_indices import analyze_climate

# --- модули для проверки и анализа ---
from data.actual import fetch_actual, check_station_availability, fetch_archive
from analysis.statistics import analyze_period, analyze_by_day

# --- модули для матриц Хандожко ---
from analysis.aviation_verify import compare_all_models

# --- модули для тропопаузы ---
from data.tropopause_data import fetch_pressure_level_data
from analysis.tropopause import analyze_day

# ------------------------------------------------------------------
# Логирование
# ------------------------------------------------------------------
log = logging.getLogger("weather")
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder="static", static_url_path="/static")


# ------------------------------------------------------------------
# Jinja-фильтры
# ------------------------------------------------------------------
@app.template_filter("date_ru")
def date_ru_filter(iso_date):
    """2024-01-15 -> 'Пн, 15 января'."""
    from datetime import datetime
    months = ["января", "февраля", "марта", "апреля", "мая", "июня",
              "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    try:
        d = datetime.strptime(str(iso_date)[:10], "%Y-%m-%d")
        return f"{weekdays[d.weekday()]}, {d.day} {months[d.month - 1]}"
    except Exception:
        return str(iso_date)


@app.template_filter("absval")
def absval_filter(value):
    """Безопасное абсолютное значение для старых Jinja."""
    try:
        return abs(value)
    except Exception:
        return value


# ------------------------------------------------------------------
# Вспомогательная функция: построение SVG-графика
# ------------------------------------------------------------------
def build_chart_svg(series, fact_series, field, unit, title,
                    decimals=1, width=1400, height=320,
                    times_labels=None, step=1):
    """
    Строит SVG-график как строку.

    series: список {key, name, color, temps, press, winds, precips}
    fact_series: {name, color, temps, press, winds, precips} | None
    field: 'temps' | 'press' | 'winds' | 'precips'
    times_labels: список подписей по X
    step: дискретность точек
    """
    all_vals = []
    for s in series:
        for v in s.get(field, []):
            if v is not None:
                all_vals.append(v)
    if fact_series:
        for v in fact_series.get(field, []):
            if v is not None:
                all_vals.append(v)

    if not all_vals:
        return '<div class="empty-note">Нет данных для отображения.</div>'

    if unit == "гПа":
        vmin = min(all_vals)
        vmax = max(all_vals)
        pad_v = (vmax - vmin) * 0.1 or 5
        vmin -= pad_v
        vmax += pad_v
    else:
        vmin = min(all_vals)
        vmax = max(all_vals)

    if field == "precips":
        vmin = 0

    vspan = (vmax - vmin) or 1

    pad_left = 70
    pad_right = 30
    pad_top = 20
    pad_bottom = 60
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    n = len(series[0].get(field, [])) if series else 0
    if n == 0:
        return '<div class="empty-note">Нет данных.</div>'
    dx = plot_w / (n - 1) if n > 1 else plot_w

    def x(idx):
        return pad_left + dx * idx

    def y(v):
        return pad_top + plot_h * (vmax - v) / vspan

    def fmt(v):
        return f"{v:.{decimals}f}"

    parts = []
    parts.append(f'<svg viewBox="0 0 {width} {height}" '
                 f'preserveAspectRatio="xMidYMid meet" '
                 f'style="width:100%;height:auto;display:block;">')

    parts.append(f'<rect x="{pad_left}" y="{pad_top}" '
                 f'width="{plot_w}" height="{plot_h}" '
                 f'fill="rgba(15,21,36,0.6)" stroke="rgba(120,160,255,0.15)" '
                 f'stroke-width="0.5" rx="6"/>')

    for i in range(6):
        yy = pad_top + plot_h * i / 5
        val = vmax - vspan * i / 5
        parts.append(f'<line x1="{pad_left}" y1="{yy:.2f}" '
                     f'x2="{pad_left + plot_w}" y2="{yy:.2f}" '
                     f'stroke="rgba(120,160,255,0.08)" stroke-width="0.5"/>')
        parts.append(f'<text x="{pad_left - 10}" y="{yy + 5:.2f}" '
                     f'text-anchor="end" fill="#a8b4d0" font-size="13" '
                     f'font-family="JetBrains Mono, monospace">{fmt(val)}</text>')

    if times_labels and n > 1:
        label_step = max(1, n // 12)
        if step > 1:
            label_step = max(label_step, step)

        for i in range(0, n, label_step):
            xx = x(i)
            label = times_labels[i] if i < len(times_labels) else ""
            parts.append(f'<line x1="{xx:.2f}" y1="{pad_top + plot_h}" '
                         f'x2="{xx:.2f}" y2="{pad_top + plot_h + 5}" '
                         f'stroke="rgba(120,160,255,0.3)" stroke-width="0.5"/>')
            parts.append(f'<text x="{xx:.2f}" y="{pad_top + plot_h + 20}" '
                         f'text-anchor="middle" fill="#a8b4d0" font-size="12" '
                         f'font-family="JetBrains Mono, monospace">{label}</text>')

    for s in series:
        vals = s.get(field, [])
        pts = []
        color = s.get("color", "#4dabff")

        circles = []
        for idx, v in enumerate(vals):
            if v is not None:
                px = x(idx)
                py = y(v)
                pts.append(f"{px:.2f},{py:.2f}")
                if idx % step == 0:
                    label_txt = times_labels[idx] if times_labels and idx < len(times_labels) else ""
                    circles.append(
                        f'<circle cx="{px:.2f}" cy="{py:.2f}" r="3" '
                        f'fill="{color}" stroke="var(--bg-0)" stroke-width="1" '
                        f'data-time="{label_txt}" '
                        f'data-value="{fmt(v)}" '
                        f'data-unit="{unit}" '
                        f'data-model="{s.get("name", "")}" '
                        f'style="cursor:pointer;"/>'
                    )

        if pts:
            parts.append(f'<polyline fill="none" stroke="{color}" '
                         f'stroke-width="2" stroke-linejoin="round" '
                         f'stroke-linecap="round" points="{" ".join(pts)}"/>')
            parts.extend(circles)

    if fact_series:
        vals = fact_series.get(field, [])
        pts = []
        color = fact_series.get("color", "#a8b4d0")
        for idx, v in enumerate(vals):
            if v is not None:
                pts.append(f"{x(idx):.2f},{y(v):.2f}")
        if pts:
            parts.append(f'<polyline fill="none" stroke="{color}" '
                         f'stroke-width="1.5" stroke-opacity="0.7" '
                         f'stroke-dasharray="4 3" '
                         f'stroke-linejoin="round" stroke-linecap="round" '
                         f'points="{" ".join(pts)}"/>')

    parts.append(f'<text x="8" y="{pad_top - 4}" '
                 f'fill="#6b7694" font-size="12" '
                 f'font-family="Inter, sans-serif">{unit}</text>')

    parts.append('</svg>')

    return "".join(parts)


# ------------------------------------------------------------------
# Конфигурация
# ------------------------------------------------------------------
try:
    from core.config import STATIONS as _STATIONS
    STATIONS = _STATIONS
except ImportError:
    STATIONS = {
        "tushino": {"name": "Тушино", "lat": 55.85, "lon": 37.44, "key": "tushino"},
    }

try:
    from core.config import MODELS as _MODELS
    MODELS = _MODELS
except ImportError:
    MODELS = {
        "gfs":   {"name": "GFS (США)"},
        "ecmwf": {"name": "ECMWF (Европа)"},
        "icon":  {"name": "ICON (Германия)"},
    }

PHENOMENA = {
    "frost":   {"name": "Заморозок",     "unit": "°C"},
    "wind":    {"name": "Сильный ветер", "unit": "м/с"},
    "rain":    {"name": "Сильный дождь", "unit": "мм"},
    "fog":     {"name": "Туман",         "unit": "км"},
    "thunder": {"name": "Гроза",         "unit": "—"},
}

HISTORY_DAYS = 14

_MODEL_COLORS = {
    "gfs":   "#4dabff",
    "ecmwf": "#ffb547",
    "icon":  "#00e5a0",
}
_FACT_COLOR = "#a8b4d0"


# ------------------------------------------------------------------
# Главные страницы
# ------------------------------------------------------------------
@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/tests")
def tests_page():
    """Страница тестов: выбор блока, прохождение, результат."""
    import json as _json
    return render_template_string(
        TESTS_HTML,
        tests=TESTS,
        tests_json=_json.dumps(TESTS, ensure_ascii=False),
    )

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


# ------------------------------------------------------------------
# НОВЫЕ РОУТЫ: теория по группам + библиография
# ------------------------------------------------------------------
@app.route("/bibliography")
def bibliography_page():
    """Библиография: источники по всем разделам."""
    return render_template_string(
        BIBLIOGRAPHY_HTML,
        bibliography=BIBLIOGRAPHY_ITEMS,
    )


@app.route("/theory/methods")
def theory_methods():
    """Теория: методы прогноза (изоэнтропика, PV, синоптика)."""
    return render_template_string(THEORY_METHODS_HTML)


@app.route("/theory/matrices")
def theory_matrices():
    """Теория: матрицы сопряжённости и критерии Хандожко."""
    return render_template_string(THEORY_MATRICES_HTML)


@app.route("/theory/indices")
def theory_indices():
    """Теория: индексы неустойчивости и явления."""
    return render_template_string(THEORY_INDICES_HTML)


# ------------------------------------------------------------------
# Карта, обучение, климат
# ------------------------------------------------------------------
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


@app.route("/climate")
def climate_page():
    """Климатические индексы: ENSO, SSW, PV."""
    try:
        days_back = int(request.args.get("days", 365))
    except (TypeError, ValueError):
        days_back = 365
    days_back = max(30, min(days_back, 730))

    try:
        data = analyze_climate(days_back=days_back)
    except Exception as e:
        log.exception("climate: error: %s", e)
        return render_template_string(
            CLIMATE_HTML,
            period={"start": "—", "end": "—"},
            days_back=days_back,
            enso=None, ssw=None, pv=None,
            error=str(e),
        )

    return render_template_string(
        CLIMATE_HTML,
        period=data.get("period") or {"start": "—", "end": "—"},
        days_back=days_back,
        enso=data.get("enso"),
        ssw=data.get("ssw"),
        pv=data.get("pv"),
        error=data.get("error"),
    )


@app.route("/search")
def search():
    """Поиск точки: geocoding или координаты."""
    return render_template_string(
        SEARCH_HTML,
        models=MODELS,
        preset_lat=request.args.get("lat"),
        preset_lon=request.args.get("lon"),
        preset_name=request.args.get("name", ""),
    )


@app.route("/tropopause")
def tropopause_page():
    """Складки тропопаузы: EPV, 2 PVU, профиль."""
    station_key = request.args.get("station", "domodedovo")
    if station_key not in STATIONS:
        station_key = next(iter(STATIONS))
    s = STATIONS[station_key]
    lat, lon = s["lat"], s["lon"]

    target_date = request.args.get("date", date.today().isoformat())

    try:
        hour_index = int(request.args.get("hour", 12))
    except (TypeError, ValueError):
        hour_index = 12
    hour_index = max(0, min(hour_index, 23))

    try:
        raw = fetch_pressure_level_data(lat, lon, target_date)
    except Exception as e:
        log.exception("tropopause: ошибка данных: %s", e)
        return render_template_string(
            TROPOPAUSE_HTML,
            station_key=station_key,
            station_name=s["name"],
            lat=lat, lon=lon,
            target_date=target_date,
            hour_index=hour_index,
            hours_options=list(range(0, 24, 3)),
            stations=STATIONS,
            error=str(e),
            analysis=False,
            max_pv_day_scale=1.0,
        )

    try:
        day_result = analyze_day(raw, lat, lon)
    except Exception as e:
        log.exception("tropopause: ошибка анализа: %s", e)
        return render_template_string(
            TROPOPAUSE_HTML,
            station_key=station_key,
            station_name=s["name"],
            lat=lat, lon=lon,
            target_date=target_date,
            hour_index=hour_index,
            hours_options=list(range(0, 24, 3)),
            stations=STATIONS,
            error=str(e),
            analysis=False,
            max_pv_day_scale=1.0,
        )

    hours = day_result.get("hours", [])
    if hour_index >= len(hours):
        hour_index = min(len(hours) - 1, 12)

    selected = hours[hour_index] if hours else None

    all_pv = [h.get("max_pv", 0) or 0 for h in hours]
    max_pv_day_scale = max(all_pv) if all_pv else 1.0

    return render_template_string(
        TROPOPAUSE_HTML,
        station_key=station_key,
        station_name=s["name"],
        lat=lat, lon=lon,
        target_date=target_date,
        hour_index=hour_index,
        hours_options=list(range(0, 24, 3)),
        stations=STATIONS,
        summary=day_result.get("summary"),
        selected=selected,
        all_hours=hours,
        error=None,
        analysis=True,
        max_pv_day_scale=max_pv_day_scale,
    )


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


# ------------------------------------------------------------------
# Таблица прогноза
# ------------------------------------------------------------------
@app.route("/forecast/<model_key>/<station_key>")
def forecast_table(model_key, station_key):
    """Таблица прогноза по модели и станции."""
    if model_key not in MODELS:
        return "Модель не найдена", 404
    if station_key not in STATIONS:
        return "Станция не найдена", 404

    s = STATIONS[station_key]
    lat, lon = s["lat"], s["lon"]
    model_name = MODELS[model_key]["name"]

    model_switcher = [
        {"key": k, "name": v["name"], "active": (k == model_key)}
        for k, v in MODELS.items()
    ]

    try:
        raw = fetch_forecast(model_key, lat, lon, days=5)
        forecast = parse_hourly(raw)
        by_day = prepare_forecast_for_render(forecast)
        events = analyze_synoptic(forecast)
    except Exception as e:
        log.exception("Ошибка при получении прогноза: %s", e)
        return render_template_string(
            TABLE_TEMPLATE,
            model=model_key,
            model_name=model_name,
            station=s["name"],
            station_key=station_key,
            lat=lat, lon=lon, days=5,
            days_list=[],
            events=[],
            events_by_time={},
            model_switcher=model_switcher,
            error=str(e),
            is_point=False,
        )

    events_by_time = {}
    for ev in events:
        events_by_time.setdefault(ev["time"], []).append(ev)

    days_list = []
    for day, rows in by_day.items():
        days_list.append({
            "date": day,
            "rows": rows,
            "events": [ev for ev in events if ev["time"][:10] == day],
        })

    return render_template_string(
        TABLE_TEMPLATE,
        model=model_key,
        model_name=model_name,
        station=s["name"],
        station_key=station_key,
        lat=lat, lon=lon, days=5,
        days_list=days_list,
        events=events,
        events_by_time=events_by_time,
        model_switcher=model_switcher,
        error=None,
        is_point=False,
    )


@app.route("/text/<model_key>/<station_key>")
def forecast_text(model_key, station_key):
    """Текстовый прогноз по модели и станции."""
    if model_key not in MODELS:
        return "Модель не найдена", 404
    if station_key not in STATIONS:
        return "Станция не найдена", 404

    s = STATIONS[station_key]
    lat, lon = s["lat"], s["lon"]
    station_name = s["name"]
    model_name = MODELS[model_key]["name"]

    try:
        days = int(request.args.get("days", 5))
    except (TypeError, ValueError):
        days = 5
    days = max(1, min(days, 7))

    model_switcher = [
        {"key": k, "name": v["name"], "active": (k == model_key)}
        for k, v in MODELS.items()
    ]

    try:
        raw = fetch_forecast(model_key, lat, lon, days=days)
        forecast = parse_hourly(raw)
    except Exception as e:
        log.exception("forecast_text: ошибка прогноза: %s", e)
        return render_template_string(
            TEXT_TEMPLATE,
            model=model_key,
            model_name=model_name,
            station=station_name,
            station_key=station_key,
            lat=lat, lon=lon,
            days=days,
            model_switcher=model_switcher,
            days_options=[1, 3, 5, 7],
            text=f"Не удалось загрузить прогноз: {e}",
            error=str(e),
            is_point=False,
        )

    try:
        text = generate_text_forecast(model_name, station_name, forecast)
    except Exception as e:
        log.exception("forecast_text: ошибка генерации текста: %s", e)
        text = f"Ошибка генерации текста: {e}"

    return render_template_string(
        TEXT_TEMPLATE,
        model=model_key,
        model_name=model_name,
        station=station_name,
        station_key=station_key,
        lat=lat, lon=lon,
        days=days,
        model_switcher=model_switcher,
        days_options=[1, 3, 5, 7],
        text=text,
        error=None,
        is_point=False,
    )


# ------------------------------------------------------------------
# График сравнения моделей (станция)
# ------------------------------------------------------------------
@app.route("/chart/<station_key>")
def chart_page(station_key):
    """Сравнение моделей на графике: T, P, ветер, осадки."""
    if station_key not in STATIONS:
        return "Станция не найдена", 404

    s = STATIONS[station_key]
    lat, lon = s["lat"], s["lon"]
    station_name = s["name"]

    try:
        days = int(request.args.get("days", 5))
    except (TypeError, ValueError):
        days = 5
    days = max(2, min(days, 7))

    step = request.args.get("step", type=int, default=1) or 1
    step = max(1, min(step, 12))

    models_param = request.args.get("models", "")
    if models_param:
        selected_models = [m.strip() for m in models_param.split(",") if m.strip() in MODELS]
    else:
        selected_models = list(MODELS.keys())
    if not selected_models:
        selected_models = list(MODELS.keys())

    toggle_models = {}
    for mk in MODELS:
        if mk in selected_models:
            toggle_models[mk] = [m for m in selected_models if m != mk]
        else:
            toggle_models[mk] = selected_models + [mk]

    series = []
    times_global = None

    for model_key in selected_models:
        try:
            raw = fetch_forecast(model_key, lat, lon, days=days)
            forecast = parse_hourly(raw)
        except Exception as e:
            log.exception("chart_page: %s error: %s", model_key, e)
            continue

        if not forecast:
            continue

        model_times = [h["time"] for h in forecast]
        if times_global is None:
            times_global = model_times
        else:
            times_global = [t for t in times_global if t in model_times]

    if times_global is None or not times_global:
        return render_template_string(
            CHART_HTML,
            station_name=station_name,
            station_key=station_key,
            lat=lat, lon=lon,
            days=days,
            step=step,
            days_options=[3, 5, 7],
            models=MODELS,
            selected_models=selected_models,
            toggle_models=toggle_models,
            model_colors=_MODEL_COLORS,
            times=[], times_labels=[], days_list=[],
            series=[], fact_series=None,
            svg_temps="", svg_press="", svg_winds="", svg_prec="",
            error="Не удалось загрузить прогнозы. Попробуйте позже.",
            is_point=False,
        )

    for model_key in selected_models:
        try:
            raw = fetch_forecast(model_key, lat, lon, days=days)
            forecast = parse_hourly(raw)
        except Exception:
            continue

        by_time = {h["time"]: h for h in forecast}
        temps, press, winds, precips = [], [], [], []

        for t in times_global:
            h = by_time.get(t)
            if h is None:
                temps.append(None); press.append(None)
                winds.append(None); precips.append(None)
            else:
                temps.append(h.get("temp_c"))
                press.append(h.get("pressure_hpa"))
                winds.append(h.get("wind_ms"))
                precips.append(h.get("precipitation_mm"))

        series.append({
            "key": model_key,
            "name": MODELS[model_key]["name"],
            "color": _MODEL_COLORS.get(model_key, "#888"),
            "temps": temps, "press": press,
            "winds": winds, "precips": precips,
        })

    fact_series = None
    try:
        today = date.today()
        start = (today - timedelta(days=days)).isoformat()
        end = (today - timedelta(days=1)).isoformat()
        archive = fetch_archive(lat, lon, start, end)
        if archive:
            h = archive.get("hourly", {})
            fact_times = dict(zip(h.get("time", []), h.get("temperature_2m", [])))
            fact_press = dict(zip(h.get("time", []), h.get("pressure_msl", [])))
            fact_wind  = dict(zip(h.get("time", []), h.get("wind_speed_10m", [])))
            fact_prec  = dict(zip(h.get("time", []), h.get("precipitation", [])))

            f_temps   = [fact_times.get(t) for t in times_global]
            f_press   = [fact_press.get(t) for t in times_global]
            f_winds   = [fact_wind.get(t) for t in times_global]
            f_precips = [fact_prec.get(t) for t in times_global]

            if any(v is not None for v in f_temps):
                fact_series = {
                    "name": "ERA5 (факт)", "color": _FACT_COLOR,
                    "temps": f_temps, "press": f_press,
                    "winds": f_winds, "precips": f_precips,
                }
    except Exception as e:
        log.warning("chart_page: ERA5 не загружен: %s", e)

    days_map = {}
    for i, t in enumerate(times_global):
        d = t[:10]
        if d not in days_map:
            days_map[d] = {"date": d, "start_idx": i, "end_idx": i}
        else:
            days_map[d]["end_idx"] = i

    days_list = list(days_map.values())
    times_labels = [t[11:16] for t in times_global]

    svg_temps = build_chart_svg(series, fact_series, "temps", "°C", "Температура",
                                decimals=1, times_labels=times_labels, step=step)
    svg_press = build_chart_svg(series, fact_series, "press", "гПа", "Давление",
                                decimals=0, times_labels=times_labels, step=step)
    svg_winds = build_chart_svg(series, fact_series, "winds", "м/с", "Ветер",
                                decimals=0, times_labels=times_labels, step=step)
    svg_prec  = build_chart_svg(series, fact_series, "precips", "мм", "Осадки",
                                decimals=2, times_labels=times_labels, step=step)

    return render_template_string(
        CHART_HTML,
        station_name=station_name,
        station_key=station_key,
        lat=lat, lon=lon,
        days=days,
        step=step,
        days_options=[3, 5, 7],
        models=MODELS,
        selected_models=selected_models,
        toggle_models=toggle_models,
        model_colors=_MODEL_COLORS,
        times=times_global,
        times_labels=times_labels,
        days_list=days_list,
        series=series,
        fact_series=fact_series,
        svg_temps=svg_temps,
        svg_press=svg_press,
        svg_winds=svg_winds,
        svg_prec=svg_prec,
        error=None,
        is_point=False,
    )


@app.route("/compare/<station_key>")
def compare_page(station_key):
    return render_template_string(
        COMPARE_HTML,
        station_name=STATIONS.get(station_key, {}).get("name", station_key),
        days=5,
    )
@app.route("/compare/point")
def compare_point():
    """Сводка явлений для произвольной точки (по координатам или названию)."""
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    name = request.args.get("name", "").strip()

    # Если координаты не переданы — показываем только форму поиска
    if lat is None or lon is None:
        return render_template_string(
            COMPARE_POINT_HTML,
            models=MODELS,
            preset_lat=None,
            preset_lon=None,
            preset_name=name,
            results=None,
            phenomena=None,
            error=None,
            days=5,
            days_options=[3, 5, 7],
            station_key="point",
            station_name=None,
        )

    if not name:
        name = f"{lat:.4f}, {lon:.4f}"

    try:
        days = int(request.args.get("days", 5))
    except (TypeError, ValueError):
        days = 5
    days = max(1, min(days, 7))

    # Явления — те же, что в compare_page
    PHENOMENA_LIST = [
        ("fog",     "Туман",         "🌫", lambda h: h.get("weather_code") in (45, 48)),
        ("thunder", "Гроза",         "⚡", lambda h: h.get("weather_code") in (95, 96, 99)),
        ("rain",    "Осадки",        "🌧", lambda h: (h.get("precipitation_mm") or 0) > 0.05),
        ("snow",    "Снег",          "❄️", lambda h: h.get("weather_code") in (71, 73, 75, 77, 85, 86)),
        ("frost",   "Заморозок",     "🥶", lambda h: h.get("temp_c") is not None and h.get("temp_c") < 0),
        ("wind",    "Сильный ветер", "💨", lambda h: (h.get("wind_ms") or 0) >= 12.0),
    ]

    results = []
    for model_key in MODELS:
        row = {
            "model_key": model_key,
            "model_name": MODELS[model_key]["name"],
            "color": _MODEL_COLORS.get(model_key, "#888"),
            "error": None,
            "phenomena": [],
        }

        try:
            raw = fetch_forecast(model_key, lat, lon, days=days)
            forecast = parse_hourly(raw)
        except Exception as e:
            log.exception("compare_point: %s error: %s", model_key, e)
            row["error"] = str(e)
            results.append(row)
            continue

        for key, ph_name, icon, test in PHENOMENA_LIST:
            hit_hours = [h for h in forecast if test(h)]
            hours_count = len(hit_hours)
            total_hours = len(forecast)
            percent = round(100.0 * hours_count / total_hours, 1) if total_hours else 0

            times = [h["time"] for h in hit_hours]
            row["phenomena"].append({
                "key": key,
                "name": ph_name,
                "icon": icon,
                "hours": hours_count,
                "total": total_hours,
                "percent": percent,
                "first_time": times[0] if times else None,
                "last_time": times[-1] if times else None,
            })

        results.append(row)

    return render_template_string(
        COMPARE_POINT_HTML,
        models=MODELS,
        preset_lat=lat,
        preset_lon=lon,
        preset_name=name,
        results=results,
        phenomena=PHENOMENA_LIST,
        error=None,
        days=days,
        days_options=[3, 5, 7],
        station_key="point",
        station_name=name,
    )

# ------------------------------------------------------------------
# Точка: таблица, текст, авиация, график
# ------------------------------------------------------------------
@app.route("/forecast/point")
def forecast_point():
    """Таблица прогноза для произвольной точки."""
    lat = request.args.get("lat", type=float, default=DEFAULT_LOCATION["lat"])
    lon = request.args.get("lon", type=float, default=DEFAULT_LOCATION["lon"])
    name = request.args.get("name", DEFAULT_LOCATION["name"])
    model_key = request.args.get("model", "gfs")
    if model_key not in MODELS:
        model_key = "gfs"

    days = 5
    model_name = MODELS[model_key]["name"]

    model_switcher = [
        {"key": k, "name": v["name"], "active": (k == model_key)}
        for k, v in MODELS.items()
    ]

    try:
        raw = fetch_forecast(model_key, lat, lon, days=days)
        forecast = parse_hourly(raw)
        by_day = prepare_forecast_for_render(forecast)
        events = analyze_synoptic(forecast)
    except Exception as e:
        log.exception("forecast_point error: %s", e)
        return render_template_string(
            TABLE_TEMPLATE,
            model=model_key,
            model_name=model_name,
            station=name,
            station_key="point",
            lat=lat, lon=lon, days=days,
            days_list=[], events=[], events_by_time={},
            model_switcher=model_switcher,
            error=str(e),
            is_point=True,
        )

    events_by_time = {}
    for ev in events:
        events_by_time.setdefault(ev["time"], []).append(ev)

    days_list = []
    for day, rows in by_day.items():
        days_list.append({
            "date": day,
            "rows": rows,
            "events": [ev for ev in events if ev["time"][:10] == day],
        })

    return render_template_string(
        TABLE_TEMPLATE,
        model=model_key,
        model_name=model_name,
        station=name,
        station_key="point",
        lat=lat, lon=lon, days=days,
        days_list=days_list,
        events=events,
        events_by_time=events_by_time,
        model_switcher=model_switcher,
        error=None,
        is_point=True,
    )


@app.route("/point-text")
def point_text():
    """Текстовый прогноз для произвольной точки."""
    lat = request.args.get("lat", type=float, default=DEFAULT_LOCATION["lat"])
    lon = request.args.get("lon", type=float, default=DEFAULT_LOCATION["lon"])
    name = request.args.get("name", DEFAULT_LOCATION["name"])
    model_key = request.args.get("model", "gfs")
    if model_key not in MODELS:
        model_key = "gfs"

    try:
        days = int(request.args.get("days", 5))
    except (TypeError, ValueError):
        days = 5
    days = max(1, min(days, 7))

    model_name = MODELS[model_key]["name"]

    model_switcher = [
        {"key": k, "name": v["name"], "active": (k == model_key)}
        for k, v in MODELS.items()
    ]

    try:
        raw = fetch_forecast(model_key, lat, lon, days=days)
        forecast = parse_hourly(raw)
        text = generate_text_forecast(model_name, name, forecast)
    except Exception as e:
        log.exception("point_text error: %s", e)
        text = f"Не удалось сгенерировать прогноз: {e}"

    return render_template_string(
        TEXT_TEMPLATE,
        model=model_key,
        model_name=model_name,
        station=name,
        station_key="point",
        lat=lat, lon=lon,
        days=days,
        model_switcher=model_switcher,
        days_options=[1, 3, 5, 7],
        text=text,
        error=None,
        is_point=True,
    )


@app.route("/point-aviation")
def point_aviation():
    """Авиационный прогноз для произвольной точки."""
    lat = request.args.get("lat", type=float, default=DEFAULT_LOCATION["lat"])
    lon = request.args.get("lon", type=float, default=DEFAULT_LOCATION["lon"])
    name = request.args.get("name", DEFAULT_LOCATION["name"])
    model_key = request.args.get("model", "gfs")
    if model_key not in MODELS:
        model_key = "gfs"

    try:
        days = int(request.args.get("days", 3))
    except (TypeError, ValueError):
        days = 3
    days = max(1, min(days, 7))

    model_name = MODELS[model_key]["name"]

    model_switcher = [
        {"key": k, "name": v["name"], "active": (k == model_key)}
        for k, v in MODELS.items()
    ]

    try:
        raw = fetch_forecast(model_key, lat, lon, days=days)
        forecast = parse_hourly(raw)
        by_day = prepare_forecast_for_render(forecast)
    except Exception as e:
        log.exception("point_aviation error: %s", e)
        return render_template_string(
            AVIATION_HTML,
            model=model_key,
            model_name=model_name,
            station_name=name,
            station_key="point",
            lat=lat, lon=lon, days=days,
            days_list=[],
            model_switcher=model_switcher,
            days_options=[1, 2, 3, 5, 7],
            summary={},
            error=str(e),
            MODELS=MODELS,
            is_point=True,
        )

    summary = {
        "hours_total": 0,
        "thunder_hours": 0,
        "thunder_max_prob": 0,
        "thunder_max_level": "нет",
        "fog_hours": 0,
        "fog_max_prob": 0,
        "fog_max_level": "нет",
        "k_max": None,
        "li_min": None,
        "cape_max": None,
    }

    for h in forecast:
        summary["hours_total"] += 1

        avt = h.get("av_thunder") or {}
        if avt.get("combined_level") and avt["combined_level"] not in ("нет", "нет данных"):
            summary["thunder_hours"] += 1
        if avt.get("combined_prob") and avt["combined_prob"] > summary["thunder_max_prob"]:
            summary["thunder_max_prob"] = avt["combined_prob"]
            summary["thunder_max_level"] = avt.get("combined_level", "нет")

        avf = h.get("av_fog") or {}
        if avf.get("level") and avf["level"] not in ("нет", "нет данных"):
            summary["fog_hours"] += 1
        if avf.get("probability") and avf["probability"] > summary["fog_max_prob"]:
            summary["fog_max_prob"] = avf["probability"]
            summary["fog_max_level"] = avf.get("level", "нет")

        if avt.get("k") is not None:
            if summary["k_max"] is None or avt["k"] > summary["k_max"]:
                summary["k_max"] = avt["k"]
        if avt.get("li") is not None:
            if summary["li_min"] is None or avt["li"] < summary["li_min"]:
                summary["li_min"] = avt["li"]
        if avt.get("cape") is not None:
            if summary["cape_max"] is None or avt["cape"] > summary["cape_max"]:
                summary["cape_max"] = avt["cape"]

    days_list = []
    for day, rows in by_day.items():
        days_list.append({"date": day, "rows": rows})

    return render_template_string(
        AVIATION_HTML,
        model=model_key,
        model_name=model_name,
        station_name=name,
        station_key="point",
        lat=lat, lon=lon, days=days,
        days_list=days_list,
        model_switcher=model_switcher,
        days_options=[1, 2, 3, 5, 7],
        summary=summary,
        error=None,
        MODELS=MODELS,
        is_point=True,
    )


@app.route("/point-chart")
def point_chart():
    """Сравнение моделей на графике для произвольной точки."""
    lat = request.args.get("lat", type=float, default=DEFAULT_LOCATION["lat"])
    lon = request.args.get("lon", type=float, default=DEFAULT_LOCATION["lon"])
    name = request.args.get("name", DEFAULT_LOCATION["name"])

    try:
        days = int(request.args.get("days", 5))
    except (TypeError, ValueError):
        days = 5
    days = max(2, min(days, 7))

    step = request.args.get("step", type=int, default=1) or 1
    step = max(1, min(step, 12))

    models_param = request.args.get("models", "")
    if models_param:
        selected_models = [m.strip() for m in models_param.split(",") if m.strip() in MODELS]
    else:
        selected_models = list(MODELS.keys())
    if not selected_models:
        selected_models = list(MODELS.keys())

    toggle_models = {}
    for mk in MODELS:
        if mk in selected_models:
            toggle_models[mk] = [m for m in selected_models if m != mk]
        else:
            toggle_models[mk] = selected_models + [mk]

    series = []
    times_global = None

    for model_key in selected_models:
        try:
            raw = fetch_forecast(model_key, lat, lon, days=days)
            forecast = parse_hourly(raw)
        except Exception as e:
            log.exception("point_chart: %s error: %s", model_key, e)
            continue

        if not forecast:
            continue

        model_times = [h["time"] for h in forecast]
        if times_global is None:
            times_global = model_times
        else:
            times_global = [t for t in times_global if t in model_times]

    if times_global is None or not times_global:
        return render_template_string(
            CHART_HTML,
            station_name=name,
            station_key="point",
            lat=lat, lon=lon,
            days=days,
            step=step,
            days_options=[3, 5, 7],
            models=MODELS,
            selected_models=selected_models,
            toggle_models=toggle_models,
            model_colors=_MODEL_COLORS,
            times=[], times_labels=[], days_list=[],
            series=[], fact_series=None,
            svg_temps="", svg_press="", svg_winds="", svg_prec="",
            error="Не удалось загрузить прогнозы. Попробуйте позже.",
            is_point=True,
        )

    for model_key in selected_models:
        try:
            raw = fetch_forecast(model_key, lat, lon, days=days)
            forecast = parse_hourly(raw)
        except Exception:
            continue

        by_time = {h["time"]: h for h in forecast}
        temps, press, winds, precips = [], [], [], []

        for t in times_global:
            h = by_time.get(t)
            if h is None:
                temps.append(None); press.append(None)
                winds.append(None); precips.append(None)
            else:
                temps.append(h.get("temp_c"))
                press.append(h.get("pressure_hpa"))
                winds.append(h.get("wind_ms"))
                precips.append(h.get("precipitation_mm"))

        series.append({
            "key": model_key,
            "name": MODELS[model_key]["name"],
            "color": _MODEL_COLORS.get(model_key, "#888"),
            "temps": temps, "press": press,
            "winds": winds, "precips": precips,
        })

    fact_series = None
    try:
        today = date.today()
        start = (today - timedelta(days=days)).isoformat()
        end = (today - timedelta(days=1)).isoformat()
        archive = fetch_archive(lat, lon, start, end)
        if archive:
            h = archive.get("hourly", {})
            fact_times = dict(zip(h.get("time", []), h.get("temperature_2m", [])))
            fact_press = dict(zip(h.get("time", []), h.get("pressure_msl", [])))
            fact_wind  = dict(zip(h.get("time", []), h.get("wind_speed_10m", [])))
            fact_prec  = dict(zip(h.get("time", []), h.get("precipitation", [])))

            f_temps   = [fact_times.get(t) for t in times_global]
            f_press   = [fact_press.get(t) for t in times_global]
            f_winds   = [fact_wind.get(t) for t in times_global]
            f_precips = [fact_prec.get(t) for t in times_global]

            if any(v is not None for v in f_temps):
                fact_series = {
                    "name": "ERA5 (факт)", "color": _FACT_COLOR,
                    "temps": f_temps, "press": f_press,
                    "winds": f_winds, "precips": f_precips,
                }
    except Exception as e:
        log.warning("point_chart: ERA5 не загружен: %s", e)

    days_map = {}
    for i, t in enumerate(times_global):
        d = t[:10]
        if d not in days_map:
            days_map[d] = {"date": d, "start_idx": i, "end_idx": i}
        else:
            days_map[d]["end_idx"] = i

    days_list = list(days_map.values())
    times_labels = [t[11:16] for t in times_global]

    svg_temps = build_chart_svg(series, fact_series, "temps", "°C", "Температура",
                                decimals=1, times_labels=times_labels, step=step)
    svg_press = build_chart_svg(series, fact_series, "press", "гПа", "Давление",
                                decimals=0, times_labels=times_labels, step=step)
    svg_winds = build_chart_svg(series, fact_series, "winds", "м/с", "Ветер",
                                decimals=0, times_labels=times_labels, step=step)
    svg_prec  = build_chart_svg(series, fact_series, "precips", "мм", "Осадки",
                                decimals=2, times_labels=times_labels, step=step)

    return render_template_string(
        CHART_HTML,
        station_name=name,
        station_key="point",
        lat=lat, lon=lon,
        days=days,
        step=step,
        days_options=[3, 5, 7],
        models=MODELS,
        selected_models=selected_models,
        toggle_models=toggle_models,
        model_colors=_MODEL_COLORS,
        times=times_global,
        times_labels=times_labels,
        days_list=days_list,
        series=series,
        fact_series=fact_series,
        svg_temps=svg_temps,
        svg_press=svg_press,
        svg_winds=svg_winds,
        svg_prec=svg_prec,
        error=None,
        is_point=True,
    )


# ------------------------------------------------------------------
# СИНОПТИКА ПО УРОВНЯМ
# ------------------------------------------------------------------
@app.route("/synoptic/<model_key>/<station_key>")
def synoptic_station(model_key, station_key):
    """Синоптический анализ по уровням для станции."""
    if model_key not in MODELS:
        return "Модель не найдена", 404
    if station_key not in STATIONS:
        return "Станция не найдена", 404

    s = STATIONS[station_key]
    lat, lon = s["lat"], s["lon"]
    station_name = s["name"]
    model_name = MODELS[model_key]["name"]

    try:
        days = int(request.args.get("days", 3))
    except (TypeError, ValueError):
        days = 3
    days = max(1, min(days, 5))

    try:
        hour_index = int(request.args.get("hour", 12))
    except (TypeError, ValueError):
        hour_index = 12
    hour_index = max(0, min(hour_index, 23))

    model_switcher = [
        {"key": k, "name": v["name"], "active": (k == model_key)}
        for k, v in MODELS.items()
    ]

    try:
        raw = fetch_forecast(model_key, lat, lon, days=days)
        forecast = parse_hourly(raw)
        hours = extract_levels(forecast)
        text = generate_synoptic_text(station_name, model_name, hours, hour_index=hour_index)
        profile_svg = build_profile_svg(hours, hour_index)
    except Exception as e:
        log.exception("synoptic error: %s", e)
        return render_template_string(
            SYNOPTIC_HTML,
            model=model_key,
            model_name=model_name,
            station_name=station_name,
            station_key=station_key,
            lat=lat, lon=lon,
            days=days, hour_index=hour_index,
            model_switcher=model_switcher,
            days_options=[1, 3, 5],
            hours_options=list(range(0, 24, 3)),
            hours=[], text="", profile_svg="",
            levels=SYNOPTIC_LEVELS,
            level_names=LEVEL_NAMES,
            error=str(e),
            is_point=False,
        )

    return render_template_string(
        SYNOPTIC_HTML,
        model=model_key,
        model_name=model_name,
        station_name=station_name,
        station_key=station_key,
        lat=lat, lon=lon,
        days=days, hour_index=hour_index,
        model_switcher=model_switcher,
        days_options=[1, 3, 5],
        hours_options=list(range(0, 24, 3)),
        hours=hours,
        text=text,
        profile_svg=profile_svg,
        levels=SYNOPTIC_LEVELS,
        level_names=LEVEL_NAMES,
        error=None,
        is_point=False,
    )


@app.route("/point-synoptic")
def synoptic_point():
    """Синоптический анализ по уровням для точки."""
    lat = request.args.get("lat", type=float, default=DEFAULT_LOCATION["lat"])
    lon = request.args.get("lon", type=float, default=DEFAULT_LOCATION["lon"])
    name = request.args.get("name", DEFAULT_LOCATION["name"])
    model_key = request.args.get("model", "gfs")
    if model_key not in MODELS:
        model_key = "gfs"

    try:
        days = int(request.args.get("days", 3))
    except (TypeError, ValueError):
        days = 3
    days = max(1, min(days, 5))

    try:
        hour_index = int(request.args.get("hour", 12))
    except (TypeError, ValueError):
        hour_index = 12
    hour_index = max(0, min(hour_index, 23))

    model_name = MODELS[model_key]["name"]

    model_switcher = [
        {"key": k, "name": v["name"], "active": (k == model_key)}
        for k, v in MODELS.items()
    ]

    try:
        raw = fetch_forecast(model_key, lat, lon, days=days)
        forecast = parse_hourly(raw)
        hours = extract_levels(forecast)
        text = generate_synoptic_text(name, model_name, hours, hour_index=hour_index)
        profile_svg = build_profile_svg(hours, hour_index)
    except Exception as e:
        log.exception("synoptic point error: %s", e)
        return render_template_string(
            SYNOPTIC_HTML,
            model=model_key,
            model_name=model_name,
            station_name=name,
            station_key="point",
            lat=lat, lon=lon,
            days=days, hour_index=hour_index,
            model_switcher=model_switcher,
            days_options=[1, 3, 5],
            hours_options=list(range(0, 24, 3)),
            hours=[], text="", profile_svg="",
            levels=SYNOPTIC_LEVELS,
            level_names=LEVEL_NAMES,
            error=str(e),
            is_point=True,
        )

    return render_template_string(
        SYNOPTIC_HTML,
        model=model_key,
        model_name=model_name,
        station_name=name,
        station_key="point",
        lat=lat, lon=lon,
        days=days, hour_index=hour_index,
        model_switcher=model_switcher,
        days_options=[1, 3, 5],
        hours_options=list(range(0, 24, 3)),
        hours=hours,
        text=text,
        profile_svg=profile_svg,
        levels=SYNOPTIC_LEVELS,
        level_names=LEVEL_NAMES,
        error=None,
        is_point=True,
    )


# ------------------------------------------------------------------
# Проверка моделей
# ------------------------------------------------------------------
@app.route("/verify/<station_key>")
def verify_page(station_key):
    """Сравнение моделей с фактом за N дней."""
    if station_key not in STATIONS:
        return "Станция не найдена", 404

    s = STATIONS[station_key]
    lat, lon = s["lat"], s["lon"]
    station_name = s["name"]

    try:
        days = int(request.args.get("days", 14))
    except (TypeError, ValueError):
        days = 14
    days = max(1, min(days, 30))

    selected_model = request.args.get("model", "")

    try:
        station_info = check_station_availability(lat, lon)
    except Exception as e:
        log.warning("check_station_availability error: %s", e)
        station_info = {"available": False, "reason": str(e)}

    models_stats = []
    for model_key in MODELS:
        try:
            stats = analyze_period(model_key, lat, lon, days=days)
        except Exception as e:
            log.exception("analyze_period failed for %s: %s", model_key, e)
            stats = {
                "error": str(e),
                "model": model_key,
                "model_name": MODELS[model_key]["name"],
            }
        stats["model_key"] = model_key
        models_stats.append(stats)

    detail = None
    if selected_model and selected_model in MODELS:
        for st in models_stats:
            if st.get("model_key") == selected_model:
                detail = st
                break

    return render_template_string(
        VERIFY_HTML,
        station_key=station_key,
        station_name=station_name,
        lat=lat, lon=lon,
        days=days,
        days_options=[7, 14, 30],
        models_stats=models_stats,
        selected_model=selected_model,
        detail=detail,
        station_info=station_info,
        history_days=HISTORY_DAYS,
        MODELS=MODELS,
        STATIONS=STATIONS,
    )


@app.route("/verify/<station_key>/history")
def verify_history_page(station_key):
    """История ошибок по дням: MAE и Bias для каждой модели."""
    if station_key not in STATIONS:
        return "Станция не найдена", 404

    s = STATIONS[station_key]
    lat, lon = s["lat"], s["lon"]
    station_name = s["name"]

    try:
        days = int(request.args.get("days", 14))
    except (TypeError, ValueError):
        days = 14
    days = max(3, min(days, 30))

    per_model = {}
    dates_union = []

    for model_key in MODELS:
        try:
            result = analyze_by_day(model_key, lat, lon, days=days)
        except Exception as e:
            log.exception("verify_history: %s error: %s", model_key, e)
            per_model[model_key] = {
                "model_name": MODELS[model_key]["name"],
                "color": _MODEL_COLORS.get(model_key, "#888"),
                "days": [],
                "error": str(e),
            }
            continue

        model_days = result.get("days", [])
        per_model[model_key] = {
            "model_name": MODELS[model_key]["name"],
            "color": _MODEL_COLORS.get(model_key, "#888"),
            "days": model_days,
            "summary": result.get("summary", {}),
            "error": None,
        }

        for d in model_days:
            if d["date"] not in dates_union:
                dates_union.append(d["date"])

    dates_union.sort()

    def build_series(field):
        out = []
        for mk, data in per_model.items():
            if data.get("error"):
                continue
            by_date = {d["date"]: d for d in data["days"]}
            values = []
            for date in dates_union:
                d = by_date.get(date)
                if d is None or d.get(field) is None:
                    values.append(None)
                else:
                    values.append(d[field])
            out.append({
                "key": mk,
                "name": data["model_name"],
                "color": data["color"],
                field: values,
            })
        return out

    mae_series = build_series("mae")
    bias_series = build_series("bias")
    rmse_series = build_series("rmse")

    svg_mae  = build_chart_svg(mae_series,  None, "mae",  "°C", "MAE по дням",  decimals=2)
    svg_bias = build_chart_svg(bias_series, None, "bias", "°C", "Bias по дням", decimals=2)
    svg_rmse = build_chart_svg(rmse_series, None, "rmse", "°C", "RMSE по дням", decimals=2)

    table_rows = []
    for date in dates_union:
        for mk, data in per_model.items():
            if data.get("error"):
                continue
            by_date = {d["date"]: d for d in data["days"]}
            d = by_date.get(date)
            if d is None:
                continue
            table_rows.append({
                "date": date,
                "model_name": data["model_name"],
                "model_color": data["color"],
                "mae": d.get("mae"),
                "bias": d.get("bias"),
                "rmse": d.get("rmse"),
                "hours": d.get("hours", 0),
                "corr": d.get("corr"),
            })

    return render_template_string(
        VERIFY_HISTORY_HTML,
        station_key=station_key,
        station_name=station_name,
        lat=lat, lon=lon,
        days=days,
        days_options=[7, 14, 30],
        per_model=per_model,
        dates=dates_union,
        table_rows=table_rows,
        svg_mae=svg_mae,
        svg_bias=svg_bias,
        svg_rmse=svg_rmse,
        error=None,
    )


# ------------------------------------------------------------------
# Расширенный анализ
# ------------------------------------------------------------------
@app.route("/analyze/<station_key>")
def analyze_page(station_key):
    """Расширенный анализ: детальная статистика + по дням."""
    if station_key not in STATIONS:
        return "Станция не найдена", 404

    s = STATIONS[station_key]
    lat, lon = s["lat"], s["lon"]
    station_name = s["name"]

    try:
        days = int(request.args.get("days", 14))
    except (TypeError, ValueError):
        days = 14
    days = max(7, min(days, 30))

    selected_model = request.args.get("model", "gfs")
    if selected_model not in MODELS:
        selected_model = "gfs"

    try:
        detail_stats = analyze_period(selected_model, lat, lon, days=days)
        detail_stats["model_key"] = selected_model
    except Exception as e:
        log.exception("analyze_period failed for %s: %s", selected_model, e)
        detail_stats = {
            "error": str(e),
            "model": selected_model,
            "model_name": MODELS[selected_model]["name"],
            "model_key": selected_model,
        }

    try:
        by_day = analyze_by_day(selected_model, lat, lon, days=days)
    except Exception as e:
        log.exception("analyze_by_day failed: %s", e)
        by_day = {"days": [], "summary": {}, "error": str(e)}

    compare_stats = []
    for model_key in MODELS:
        try:
            st = analyze_period(model_key, lat, lon, days=days)
            st["model_key"] = model_key
            compare_stats.append(st)
        except Exception as e:
            log.warning("analyze_period failed for %s: %s", model_key, e)
            compare_stats.append({
                "model_key": model_key,
                "model_name": MODELS[model_key]["name"],
                "error": str(e),
            })

    try:
        station_info = check_station_availability(lat, lon)
    except Exception as e:
        station_info = {"available": False, "reason": str(e)}

    return render_template_string(
        ANALYZE_HTML,
        station_key=station_key,
        station_name=station_name,
        lat=lat, lon=lon,
        days=days,
        days_options=[7, 14, 30],
        selected_model=selected_model,
        detail=detail_stats,
        by_day=by_day,
        compare_stats=compare_stats,
        station_info=station_info,
        MODELS=MODELS,
        STATIONS=STATIONS,
    )


# ------------------------------------------------------------------
# Авиация (станция)
# ------------------------------------------------------------------
@app.route("/aviation/<model_key>/<station_key>")
def aviation_page(model_key, station_key):
    """Авиационные прогнозы: Вайтинг, LI, CAPE, туман по Кирюхину."""
    if model_key not in MODELS:
        return "Модель не найдена", 404
    if station_key not in STATIONS:
        return "Станция не найдена", 404

    s = STATIONS[station_key]
    lat, lon = s["lat"], s["lon"]
    station_name = s["name"]
    model_name = MODELS[model_key]["name"]

    try:
        days = int(request.args.get("days", 3))
    except (TypeError, ValueError):
        days = 3
    days = max(1, min(days, 7))

    model_switcher = [
        {"key": k, "name": v["name"], "active": (k == model_key)}
        for k, v in MODELS.items()
    ]

    try:
        raw = fetch_forecast(model_key, lat, lon, days=days)
        forecast = parse_hourly(raw)
        by_day = prepare_forecast_for_render(forecast)
    except Exception as e:
        log.exception("aviation_page: ошибка прогноза: %s", e)
        return render_template_string(
            AVIATION_HTML,
            model=model_key,
            model_name=model_name,
            station_name=station_name,
            station_key=station_key,
            lat=lat, lon=lon, days=days,
            days_list=[],
            model_switcher=model_switcher,
            days_options=[1, 2, 3, 5, 7],
            summary={},
            error=str(e),
            MODELS=MODELS,
            is_point=False,
        )

    summary = {
        "hours_total": 0,
        "thunder_hours": 0,
        "thunder_max_prob": 0,
        "thunder_max_level": "нет",
        "fog_hours": 0,
        "fog_max_prob": 0,
        "fog_max_level": "нет",
        "k_max": None,
        "li_min": None,
        "cape_max": None,
    }

    for h in forecast:
        summary["hours_total"] += 1

        avt = h.get("av_thunder") or {}
        if avt.get("combined_level") and avt["combined_level"] not in ("нет", "нет данных"):
            summary["thunder_hours"] += 1
        if avt.get("combined_prob") and avt["combined_prob"] > summary["thunder_max_prob"]:
            summary["thunder_max_prob"] = avt["combined_prob"]
            summary["thunder_max_level"] = avt.get("combined_level", "нет")

        avf = h.get("av_fog") or {}
        if avf.get("level") and avf["level"] not in ("нет", "нет данных"):
            summary["fog_hours"] += 1
        if avf.get("probability") and avf["probability"] > summary["fog_max_prob"]:
            summary["fog_max_prob"] = avf["probability"]
            summary["fog_max_level"] = avf.get("level", "нет")

        if avt.get("k") is not None:
            if summary["k_max"] is None or avt["k"] > summary["k_max"]:
                summary["k_max"] = avt["k"]
        if avt.get("li") is not None:
            if summary["li_min"] is None or avt["li"] < summary["li_min"]:
                summary["li_min"] = avt["li"]
        if avt.get("cape") is not None:
            if summary["cape_max"] is None or avt["cape"] > summary["cape_max"]:
                summary["cape_max"] = avt["cape"]

    days_list = []
    for day, rows in by_day.items():
        days_list.append({"date": day, "rows": rows})

    return render_template_string(
        AVIATION_HTML,
        model=model_key,
        model_name=model_name,
        station_name=station_name,
        station_key=station_key,
        lat=lat, lon=lon, days=days,
        days_list=days_list,
        model_switcher=model_switcher,
        days_options=[1, 2, 3, 5, 7],
        summary=summary,
        error=None,
        MODELS=MODELS,
        is_point=False,
    )


# ------------------------------------------------------------------
# Матрица альтернативных прогнозов
# ------------------------------------------------------------------
@app.route("/alt-verify")
def alt_verify_point():
    """Бинарная верификация явлений по точке."""
    lat = request.args.get("lat", type=float, default=55.75)
    lon = request.args.get("lon", type=float, default=37.62)
    name = request.args.get("name", "Точка")

    phenomenon = request.args.get("phenomenon", "fog")
    if phenomenon not in PHENOMENA:
        phenomenon = "fog"

    try:
        days = int(request.args.get("days", 14))
    except (TypeError, ValueError):
        days = 14
    days = max(1, min(days, 30))

    try:
        results = compare_all_models(lat, lon, phenomenon, days)
    except Exception as e:
        log.exception("alt_verify error: %s", e)
        results = []

    best_model = None
    for r in results:
        if r.get("criteria"):
            if best_model is None or (r["criteria"]["p"] or 0) > (best_model["criteria"]["p"] or 0):
                best_model = r

    return render_template_string(
        ALT_VERIFY_HTML,
        station_key="",
        title=name,
        lat=lat,
        lon=lon,
        models=MODELS,
        phenomena=PHENOMENA,
        phenomenon=phenomenon,
        days=days,
        days_options=[7, 14, 30],
        results=results,
        best_model_key=best_model["model_key"] if best_model else None,
    )


@app.route("/alt-verify/<station_key>")
def alt_verify_station(station_key):
    """Бинарная верификация явлений по станции."""
    if station_key not in STATIONS:
        return "Станция не найдена", 404

    s = STATIONS[station_key]
    lat, lon = s["lat"], s["lon"]
    name = s["name"]

    phenomenon = request.args.get("phenomenon", "fog")
    if phenomenon not in PHENOMENA:
        phenomenon = "fog"

    try:
        days = int(request.args.get("days", 14))
    except (TypeError, ValueError):
        days = 14
    days = max(1, min(days, 30))

    try:
        results = compare_all_models(lat, lon, phenomenon, days)
    except Exception as e:
        log.exception("alt_verify error: %s", e)
        results = []

    best_model = None
    for r in results:
        if r.get("criteria"):
            if best_model is None or (r["criteria"]["p"] or 0) > (best_model["criteria"]["p"] or 0):
                best_model = r

    return render_template_string(
        ALT_VERIFY_HTML,
        station_key=station_key,
        title=name,
        lat=lat,
        lon=lon,
        models=MODELS,
        phenomena=PHENOMENA,
        phenomenon=phenomenon,
        days=days,
        days_options=[7, 14, 30],
        results=results,
        best_model_key=best_model["model_key"] if best_model else None,
    )


@app.route("/compare-matrices/<station_key>")
def compare_matrices_page(station_key):
    """Сравнение моделей по матрицам Хандожко для всех явлений."""
    if station_key not in STATIONS:
        return "Станция не найдена", 404

    s = STATIONS[station_key]
    lat, lon = s["lat"], s["lon"]
    station_name = s["name"]

    try:
        days = int(request.args.get("days", 14))
    except (TypeError, ValueError):
        days = 14
    days = max(3, min(days, 30))

    results_per_phenomenon = {}
    for ph_key in PHENOMENA:
        try:
            r = compare_all_models(lat, lon, ph_key, days)
        except Exception as e:
            log.exception("compare_matrices: %s error: %s", ph_key, e)
            r = []
        results_per_phenomenon[ph_key] = r

    best_per_phenomenon = {}
    for ph_key, results in results_per_phenomenon.items():
        best = None
        for r in results:
            cr = r.get("criteria")
            if cr and cr.get("p") is not None:
                if best is None or cr["p"] > best["criteria"]["p"]:
                    best = r
        best_per_phenomenon[ph_key] = best["model_key"] if best else None

    return render_template_string(
        COMPARE_MATRICES_HTML,
        station_key=station_key,
        station_name=station_name,
        lat=lat, lon=lon,
        days=days,
        days_options=[7, 14, 30],
        phenomena=PHENOMENA,
        results_per_phenomenon=results_per_phenomenon,
        best_per_phenomenon=best_per_phenomenon,
        error=None,
    )


# ------------------------------------------------------------------
# API
# ------------------------------------------------------------------
@app.route("/api/geocode")
def api_geocode():
    """Реальный geocoding через Open-Meteo Geocoding API."""
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"results": []})

    try:
        count = int(request.args.get("count", 8))
    except (TypeError, ValueError):
        count = 8
    count = max(1, min(count, 20))

    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": q,
            "count": count,
            "language": "ru",
            "format": "json",
        }
        r = _session.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        log.exception("geocode error: %s", e)
        return jsonify({"results": [], "error": str(e)})

    results = []
    for item in data.get("results", []):
        results.append({
            "name": item.get("name", ""),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
            "country": item.get("country", ""),
            "admin1": item.get("admin1", ""),
            "admin2": item.get("admin2", ""),
            "timezone": item.get("timezone", ""),
            "population": item.get("population"),
            "elevation": item.get("elevation"),
        })

    return jsonify({"results": results})


@app.route("/api/verify/<station_key>")
def api_verify(station_key):
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