# -*- coding: utf-8 -*-

"""

Flask-РїСЂРёР»РѕР¶РµРЅРёРµ weather-msk.

РњР°СЂС€СЂСѓС‚С‹ Рё API. РЁР°Р±Р»РѕРЅС‹ Р±РµСЂСѓС‚СЃСЏ РёР· templates.py.

"""



import json

import logging

from datetime import date, timedelta



from flask import Flask, render_template_string, request, jsonify

from tests_bank import TESTS

from ui import TESTS_HTML

from ui import (

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



# --- РјРѕРґСѓР»Рё РґР»СЏ С‚Р°Р±Р»РёС†С‹ РїСЂРѕРіРЅРѕР·Р° ---

from data.forecast import fetch_forecast

from analysis.parsing import parse_hourly, prepare_forecast_for_render

from analysis.synoptic import analyze_synoptic

from analysis.text_forecast import generate_text_forecast

from analysis.synoptic_level import (

    extract_levels, generate_synoptic_text, build_profile_svg,

    SYNOPTIC_LEVELS, LEVEL_NAMES,

)

from analysis.climate_indices import analyze_climate



# --- РјРѕРґСѓР»Рё РґР»СЏ РїСЂРѕРІРµСЂРєРё Рё Р°РЅР°Р»РёР·Р° ---

from data.actual import fetch_actual, check_station_availability, fetch_archive

from analysis.statistics import analyze_period, analyze_by_day



# --- РјРѕРґСѓР»Рё РґР»СЏ РјР°С‚СЂРёС† РҐР°РЅРґРѕР¶РєРѕ ---

from analysis.aviation_verify import compare_all_models



# --- РјРѕРґСѓР»Рё РґР»СЏ С‚СЂРѕРїРѕРїР°СѓР·С‹ ---

from data.tropopause_data import fetch_pressure_level_data

from analysis.tropopause import analyze_day

# --- РєР°СЂС‚С‹ РїРѕРіРѕРґС‹ (ICON-EU + GFS, Leaflet) ---

from maps_routes import maps_bp



from synoptic_maps.routes import synoptic_maps_bp

# ------------------------------------------------------------------

# Р›РѕРіРёСЂРѕРІР°РЅРёРµ

# ------------------------------------------------------------------

log = logging.getLogger("weather")

logging.basicConfig(level=logging.INFO)



app = Flask(__name__, static_folder="static", static_url_path="/static")







@app.route("/static/service-worker.js")

def service_worker():

    """Service Worker РґР»СЏ PWA."""

    return app.send_static_file("service-worker.js"), 200, {

        "Content-Type": "application/javascript",

        "Service-Worker-Allowed": "/",

    }

# === РџР»Р°РЅРёСЂРѕРІС‰РёРє РєР°СЂС‚ (С„РѕРЅРѕРІРѕРµ РѕР±РЅРѕРІР»РµРЅРёРµ) ===


import os as _os

from data.soundings import fetch_sounding, render_skewt_svg

from scheduler import init_scheduler
init_scheduler(app)



# ------------------------------------------------------------------

# Jinja-С„РёР»СЊС‚СЂС‹

# ------------------------------------------------------------------

@app.template_filter("date_ru")

def date_ru_filter(iso_date):

    """2024-01-15 -> 'РџРЅ, 15 СЏРЅРІР°СЂСЏ'."""

    from datetime import datetime

    months = ["января",
          "февраля",
          "марта",
          "апреля",
          "мая",
          "июня",
          "июля",
          "августа",
          "сентября",
          "октября",
          "ноября",
          "декабря"]
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    try:

        d = datetime.strptime(str(iso_date)[:10], "%Y-%m-%d")

        return f"{weekdays[d.weekday()]}, {d.day} {months[d.month - 1]}"

    except Exception:

        return str(iso_date)



app.register_blueprint(maps_bp)



app.register_blueprint(synoptic_maps_bp)

@app.template_filter("absval")

def absval_filter(value):

    """Р‘РµР·РѕРїР°СЃРЅРѕРµ Р°Р±СЃРѕР»СЋС‚РЅРѕРµ Р·РЅР°С‡РµРЅРёРµ РґР»СЏ СЃС‚Р°СЂС‹С… Jinja."""

    try:

        return abs(value)

    except Exception:

        return value





# ------------------------------------------------------------------

# Р’СЃРїРѕРјРѕРіР°С‚РµР»СЊРЅР°СЏ С„СѓРЅРєС†РёСЏ: РїРѕСЃС‚СЂРѕРµРЅРёРµ SVG-РіСЂР°С„РёРєР°

# ------------------------------------------------------------------

def build_chart_svg(series, fact_series, field, unit, title,

                    decimals=1, width=1400, height=320,

                    times_labels=None, step=1):

    """

    РЎС‚СЂРѕРёС‚ SVG-РіСЂР°С„РёРє РєР°Рє СЃС‚СЂРѕРєСѓ.



    series: СЃРїРёСЃРѕРє {key, name, color, temps, press, winds, precips}

    fact_series: {name, color, temps, press, winds, precips} | None

    field: 'temps' | 'press' | 'winds' | 'precips'

    times_labels: СЃРїРёСЃРѕРє РїРѕРґРїРёСЃРµР№ РїРѕ X

    step: РґРёСЃРєСЂРµС‚РЅРѕСЃС‚СЊ С‚РѕС‡РµРє

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

        return '<div class="empty-note">РќРµС‚ РґР°РЅРЅС‹С… РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ.</div>'



    if unit == "РіРџР°":

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

        return '<div class="empty-note">РќРµС‚ РґР°РЅРЅС‹С….</div>'

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

# РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ

# ------------------------------------------------------------------

try:

    from core.config import STATIONS as _STATIONS

    STATIONS = _STATIONS

except ImportError:

    STATIONS = {

        "tushino": {"name": "РўСѓС€РёРЅРѕ", "lat": 55.85, "lon": 37.44, "key": "tushino"},

    }



try:

    from core.config import MODELS as _MODELS

    MODELS = _MODELS

except ImportError:

    MODELS = {

        "gfs":   {"name": "GFS (РЎРЁРђ)"},

        "ecmwf": {"name": "ECMWF (Р•РІСЂРѕРїР°)"},

        "icon":  {"name": "ICON (Р“РµСЂРјР°РЅРёСЏ)"},

    }



PHENOMENA = {

    "frost":   {"name": "Р—Р°РјРѕСЂРѕР·РѕРє",     "unit": "В°C"},

    "wind":    {"name": "РЎРёР»СЊРЅС‹Р№ РІРµС‚РµСЂ", "unit": "Рј/СЃ"},

    "rain":    {"name": "РЎРёР»СЊРЅС‹Р№ РґРѕР¶РґСЊ", "unit": "РјРј"},

    "fog":     {"name": "РўСѓРјР°РЅ",         "unit": "РєРј"},

    "thunder": {"name": "Р“СЂРѕР·Р°",         "unit": "вЂ”"},

}



HISTORY_DAYS = 14



_MODEL_COLORS = {

    "gfs":   "#4dabff",

    "ecmwf": "#ffb547",

    "icon":  "#00e5a0",

}

_FACT_COLOR = "#a8b4d0"





# ------------------------------------------------------------------

# Р“Р»Р°РІРЅС‹Рµ СЃС‚СЂР°РЅРёС†С‹

# ------------------------------------------------------------------

@app.route("/")

def index():

    return render_template_string(INDEX_HTML)



@app.route("/tests")

def tests_page():

    """РЎС‚СЂР°РЅРёС†Р° С‚РµСЃС‚РѕРІ: РІС‹Р±РѕСЂ Р±Р»РѕРєР°, РїСЂРѕС…РѕР¶РґРµРЅРёРµ, СЂРµР·СѓР»СЊС‚Р°С‚."""

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

# РќРћР’Р«Р• Р РћРЈРўР«: С‚РµРѕСЂРёСЏ РїРѕ РіСЂСѓРїРїР°Рј + Р±РёР±Р»РёРѕРіСЂР°С„РёСЏ

# ------------------------------------------------------------------

@app.route("/bibliography")

def bibliography_page():

    """Р‘РёР±Р»РёРѕРіСЂР°С„РёСЏ: РёСЃС‚РѕС‡РЅРёРєРё РїРѕ РІСЃРµРј СЂР°Р·РґРµР»Р°Рј."""

    return render_template_string(

        BIBLIOGRAPHY_HTML,

        bibliography=BIBLIOGRAPHY_ITEMS,

    )





@app.route("/theory/methods")

def theory_methods():

    """РўРµРѕСЂРёСЏ: РјРµС‚РѕРґС‹ РїСЂРѕРіРЅРѕР·Р° (РёР·РѕСЌРЅС‚СЂРѕРїРёРєР°, PV, СЃРёРЅРѕРїС‚РёРєР°)."""

    return render_template_string(THEORY_METHODS_HTML)





@app.route("/theory/matrices")

def theory_matrices():

    """РўРµРѕСЂРёСЏ: РјР°С‚СЂРёС†С‹ СЃРѕРїСЂСЏР¶С‘РЅРЅРѕСЃС‚Рё Рё РєСЂРёС‚РµСЂРёРё РҐР°РЅРґРѕР¶РєРѕ."""

    return render_template_string(THEORY_MATRICES_HTML)





@app.route("/theory/indices")

def theory_indices():

    """РўРµРѕСЂРёСЏ: РёРЅРґРµРєСЃС‹ РЅРµСѓСЃС‚РѕР№С‡РёРІРѕСЃС‚Рё Рё СЏРІР»РµРЅРёСЏ."""

    return render_template_string(THEORY_INDICES_HTML)





# ------------------------------------------------------------------

# РљР°СЂС‚Р°, РѕР±СѓС‡РµРЅРёРµ, РєР»РёРјР°С‚

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

    """РљР»РёРјР°С‚РёС‡РµСЃРєРёРµ РёРЅРґРµРєСЃС‹: ENSO, SSW, PV."""

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

            period={"start": "вЂ”", "end": "вЂ”"},

            days_back=days_back,

            enso=None, ssw=None, pv=None,

            error=str(e),

        )



    return render_template_string(

        CLIMATE_HTML,

        period=data.get("period") or {"start": "вЂ”", "end": "вЂ”"},

        days_back=days_back,

        enso=data.get("enso"),

        ssw=data.get("ssw"),

        pv=data.get("pv"),

        error=data.get("error"),

    )





@app.route("/search")

def search():

    """РџРѕРёСЃРє С‚РѕС‡РєРё: geocoding РёР»Рё РєРѕРѕСЂРґРёРЅР°С‚С‹."""

    return render_template_string(

        SEARCH_HTML,

        models=MODELS,

        preset_lat=request.args.get("lat"),

        preset_lon=request.args.get("lon"),

        preset_name=request.args.get("name", ""),

    )





@app.route("/tropopause")

def tropopause_page():

    """РЎРєР»Р°РґРєРё С‚СЂРѕРїРѕРїР°СѓР·С‹: EPV, 2 PVU, РїСЂРѕС„РёР»СЊ."""

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

        log.exception("tropopause: РѕС€РёР±РєР° РґР°РЅРЅС‹С…: %s", e)

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

        log.exception("tropopause: РѕС€РёР±РєР° Р°РЅР°Р»РёР·Р°: %s", e)

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

# РњРѕРґРµР»Рё Рё СЃС‚Р°РЅС†РёРё

# ------------------------------------------------------------------

@app.route("/model/<model_key>")

def model_page(model_key):

    if model_key not in MODELS:

        return "РњРѕРґРµР»СЊ РЅРµ РЅР°Р№РґРµРЅР°", 404

    first = next(iter(STATIONS))

    return render_template_string(

        MODEL_HTML,

        model=model_key,

        model_name=MODELS[model_key]["name"],

        stations=STATIONS,

        first_station=first,

    )





# ------------------------------------------------------------------

# РўР°Р±Р»РёС†Р° РїСЂРѕРіРЅРѕР·Р°

# ------------------------------------------------------------------

@app.route("/forecast/<model_key>/<station_key>")

def forecast_table(model_key, station_key):

    """РўР°Р±Р»РёС†Р° РїСЂРѕРіРЅРѕР·Р° РїРѕ РјРѕРґРµР»Рё Рё СЃС‚Р°РЅС†РёРё."""

    if model_key not in MODELS:

        return "РњРѕРґРµР»СЊ РЅРµ РЅР°Р№РґРµРЅР°", 404

    if station_key not in STATIONS:

        return "РЎС‚Р°РЅС†РёСЏ РЅРµ РЅР°Р№РґРµРЅР°", 404



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

        log.exception("РћС€РёР±РєР° РїСЂРё РїРѕР»СѓС‡РµРЅРёРё РїСЂРѕРіРЅРѕР·Р°: %s", e)

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

    """РўРµРєСЃС‚РѕРІС‹Р№ РїСЂРѕРіРЅРѕР· РїРѕ РјРѕРґРµР»Рё Рё СЃС‚Р°РЅС†РёРё."""

    if model_key not in MODELS:

        return "РњРѕРґРµР»СЊ РЅРµ РЅР°Р№РґРµРЅР°", 404

    if station_key not in STATIONS:

        return "РЎС‚Р°РЅС†РёСЏ РЅРµ РЅР°Р№РґРµРЅР°", 404



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

        log.exception("forecast_text: РѕС€РёР±РєР° РїСЂРѕРіРЅРѕР·Р°: %s", e)

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

            text=f"РќРµ СѓРґР°Р»РѕСЃСЊ Р·Р°РіСЂСѓР·РёС‚СЊ РїСЂРѕРіРЅРѕР·: {e}",

            error=str(e),

            is_point=False,

        )



    try:

        text = generate_text_forecast(model_name, station_name, forecast)

    except Exception as e:

        log.exception("forecast_text: РѕС€РёР±РєР° РіРµРЅРµСЂР°С†РёРё С‚РµРєСЃС‚Р°: %s", e)

        text = f"РћС€РёР±РєР° РіРµРЅРµСЂР°С†РёРё С‚РµРєСЃС‚Р°: {e}"



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

# Р“СЂР°С„РёРє СЃСЂР°РІРЅРµРЅРёСЏ РјРѕРґРµР»РµР№ (СЃС‚Р°РЅС†РёСЏ)

# ------------------------------------------------------------------

@app.route("/chart/<station_key>")

def chart_page(station_key):

    """РЎСЂР°РІРЅРµРЅРёРµ РјРѕРґРµР»РµР№ РЅР° РіСЂР°С„РёРєРµ: T, P, РІРµС‚РµСЂ, РѕСЃР°РґРєРё."""

    if station_key not in STATIONS:

        return "РЎС‚Р°РЅС†РёСЏ РЅРµ РЅР°Р№РґРµРЅР°", 404



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

            error="РќРµ СѓРґР°Р»РѕСЃСЊ Р·Р°РіСЂСѓР·РёС‚СЊ РїСЂРѕРіРЅРѕР·С‹. РџРѕРїСЂРѕР±СѓР№С‚Рµ РїРѕР·Р¶Рµ.",

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

                    "name": "ERA5 (С„Р°РєС‚)", "color": _FACT_COLOR,

                    "temps": f_temps, "press": f_press,

                    "winds": f_winds, "precips": f_precips,

                }

    except Exception as e:

        log.warning("chart_page: ERA5 РЅРµ Р·Р°РіСЂСѓР¶РµРЅ: %s", e)



    days_map = {}

    for i, t in enumerate(times_global):

        d = t[:10]

        if d not in days_map:

            days_map[d] = {"date": d, "start_idx": i, "end_idx": i}

        else:

            days_map[d]["end_idx"] = i



    days_list = list(days_map.values())

    times_labels = [t[11:16] for t in times_global]



    svg_temps = build_chart_svg(series, fact_series, "temps", "В°C", "РўРµРјРїРµСЂР°С‚СѓСЂР°",

                                decimals=1, times_labels=times_labels, step=step)

    svg_press = build_chart_svg(series, fact_series, "press", "РіРџР°", "Р”Р°РІР»РµРЅРёРµ",

                                decimals=0, times_labels=times_labels, step=step)

    svg_winds = build_chart_svg(series, fact_series, "winds", "Рј/СЃ", "Р’РµС‚РµСЂ",

                                decimals=0, times_labels=times_labels, step=step)

    svg_prec  = build_chart_svg(series, fact_series, "precips", "РјРј", "РћСЃР°РґРєРё",

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

    """РЎРІРѕРґРєР° СЏРІР»РµРЅРёР№ РґР»СЏ РїСЂРѕРёР·РІРѕР»СЊРЅРѕР№ С‚РѕС‡РєРё (РїРѕ РєРѕРѕСЂРґРёРЅР°С‚Р°Рј РёР»Рё РЅР°Р·РІР°РЅРёСЋ)."""

    lat = request.args.get("lat", type=float)

    lon = request.args.get("lon", type=float)

    name = request.args.get("name", "").strip()



    # Р•СЃР»Рё РєРѕРѕСЂРґРёРЅР°С‚С‹ РЅРµ РїРµСЂРµРґР°РЅС‹ вЂ” РїРѕРєР°Р·С‹РІР°РµРј С‚РѕР»СЊРєРѕ С„РѕСЂРјСѓ РїРѕРёСЃРєР°

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



    # РЇРІР»РµРЅРёСЏ вЂ” С‚Рµ Р¶Рµ, С‡С‚Рѕ РІ compare_page

    PHENOMENA_LIST = [

        ("fog",     "РўСѓРјР°РЅ",         "рџЊ«", lambda h: h.get("weather_code") in (45, 48)),

        ("thunder", "Р“СЂРѕР·Р°",         "вљЎ", lambda h: h.get("weather_code") in (95, 96, 99)),

        ("rain",    "РћСЃР°РґРєРё",        "рџЊ§", lambda h: (h.get("precipitation_mm") or 0) > 0.05),

        ("snow",    "РЎРЅРµРі",          "вќ„пёЏ", lambda h: h.get("weather_code") in (71, 73, 75, 77, 85, 86)),

        ("frost",   "Р—Р°РјРѕСЂРѕР·РѕРє",     "рџҐ¶", lambda h: h.get("temp_c") is not None and h.get("temp_c") < 0),

        ("wind",    "РЎРёР»СЊРЅС‹Р№ РІРµС‚РµСЂ", "рџ’Ё", lambda h: (h.get("wind_ms") or 0) >= 12.0),

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

# РўРѕС‡РєР°: С‚Р°Р±Р»РёС†Р°, С‚РµРєСЃС‚, Р°РІРёР°С†РёСЏ, РіСЂР°С„РёРє

# ------------------------------------------------------------------

@app.route("/forecast/point")

def forecast_point():

    """РўР°Р±Р»РёС†Р° РїСЂРѕРіРЅРѕР·Р° РґР»СЏ РїСЂРѕРёР·РІРѕР»СЊРЅРѕР№ С‚РѕС‡РєРё."""

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

    """РўРµРєСЃС‚РѕРІС‹Р№ РїСЂРѕРіРЅРѕР· РґР»СЏ РїСЂРѕРёР·РІРѕР»СЊРЅРѕР№ С‚РѕС‡РєРё."""

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

        text = f"РќРµ СѓРґР°Р»РѕСЃСЊ СЃРіРµРЅРµСЂРёСЂРѕРІР°С‚СЊ РїСЂРѕРіРЅРѕР·: {e}"



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

    """РђРІРёР°С†РёРѕРЅРЅС‹Р№ РїСЂРѕРіРЅРѕР· РґР»СЏ РїСЂРѕРёР·РІРѕР»СЊРЅРѕР№ С‚РѕС‡РєРё."""

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

        "thunder_max_level": "РЅРµС‚",

        "fog_hours": 0,

        "fog_max_prob": 0,

        "fog_max_level": "РЅРµС‚",

        "k_max": None,

        "li_min": None,

        "cape_max": None,

    }



    for h in forecast:

        summary["hours_total"] += 1



        avt = h.get("av_thunder") or {}

        if avt.get("combined_level") and avt["combined_level"] not in ("РЅРµС‚", "РЅРµС‚ РґР°РЅРЅС‹С…"):

            summary["thunder_hours"] += 1

        if avt.get("combined_prob") and avt["combined_prob"] > summary["thunder_max_prob"]:

            summary["thunder_max_prob"] = avt["combined_prob"]

            summary["thunder_max_level"] = avt.get("combined_level", "РЅРµС‚")



        avf = h.get("av_fog") or {}

        if avf.get("level") and avf["level"] not in ("РЅРµС‚", "РЅРµС‚ РґР°РЅРЅС‹С…"):

            summary["fog_hours"] += 1

        if avf.get("probability") and avf["probability"] > summary["fog_max_prob"]:

            summary["fog_max_prob"] = avf["probability"]

            summary["fog_max_level"] = avf.get("level", "РЅРµС‚")



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

    """РЎСЂР°РІРЅРµРЅРёРµ РјРѕРґРµР»РµР№ РЅР° РіСЂР°С„РёРєРµ РґР»СЏ РїСЂРѕРёР·РІРѕР»СЊРЅРѕР№ С‚РѕС‡РєРё."""

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

            error="РќРµ СѓРґР°Р»РѕСЃСЊ Р·Р°РіСЂСѓР·РёС‚СЊ РїСЂРѕРіРЅРѕР·С‹. РџРѕРїСЂРѕР±СѓР№С‚Рµ РїРѕР·Р¶Рµ.",

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

                    "name": "ERA5 (С„Р°РєС‚)", "color": _FACT_COLOR,

                    "temps": f_temps, "press": f_press,

                    "winds": f_winds, "precips": f_precips,

                }

    except Exception as e:

        log.warning("point_chart: ERA5 РЅРµ Р·Р°РіСЂСѓР¶РµРЅ: %s", e)



    days_map = {}

    for i, t in enumerate(times_global):

        d = t[:10]

        if d not in days_map:

            days_map[d] = {"date": d, "start_idx": i, "end_idx": i}

        else:

            days_map[d]["end_idx"] = i



    days_list = list(days_map.values())

    times_labels = [t[11:16] for t in times_global]



    svg_temps = build_chart_svg(series, fact_series, "temps", "В°C", "РўРµРјРїРµСЂР°С‚СѓСЂР°",

                                decimals=1, times_labels=times_labels, step=step)

    svg_press = build_chart_svg(series, fact_series, "press", "РіРџР°", "Р”Р°РІР»РµРЅРёРµ",

                                decimals=0, times_labels=times_labels, step=step)

    svg_winds = build_chart_svg(series, fact_series, "winds", "Рј/СЃ", "Р’РµС‚РµСЂ",

                                decimals=0, times_labels=times_labels, step=step)

    svg_prec  = build_chart_svg(series, fact_series, "precips", "РјРј", "РћСЃР°РґРєРё",

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

# РЎРРќРћРџРўРРљРђ РџРћ РЈР РћР’РќРЇРњ

# ------------------------------------------------------------------

@app.route("/synoptic/<model_key>/<station_key>")

def synoptic_station(model_key, station_key):

    """РЎРёРЅРѕРїС‚РёС‡РµСЃРєРёР№ Р°РЅР°Р»РёР· РїРѕ СѓСЂРѕРІРЅСЏРј РґР»СЏ СЃС‚Р°РЅС†РёРё."""

    if model_key not in MODELS:

        return "РњРѕРґРµР»СЊ РЅРµ РЅР°Р№РґРµРЅР°", 404

    if station_key not in STATIONS:

        return "РЎС‚Р°РЅС†РёСЏ РЅРµ РЅР°Р№РґРµРЅР°", 404



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

    """РЎРёРЅРѕРїС‚РёС‡РµСЃРєРёР№ Р°РЅР°Р»РёР· РїРѕ СѓСЂРѕРІРЅСЏРј РґР»СЏ С‚РѕС‡РєРё."""

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

# РџСЂРѕРІРµСЂРєР° РјРѕРґРµР»РµР№

# ------------------------------------------------------------------

@app.route("/verify/<station_key>")

def verify_page(station_key):

    """РЎСЂР°РІРЅРµРЅРёРµ РјРѕРґРµР»РµР№ СЃ С„Р°РєС‚РѕРј Р·Р° N РґРЅРµР№."""

    if station_key not in STATIONS:

        return "РЎС‚Р°РЅС†РёСЏ РЅРµ РЅР°Р№РґРµРЅР°", 404



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

    """РСЃС‚РѕСЂРёСЏ РѕС€РёР±РѕРє РїРѕ РґРЅСЏРј: MAE Рё Bias РґР»СЏ РєР°Р¶РґРѕР№ РјРѕРґРµР»Рё."""

    if station_key not in STATIONS:

        return "РЎС‚Р°РЅС†РёСЏ РЅРµ РЅР°Р№РґРµРЅР°", 404



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



    svg_mae  = build_chart_svg(mae_series,  None, "mae",  "В°C", "MAE РїРѕ РґРЅСЏРј",  decimals=2)

    svg_bias = build_chart_svg(bias_series, None, "bias", "В°C", "Bias РїРѕ РґРЅСЏРј", decimals=2)

    svg_rmse = build_chart_svg(rmse_series, None, "rmse", "В°C", "RMSE РїРѕ РґРЅСЏРј", decimals=2)



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

# Р Р°СЃС€РёСЂРµРЅРЅС‹Р№ Р°РЅР°Р»РёР·

# ------------------------------------------------------------------

@app.route("/analyze/<station_key>")

def analyze_page(station_key):

    """Р Р°СЃС€РёСЂРµРЅРЅС‹Р№ Р°РЅР°Р»РёР·: РґРµС‚Р°Р»СЊРЅР°СЏ СЃС‚Р°С‚РёСЃС‚РёРєР° + РїРѕ РґРЅСЏРј."""

    if station_key not in STATIONS:

        return "РЎС‚Р°РЅС†РёСЏ РЅРµ РЅР°Р№РґРµРЅР°", 404



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

# РђРІРёР°С†РёСЏ (СЃС‚Р°РЅС†РёСЏ)

# ------------------------------------------------------------------

@app.route("/aviation/<model_key>/<station_key>")

def aviation_page(model_key, station_key):

    """РђРІРёР°С†РёРѕРЅРЅС‹Рµ РїСЂРѕРіРЅРѕР·С‹: Р’Р°Р№С‚РёРЅРі, LI, CAPE, С‚СѓРјР°РЅ РїРѕ РљРёСЂСЋС…РёРЅСѓ."""

    if model_key not in MODELS:

        return "РњРѕРґРµР»СЊ РЅРµ РЅР°Р№РґРµРЅР°", 404

    if station_key not in STATIONS:

        return "РЎС‚Р°РЅС†РёСЏ РЅРµ РЅР°Р№РґРµРЅР°", 404



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

        log.exception("aviation_page: РѕС€РёР±РєР° РїСЂРѕРіРЅРѕР·Р°: %s", e)

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

        "thunder_max_level": "РЅРµС‚",

        "fog_hours": 0,

        "fog_max_prob": 0,

        "fog_max_level": "РЅРµС‚",

        "k_max": None,

        "li_min": None,

        "cape_max": None,

    }



    for h in forecast:

        summary["hours_total"] += 1



        avt = h.get("av_thunder") or {}

        if avt.get("combined_level") and avt["combined_level"] not in ("РЅРµС‚", "РЅРµС‚ РґР°РЅРЅС‹С…"):

            summary["thunder_hours"] += 1

        if avt.get("combined_prob") and avt["combined_prob"] > summary["thunder_max_prob"]:

            summary["thunder_max_prob"] = avt["combined_prob"]

            summary["thunder_max_level"] = avt.get("combined_level", "РЅРµС‚")



        avf = h.get("av_fog") or {}

        if avf.get("level") and avf["level"] not in ("РЅРµС‚", "РЅРµС‚ РґР°РЅРЅС‹С…"):

            summary["fog_hours"] += 1

        if avf.get("probability") and avf["probability"] > summary["fog_max_prob"]:

            summary["fog_max_prob"] = avf["probability"]

            summary["fog_max_level"] = avf.get("level", "РЅРµС‚")



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

# РњР°С‚СЂРёС†Р° Р°Р»СЊС‚РµСЂРЅР°С‚РёРІРЅС‹С… РїСЂРѕРіРЅРѕР·РѕРІ

# ------------------------------------------------------------------

@app.route("/alt-verify")

def alt_verify_point():

    """Р‘РёРЅР°СЂРЅР°СЏ РІРµСЂРёС„РёРєР°С†РёСЏ СЏРІР»РµРЅРёР№ РїРѕ С‚РѕС‡РєРµ."""

    lat = request.args.get("lat", type=float, default=55.75)

    lon = request.args.get("lon", type=float, default=37.62)

    name = request.args.get("name", "РўРѕС‡РєР°")



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

    """Р‘РёРЅР°СЂРЅР°СЏ РІРµСЂРёС„РёРєР°С†РёСЏ СЏРІР»РµРЅРёР№ РїРѕ СЃС‚Р°РЅС†РёРё."""

    if station_key not in STATIONS:

        return "РЎС‚Р°РЅС†РёСЏ РЅРµ РЅР°Р№РґРµРЅР°", 404



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

    """РЎСЂР°РІРЅРµРЅРёРµ РјРѕРґРµР»РµР№ РїРѕ РјР°С‚СЂРёС†Р°Рј РҐР°РЅРґРѕР¶РєРѕ РґР»СЏ РІСЃРµС… СЏРІР»РµРЅРёР№."""

    if station_key not in STATIONS:

        return "РЎС‚Р°РЅС†РёСЏ РЅРµ РЅР°Р№РґРµРЅР°", 404



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

    """Р РµР°Р»СЊРЅС‹Р№ geocoding С‡РµСЂРµР· Open-Meteo Geocoding API."""

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

    return jsonify({"error": "РќРµ СЂРµР°Р»РёР·РѕРІР°РЅРѕ"})





@app.route("/api/analyze/<station_key>")

def api_analyze(station_key):

    return jsonify({"error": "РќРµ СЂРµР°Р»РёР·РѕРІР°РЅРѕ"})





@app.route("/api/aviation/<model_key>/<station_key>")

def api_aviation(model_key, station_key):

    return jsonify({"error": "РќРµ СЂРµР°Р»РёР·РѕРІР°РЅРѕ"})





@app.route("/api/alt-verify")

def api_alt_verify():

    return jsonify({"error": "РќРµ СЂРµР°Р»РёР·РѕРІР°РЅРѕ"})





@app.route("/api/compare-matrices")

def api_compare_matrices():

    return jsonify({"error": "РќРµ СЂРµР°Р»РёР·РѕРІР°РЅРѕ"})





@app.route("/api/tropopause")

def api_tropopause():

    return jsonify({"error": "РќРµ СЂРµР°Р»РёР·РѕРІР°РЅРѕ"})





@app.route("/api/noaa/nearby")

def api_noaa_nearby():

    return jsonify({"stations": []})





@app.route("/api/noaa/historical")

def api_noaa_historical():

    return jsonify({"error": "РќРµ СЂРµР°Р»РёР·РѕРІР°РЅРѕ"})





# ------------------------------------------------------------------





# === Skew-T: РјР°СЂС€СЂСѓС‚ СЃ SVG + tooltip (v3) ===





# SOUNDING_VIEW_FSTRING_V3_1

def sounding_view(station):

    """Страница Skew-T: SVG-диаграмма + tooltip. Без Jinja2 (f-string)."""

    import json as _json



    df = fetch_sounding(station.upper())

    if df is None:

        return f"<h1>Нет данных для станции {station.upper()}</h1>", 404



    svg, points = render_skewt_svg(df, station=station.upper(), ts=None)

    points_json = _json.dumps(points, ensure_ascii=False)



    return f"""<!DOCTYPE html>

<html lang="ru">

<head>

<meta charset="utf-8">

<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Skew-T — {station.upper()}</title>

<style>

  html, body {{

    margin: 0; padding: 0; background: #0a0e1a; color: #e8eefc;

    font-family: 'Inter', -apple-system, sans-serif;

  }}

  .wrap {{

    max-width: 1200px; margin: 0 auto; padding: 20px;

  }}

  .head {{

    display: flex; align-items: center; gap: 16px;

    margin-bottom: 16px;

  }}

  .head h1 {{ margin: 0; font-size: 20px; }}

  .head a {{

    color: #4dabff; text-decoration: none; font-size: 13px;

    padding: 6px 12px; border-radius: 8px;

    background: rgba(77,171,255,0.08);

    border: 1px solid rgba(77,171,255,0.2);

  }}

  .head a:hover {{ background: rgba(77,171,255,0.15); }}

  .skew-wrap {{

    position: relative;

    background: #ffffff;

    border-radius: 12px;

    padding: 8px;

    box-shadow: 0 20px 40px -20px rgba(77,171,255,0.4);

  }}

  .skew-wrap svg {{

    display: block; width: 100%; height: auto;

  }}

  .skew-wrap .hotspot {{

    position: absolute;

    width: 18px; height: 18px;

    border-radius: 50%;

    background: rgba(77,171,255,0);

    border: 1px solid rgba(77,171,255,0);

    cursor: crosshair;

    transition: background 0.15s, border-color 0.15s;

    transform: translate(-50%, -50%);

    pointer-events: auto;

    z-index: 5;

  }}

  .skew-wrap .hotspot:hover {{

    background: rgba(77,171,255,0.35);

    border-color: rgba(77,171,255,0.9);

  }}

  .tooltip {{

    position: fixed;

    pointer-events: none;

    z-index: 10000;

    background: rgba(10,14,26,0.97);

    border: 1px solid rgba(120,160,255,0.4);

    border-radius: 10px;

    padding: 10px 14px;

    font-size: 12px;

    font-family: 'JetBrains Mono', monospace;

    color: #e8eefc;

    box-shadow: 0 12px 30px rgba(0,0,0,0.5);

    display: none;

    white-space: nowrap;

    line-height: 1.75;

    min-width: 210px;

  }}

  .tooltip .tt-title {{

    font-family: 'Inter', sans-serif;

    font-weight: 700;

    font-size: 13px;

    color: #4dabff;

    margin-bottom: 6px;

  }}

  .tooltip .tt-row {{

    display: flex; justify-content: space-between; gap: 16px;

  }}

  .tooltip .tt-row span:first-child {{ color: #8892b0; }}

  .tooltip .tt-row span:last-child {{ font-weight: 600; }}

  .tooltip .tt-cold {{ color: #6bb6ff; }}

  .tooltip .tt-warm {{ color: #ffb547; }}

</style>

</head>

<body>

<div class="wrap">

  <div class="head">

    <a href="/">← На главную</a>

    <h1>Skew-T — {station.upper()}</h1>

  </div>

  <div class="skew-wrap" id="skew-wrap">

    {svg}

  </div>

</div>

<div class="tooltip" id="tt"></div>

<script>

(function() {{

  var POINTS = {points_json};

  var wrap = document.getElementById('skew-wrap');

  var tt = document.getElementById('tt');



  function pct_y(p_hpa) {{

    var p0 = 1000, p1 = 100;

    var v = (Math.log(p0) - Math.log(p_hpa)) / (Math.log(p0) - Math.log(p1));

    return v * 100;

  }}



  document.addEventListener('mousemove', function(e) {{

    if (tt.style.display !== 'block') return;

    var pad = 14;

    var x = e.clientX + pad, y = e.clientY + pad;

    if (x + tt.offsetWidth > window.innerWidth) x = e.clientX - tt.offsetWidth - pad;

    if (y + tt.offsetHeight > window.innerHeight) y = e.clientY - tt.offsetHeight - pad;

    tt.style.left = x + 'px';

    tt.style.top = y + 'px';

  }});



  function row(lbl, val, cls) {{

    cls = cls || '';

    return '<div class="tt-row"><span>' + lbl

      + '</span><span class="' + cls + '">' + val + '</span></div>';

  }}



  function buildTooltip(pt) {{

    var html = '<div class="tt-title">' + pt.p + ' гПа'

      + (pt.h !== null ? ' · ' + pt.h + ' м' : '') + '</div>';

    html += row('T',  pt.T + ' °C',  pt.T < 0 ? 'tt-cold' : 'tt-warm');

    html += row('Td', pt.Td + ' °C', 'tt-cold');

    html += row('RH', pt.RH + ' %');

    html += row('θ',  pt.theta + ' K');

    html += row('mr', pt.mixr + ' г/кг');

    html += row('Ветер', pt.wind);

    return html;

  }}



  setTimeout(function() {{

    var svg = wrap.querySelector('svg');

    if (!svg) return;

    POINTS.forEach(function(pt) {{

      var el = document.createElement('div');

      el.className = 'hotspot';

      var y_pct = pct_y(pt.p);

      var x_pct = 55 + (1 - y_pct / 100) * 15;

      el.style.left = x_pct + '%';

      el.style.top  = y_pct + '%';

      el.addEventListener('mouseenter', function() {{

        tt.innerHTML = buildTooltip(pt);

        tt.style.display = 'block';

      }});

      el.addEventListener('mouseleave', function() {{

        tt.style.display = 'none';

      }});

      wrap.appendChild(el);

    }});

  }}, 100);

}})();

</script>

</body>

</html>

"""





def sounding_view(station):

    """РЎС‚СЂР°РЅРёС†Р° Skew-T РґРёР°РіСЂР°РјРјС‹ РґР»СЏ СЃС‚Р°РЅС†РёРё Р·РѕРЅРґРёСЂРѕРІР°РЅРёСЏ (SVG + tooltip)."""

    df = fetch_sounding(station.upper())

    if df is None:

        return render_template_string(

            "<h1>РќРµС‚ РґР°РЅРЅС‹С… РґР»СЏ СЃС‚Р°РЅС†РёРё {{ s }}</h1>",

            s=station.upper(),

        ), 404



    svg, points = render_skewt_svg(df, station=station.upper(), ts=None)

    import json as _json

    return render_template_string(

        SOUNDING_TOOLTIP_HTML,

        station=station.upper(),

        svg=svg,

        points_json=_json.dumps(points, ensure_ascii=False),

    )

def sounding_view(station):

    """РЎС‚СЂР°РЅРёС†Р° Skew-T РґРёР°РіСЂР°РјРјС‹ РґР»СЏ СЃС‚Р°РЅС†РёРё Р·РѕРЅРґРёСЂРѕРІР°РЅРёСЏ."""

    df = fetch_sounding(station.upper())

    if df is None:

        return render_template_string(

            "<h1>РќРµС‚ РґР°РЅРЅС‹С… РґР»СЏ СЃС‚Р°РЅС†РёРё {{ s }}</h1>",

            s=station.upper(),

        ), 404



    png_b64 = render_skewt(df)

    return render_template_string(

        '<!DOCTYPE html>'

        '<html><body style="background:#0a0e1a;'

        'display:flex;justify-content:center;align-items:center;'

        'min-height:100vh;margin:0;">'

        '<img src="data:image/png;base64,{{ png }}" '

        'style="max-width:100%;max-height:95vh;border-radius:12px;">'

        '</body></html>',

        png=png_b64,

    )





# SOUNDING_VIEW_FSTRING_V3_2

def sounding_view(station):

    """Страница Skew-T: SVG + tooltip. Без Jinja2 (f-string)."""

    import json as _json



    df = fetch_sounding(station.upper())

    if df is None:

        return f"<h1>Нет данных для станции {station.upper()}</h1>", 404



    svg, points = render_skewt_svg(df, station=station.upper(), ts=None)

    points_json = _json.dumps(points, ensure_ascii=False)



    return f"""<!DOCTYPE html>

<html lang="ru">

<head>

<meta charset="utf-8">

<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Skew-T — {station.upper()}</title>

<style>

  html, body {{ margin: 0; padding: 0; background: #0a0e1a; color: #e8eefc;

    font-family: 'Inter', -apple-system, sans-serif; }}

  .wrap {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}

  .head {{ display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }}

  .head h1 {{ margin: 0; font-size: 20px; }}

  .head a {{ color: #4dabff; text-decoration: none; font-size: 13px;

    padding: 6px 12px; border-radius: 8px;

    background: rgba(77,171,255,0.08); border: 1px solid rgba(77,171,255,0.2); }}

  .head a:hover {{ background: rgba(77,171,255,0.15); }}

  .skew-wrap {{ position: relative; background: #ffffff; border-radius: 12px;

    padding: 8px; box-shadow: 0 20px 40px -20px rgba(77,171,255,0.4); }}

  .skew-wrap svg {{ display: block; width: 100%; height: auto; }}

  .skew-wrap .hotspot {{ position: absolute; width: 18px; height: 18px;

    border-radius: 50%; background: rgba(77,171,255,0);

    border: 1px solid rgba(77,171,255,0); cursor: crosshair;

    transition: background 0.15s, border-color 0.15s;

    transform: translate(-50%, -50%); pointer-events: auto; z-index: 5; }}

  .skew-wrap .hotspot:hover {{ background: rgba(77,171,255,0.35);

    border-color: rgba(77,171,255,0.9); }}

  .tooltip {{ position: fixed; pointer-events: none; z-index: 10000;

    background: rgba(10,14,26,0.97); border: 1px solid rgba(120,160,255,0.4);

    border-radius: 10px; padding: 10px 14px; font-size: 12px;

    font-family: 'JetBrains Mono', monospace; color: #e8eefc;

    box-shadow: 0 12px 30px rgba(0,0,0,0.5); display: none;

    white-space: nowrap; line-height: 1.75; min-width: 210px; }}

  .tooltip .tt-title {{ font-family: 'Inter', sans-serif; font-weight: 700;

    font-size: 13px; color: #4dabff; margin-bottom: 6px; }}

  .tooltip .tt-row {{ display: flex; justify-content: space-between; gap: 16px; }}

  .tooltip .tt-row span:first-child {{ color: #8892b0; }}

  .tooltip .tt-row span:last-child {{ font-weight: 600; }}

  .tooltip .tt-cold {{ color: #6bb6ff; }}

  .tooltip .tt-warm {{ color: #ffb547; }}

</style>

</head>

<body>

<div class="wrap">

  <div class="head">

    <a href="/">← На главную</a>

    <h1>Skew-T — {station.upper()}</h1>

  </div>

  <div class="skew-wrap" id="skew-wrap">{svg}</div>

</div>

<div class="tooltip" id="tt"></div>

<script>

(function() {{

  var POINTS = {points_json};

  var wrap = document.getElementById('skew-wrap');

  var tt = document.getElementById('tt');



  function pct_y(p_hpa) {{

    var p0 = 1000, p1 = 100;

    var v = (Math.log(p0) - Math.log(p_hpa)) / (Math.log(p0) - Math.log(p1));

    return v * 100;

  }}



  document.addEventListener('mousemove', function(e) {{

    if (tt.style.display !== 'block') return;

    var pad = 14;

    var x = e.clientX + pad, y = e.clientY + pad;

    if (x + tt.offsetWidth > window.innerWidth) x = e.clientX - tt.offsetWidth - pad;

    if (y + tt.offsetHeight > window.innerHeight) y = e.clientY - tt.offsetHeight - pad;

    tt.style.left = x + 'px'; tt.style.top = y + 'px';

  }});



  function row(lbl, val, cls) {{

    cls = cls || '';

    return '<div class="tt-row"><span>' + lbl

      + '</span><span class="' + cls + '">' + val + '</span></div>';

  }}



  function buildTooltip(pt) {{

    var html = '<div class="tt-title">' + pt.p + ' гПа'

      + (pt.h !== null ? ' · ' + pt.h + ' м' : '') + '</div>';

    html += row('T',  pt.T + ' °C',  pt.T < 0 ? 'tt-cold' : 'tt-warm');

    html += row('Td', pt.Td + ' °C', 'tt-cold');

    html += row('RH', pt.RH + ' %');

    html += row('θ',  pt.theta + ' K');

    html += row('mr', pt.mixr + ' г/кг');

    html += row('Ветер', pt.wind);

    return html;

  }}



  setTimeout(function() {{

    var svg = wrap.querySelector('svg');

    if (!svg) return;

    POINTS.forEach(function(pt) {{

      var el = document.createElement('div');

      el.className = 'hotspot';

      var y_pct = pct_y(pt.p);

      var x_pct = 55 + (1 - y_pct / 100) * 15;

      el.style.left = x_pct + '%';

      el.style.top  = y_pct + '%';

      el.addEventListener('mouseenter', function() {{

        tt.innerHTML = buildTooltip(pt);

        tt.style.display = 'block';

      }});

      el.addEventListener('mouseleave', function() {{

        tt.style.display = 'none';

      }});

      wrap.appendChild(el);

    }});

  }}, 100);

}})();

</script>

</body>

</html>

"""







# SOUNDING_VIEW_FSTRING_V4

@app.route("/sounding/<station>")

def sounding_view(station):

    """Страница Skew-T: SVG + tooltip с точными координатами."""

    import json as _json



    df = fetch_sounding(station.upper())

    if df is None:

        return f"<h1>Нет данных для станции {station.upper()}</h1>", 404



    svg, points = render_skewt_svg(df, station=station.upper(), ts=None)

    points_json = _json.dumps(points, ensure_ascii=False)



    return f"""<!DOCTYPE html>

<html lang="ru">

<head>

<meta charset="utf-8">

<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Skew-T — {station.upper()}</title>

<style>

  html, body {{ margin: 0; padding: 0; background: #0a0e1a; color: #e8eefc;

    font-family: 'Inter', -apple-system, sans-serif; }}

  .wrap {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}

  .head {{ display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }}

  .head h1 {{ margin: 0; font-size: 20px; }}

  .head a {{ color: #4dabff; text-decoration: none; font-size: 13px;

    padding: 6px 12px; border-radius: 8px;

    background: rgba(77,171,255,0.08); border: 1px solid rgba(77,171,255,0.2); }}

  .head a:hover {{ background: rgba(77,171,255,0.15); }}

  .skew-wrap {{ position: relative; background: #ffffff; border-radius: 12px;

    padding: 8px; box-shadow: 0 20px 40px -20px rgba(77,171,255,0.4); }}

  .skew-wrap svg {{ display: block; width: 100%; height: auto; }}

  .skew-wrap .hotspot {{ position: absolute; width: 16px; height: 16px;

    border-radius: 50%; background: rgba(77,171,255,0);

    border: 1px solid rgba(77,171,255,0.35); cursor: crosshair;

    transition: background 0.15s, border-color 0.15s, transform 0.15s;

    transform: translate(-50%, -50%); pointer-events: auto; z-index: 5; }}

  .skew-wrap .hotspot:hover {{ background: rgba(77,171,255,0.55);

    border-color: rgba(77,171,255,1); transform: translate(-50%, -50%) scale(1.3); }}

  .tooltip {{ position: fixed; pointer-events: none; z-index: 10000;

    background: rgba(10,14,26,0.97); border: 1px solid rgba(120,160,255,0.4);

    border-radius: 10px; padding: 10px 14px; font-size: 12px;

    font-family: 'JetBrains Mono', monospace; color: #e8eefc;

    box-shadow: 0 12px 30px rgba(0,0,0,0.5); display: none;

    white-space: nowrap; line-height: 1.75; min-width: 210px; }}

  .tooltip .tt-title {{ font-family: 'Inter', sans-serif; font-weight: 700;

    font-size: 13px; color: #4dabff; margin-bottom: 6px; }}

  .tooltip .tt-row {{ display: flex; justify-content: space-between; gap: 16px; }}

  .tooltip .tt-row span:first-child {{ color: #8892b0; }}

  .tooltip .tt-row span:last-child {{ font-weight: 600; }}

  .tooltip .tt-cold {{ color: #6bb6ff; }}

  .tooltip .tt-warm {{ color: #ffb547; }}

</style>

</head>

<body>

<div class="wrap">

  <div class="head">

    <a href="/">← На главную</a>

    <h1>Skew-T — {station.upper()}</h1>

  </div>

  <div class="skew-wrap" id="skew-wrap">{svg}</div>

</div>

<div class="tooltip" id="tt"></div>

<script>

(function() {{

  var POINTS = {points_json};

  var wrap = document.getElementById('skew-wrap');

  var tt = document.getElementById('tt');



  document.addEventListener('mousemove', function(e) {{

    if (tt.style.display !== 'block') return;

    var pad = 14;

    var x = e.clientX + pad, y = e.clientY + pad;

    if (x + tt.offsetWidth > window.innerWidth) x = e.clientX - tt.offsetWidth - pad;

    if (y + tt.offsetHeight > window.innerHeight) y = e.clientY - tt.offsetHeight - pad;

    tt.style.left = x + 'px'; tt.style.top = y + 'px';

  }});



  function row(lbl, val, cls) {{

    cls = cls || '';

    return '<div class="tt-row"><span>' + lbl

      + '</span><span class="' + cls + '">' + val + '</span></div>';

  }}



  function buildTooltip(pt) {{

    var html = '<div class="tt-title">' + pt.p + ' гПа'

      + (pt.h !== null ? ' · ' + pt.h + ' м' : '') + '</div>';

    html += row('T',  pt.T + ' °C',  pt.T < 0 ? 'tt-cold' : 'tt-warm');

    html += row('Td', pt.Td + ' °C', 'tt-cold');

    html += row('RH', pt.RH + ' %');

    html += row('θ',  pt.theta + ' K');

    html += row('mr', pt.mixr + ' г/кг');

    html += row('Ветер', pt.wind);

    return html;

  }}



  setTimeout(function() {{

    var svg = wrap.querySelector('svg');

    if (!svg) return;

    POINTS.forEach(function(pt) {{

      if (pt.x_pct === null || pt.y_pct === null) return;

      var el = document.createElement('div');

      el.className = 'hotspot';

      el.style.left = pt.x_pct + '%';

      el.style.top  = pt.y_pct + '%';

      el.addEventListener('mouseenter', function() {{

        tt.innerHTML = buildTooltip(pt);

        tt.style.display = 'block';

      }});

      el.addEventListener('mouseleave', function() {{

        tt.style.display = 'none';

      }});

      wrap.appendChild(el);

    }});

  }}, 100);

}})();

</script>

</body>

</html>

"""











# SOUNDING_MAP_HTML_V1

from data.stations import get_stations, find_nearest_stations





@app.route("/sounding-map")

def sounding_map():

    """HTML-страница с картой станций зондирования."""

    return _SOUNDING_MAP_HTML





@app.route("/api/sounding/stations")

def api_sounding_stations():

    """JSON со всеми станциями Wyoming."""

    try:

        return jsonify({"stations": get_stations()})

    except Exception as e:

        return jsonify({"stations": [], "error": str(e)}), 500





@app.route("/api/sounding/nearest")

def api_sounding_nearest():

    """Ближайшие N станций к точке."""

    try:

        lat = float(request.args.get("lat"))

        lon = float(request.args.get("lon"))

    except (TypeError, ValueError):

        return jsonify({"error": "lat/lon required"}), 400

    try:

        n = int(request.args.get("n", 5))

    except (TypeError, ValueError):

        n = 5

    n = max(1, min(n, 20))

    try:

        return jsonify({"stations": find_nearest_stations(lat, lon, n=n)})

    except Exception as e:

        return jsonify({"stations": [], "error": str(e)}), 500





# SOUNDING_MAP_HTML_V2_FIXED

_SOUNDING_MAP_HTML = """<!DOCTYPE html>

<html lang="ru">

<head>

<meta charset="utf-8">

<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Карта зондирования</title>

<link rel="stylesheet" href="/static/leaflet/leaflet.css">

<script src="/static/leaflet/leaflet.js"></script>

<style>

  html, body { margin: 0; padding: 0; height: 100%; background: #0a0e1a;

    color: #e8eefc; font-family: 'Inter', -apple-system, sans-serif; }

  .layout { display: grid; grid-template-columns: 1fr 520px; height: 100vh; }

  @media (max-width: 900px) {

    .layout { grid-template-columns: 1fr; grid-template-rows: 45vh 55vh; }

  }

  #map { width: 100%; height: 100%; min-height: 300px; }

  .panel { background: #0f1524; border-left: 1px solid rgba(120,160,255,0.15);

    display: flex; flex-direction: column; overflow: hidden; }

  .panel-head { padding: 12px 16px; border-bottom: 1px solid rgba(120,160,255,0.15);

    display: flex; gap: 10px; align-items: center; }

  .panel-head input { flex: 1; padding: 9px 12px; border-radius: 8px;

    border: 1px solid rgba(120,160,255,0.25); background: #161d2f;

    color: #e8eefc; outline: none; font-size: 13px; }

  .panel-head input:focus { border-color: #4dabff; }

  .panel-head button { padding: 9px 14px; border-radius: 8px; border: none;

    background: linear-gradient(135deg, #4dabff, #7c5cff); color: #fff;

    cursor: pointer; font-weight: 600; font-size: 13px; }

  .panel-head button:hover { opacity: 0.9; }

  .stations-list { padding: 8px 12px; border-bottom: 1px solid rgba(120,160,255,0.15);

    max-height: 160px; overflow-y: auto; font-size: 12px; }

  .stations-list .item { display: flex; justify-content: space-between;

    padding: 6px 8px; border-radius: 6px; cursor: pointer; color: #a8b4d0;

    font-family: 'JetBrains Mono', monospace; }

  .stations-list .item:hover { background: rgba(77,171,255,0.1); color: #e8eefc; }

  .stations-list .item.active { background: rgba(77,171,255,0.25); color: #fff; }

  .stations-list .item .km { color: #6b7694; }

  #skew-frame { flex: 1; width: 100%; border: none; background: #0a0e1a; min-height: 300px; }

  .hint { padding: 10px 16px; font-size: 12px; color: #6b7694;

    border-bottom: 1px solid rgba(120,160,255,0.15); }

  /* Маркеры станций (divIcon) */

  .station-dot { width: 16px !important; height: 16px !important;

    background: radial-gradient(circle, #4dabff 0%, #4dabff 60%, rgba(77,171,255,0.4) 100%);

    border: 2px solid #fff; border-radius: 50%;

    box-shadow: 0 0 8px rgba(77,171,255,0.9);

    cursor: pointer; transition: transform 0.15s; }

  .station-dot:hover { transform: scale(1.3); }

  .station-label { display: none; }

</style>

</head>

<body>

<div class="layout">

  <div id="map"></div>

  <div class="panel">

    <div class="panel-head">

      <input id="q" type="text" placeholder="Москва, Лондон, Tokyo...">

      <button onclick="doSearch()">Найти</button>

    </div>

    <div class="hint" id="hint">Кликните по маркеру на карте или введите город</div>

    <div class="stations-list" id="nearest"></div>

    <iframe id="skew-frame" src="about:blank"></iframe>

  </div>

</div>

<script>

var map = L.map('map', { worldCopyJump: true }).setView([50, -20], 3);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {

  attribution: '&copy; OpenStreetMap', maxZoom: 19

}).addTo(map);



// 1. Форсируем пересчёт размера, когда DOM готов и CSS применён

setTimeout(function() {

  map.invalidateSize();

  map.setView([50, -20], 3);

}, 150);



// 2. Пересчитываем при изменении окна

window.addEventListener('resize', function() {

  map.invalidateSize();

});



var markers = {};



function makeIcon() {

  return L.divIcon({

    className: 'station-dot-wrap',

    html: '<div class="station-dot"></div>',

    iconSize: [16, 16],

    iconAnchor: [8, 8]

  });

}



// SOUNDING_MAP_LOADSTATIONS_V3

function loadStations() {

  fetch('/api/sounding/stations')

    .then(function(r){ return r.json(); })

    .then(function(data) {

      (data.stations || []).forEach(function(s) {

        var m = L.marker([s.lat, s.lon], {

          icon: makeIcon(),

          interactive: true,

          keyboard: false,

          riseOnHover: true

        }).addTo(map);

        m.bindTooltip(s.name + ' (' + s.station + ')',

                      { direction: 'top', offset: [0, -8] });

        // IIFE — чтобы code был свой у каждого обработчика

        m.on('click', (function(code) {

          return function(e) {

            L.DomEvent.stopPropagation(e);

            L.DomEvent.preventDefault(e);

            console.log('station clicked:', code);

            openStation(code);

          };

        })(s.station));

        markers[s.station] = m;

      });

      console.log('[sounding-map] loaded', (data.stations || []).length, 'stations');

    })

    .catch(function(err) {

      console.error('[sounding-map] loadStations error:', err);

    });

}



function openStation(code) {

  document.getElementById('skew-frame').src = '/sounding/' + code + '?t=' + Date.now();

  document.getElementById('hint').textContent = 'Станция: ' + code;

  document.querySelectorAll('.stations-list .item').forEach(function(el) {

    el.classList.toggle('active', el.dataset.code === code);

  });

}



function doSearch() {

  var q = document.getElementById('q').value.trim();

  if (!q) return;

  fetch('/api/geocode?q=' + encodeURIComponent(q))

    .then(function(r){ return r.json(); })

    .then(function(data) {

      var r0 = (data.results || [])[0];

      if (!r0) { document.getElementById('hint').textContent = 'Не найдено'; return; }

      var lat = r0.latitude, lon = r0.longitude;

      map.setView([lat, lon], 6);

      fetch('/api/sounding/nearest?lat=' + lat + '&lon=' + lon + '&n=8')

        .then(function(r){ return r.json(); })

        .then(function(d) {

          var box = document.getElementById('nearest');

          box.innerHTML = '';

          (d.stations || []).forEach(function(s) {

            var el = document.createElement('div');

            el.className = 'item';

            el.dataset.code = s.station;

            el.innerHTML = '<span>' + s.name + ' (' + s.station + ')</span>'

                         + '<span class="km">' + s.distance_km + ' км</span>';

            el.onclick = function() { openStation(s.station); };

            box.appendChild(el);

          });

          if (d.stations && d.stations.length) {

            openStation(d.stations[0].station);

          }

        });

    });

}



document.getElementById('q').addEventListener('keydown', function(e) {

  if (e.key === 'Enter') doSearch();

});



loadStations();

</script>

</body>

</html>

"""





if __name__ == "__main__":

    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)