# -*- coding: utf-8 -*-
"""Страницы прогнозов: таблица, текст, график, модель, поиск."""

from ui.styles import (
    BASE_STYLE,
    COMMON_JS,
    render_header,
    render_legend,
)
CHART_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>График — {{ station_name }}</title>
""" + BASE_STYLE + """
<style>
  .controls { display: flex; gap: 12px; flex-wrap: wrap; align-items: center;
    margin: 16px 0 20px 0; padding: 14px 18px;
    background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px;
    backdrop-filter: blur(14px); }
  .controls label { color: var(--text-1); font-size: 13px; }
  .controls a { padding: 8px 14px; border-radius: 10px; font-size: 13px;
    background: var(--bg-1); border: 1px solid var(--border);
    color: var(--text-0); text-decoration: none; transition: all 0.2s; }
  .controls a:hover { border-color: var(--border-hover); }
  .controls a.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25), rgba(124,92,255,0.25));
    border-color: var(--accent); }
  .legend { display: flex; gap: 16px; flex-wrap: wrap;
    padding: 12px 18px; margin-bottom: 16px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 14px; font-size: 13px; backdrop-filter: blur(14px); }
  .legend-item { display: flex; align-items: center; gap: 8px; }
  .legend-dot { display: inline-block; width: 14px; height: 14px; border-radius: 3px; }
  .legend-dot.fact { opacity: 0.6; }
  .chart-block { margin: 24px 0; padding: 20px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; backdrop-filter: blur(14px); }
  .chart-block h2 { margin: 0 0 16px 0; font-size: 18px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .chart-block svg { display: block; }
  .error-box { background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    border-radius: 12px; padding: 16px; color: #ff5470;
    margin: 16px 0; }
  .empty-note { color: var(--text-2); padding: 20px; font-size: 14px; }
</style>
</head>
<body>

""" + render_header("forecast") + """
<h1>📈 Сравнение моделей</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · {{ days }} дней</div>

{% if error %}
  <div class="error-box">⚠️ {{ error }}</div>
{% endif %}

<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    <a href="{% if is_point %}/point-chart?lat={{ lat }}&lon={{ lon }}&name={{ station_name }}&days={{ d }}&models={{ selected_models|join(',') }}&step={{ step }}{% else %}/chart/{{ station_key }}?days={{ d }}&models={{ selected_models|join(',') }}&step={{ step }}{% endif %}"
       class="{% if d == days %}active{% endif %}">{{ d }} дней</a>
  {% endfor %}

  <label style="margin-left:12px;">Модели:</label>
  {% for key, m in models.items() %}
    <a href="{% if is_point %}/point-chart?lat={{ lat }}&lon={{ lon }}&name={{ station_name }}&days={{ days }}&models={{ toggle_models[key]|join(',') }}&step={{ step }}{% else %}/chart/{{ station_key }}?days={{ days }}&models={{ toggle_models[key]|join(',') }}&step={{ step }}{% endif %}"
       class="{% if key in selected_models %}active{% endif %}">{{ m.name }}</a>
  {% endfor %}
</div>

<div class="controls">
  <label>Дискретность точек:</label>
  {% set cur_step = step|default(1)|int %}
  {% for s_val, s_label in [(1, '1 ч'), (3, '3 ч'), (6, '6 ч'), (12, '12 ч')] %}
    <a href="{% if is_point %}/point-chart?lat={{ lat }}&lon={{ lon }}&name={{ station_name }}&days={{ days }}&models={{ selected_models|join(',') }}&step={{ s_val }}{% else %}/chart/{{ station_key }}?days={{ days }}&models={{ selected_models|join(',') }}&step={{ s_val }}{% endif %}"
       class="{% if cur_step == s_val %}active{% endif %}">{{ s_label }}</a>
  {% endfor %}
</div>

{% if series and times %}
<div class="legend">
  {% for s in series %}
    <div class="legend-item">
      <span class="legend-dot" style="background:{{ s.color }};"></span>
      <span>{{ s.name }}</span>
    </div>
  {% endfor %}
  {% if fact_series %}
    <div class="legend-item">
      <span class="legend-dot fact" style="background:{{ fact_series.color }};"></span>
      <span>{{ fact_series.name }}</span>
    </div>
  {% endif %}
</div>

<div class="chart-block">
  <h2>🌡 Температура (°C)</h2>
  {{ svg_temps | safe }}
</div>

<div class="chart-block">
  <h2>📊 Давление (гПа)</h2>
  {{ svg_press | safe }}
</div>

<div class="chart-block">
  <h2>💨 Ветер (м/с)</h2>
  {{ svg_winds | safe }}
</div>

<div class="chart-block">
  <h2>🌧 Осадки (мм)</h2>
  {{ svg_prec | safe }}
</div>

{% else %}
  <div class="empty-note">Нет данных для отображения.</div>
{% endif %}

<div id="chart-tooltip" style="
  position:fixed; pointer-events:none; z-index:10000;
  background:var(--bg-0); border:1px solid var(--border);
  border-radius:8px; padding:8px 12px; font-size:13px;
  font-family:'JetBrains Mono', monospace; color:var(--text-0);
  box-shadow:0 8px 20px rgba(0,0,0,0.3); display:none;
  white-space:nowrap;
"></div>

<script>
(function() {
  var tt = document.getElementById('chart-tooltip');
  if (!tt) return;

  document.addEventListener('mouseover', function(e) {
    if (e.target.tagName !== 'circle') return;
    var t = e.target.getAttribute('data-time') || '';
    var v = e.target.getAttribute('data-value') || '';
    var u = e.target.getAttribute('data-unit') || '';
    var m = e.target.getAttribute('data-model') || '';
    tt.innerHTML = '<b>' + m + '</b><br>' + t + ' · <span style="color:#4dabff;">' + v + ' ' + u + '</span>';
    tt.style.display = 'block';
  });

  document.addEventListener('mousemove', function(e) {
    if (tt.style.display !== 'block') return;
    var pad = 12;
    var x = e.clientX + pad;
    var y = e.clientY + pad;
    if (x + tt.offsetWidth > window.innerWidth) x = e.clientX - tt.offsetWidth - pad;
    if (y + tt.offsetHeight > window.innerHeight) y = e.clientY - tt.offsetHeight - pad;
    tt.style.left = x + 'px';
    tt.style.top = y + 'px';
  });

  document.addEventListener('mouseout', function(e) {
    if (e.target.tagName === 'circle') tt.style.display = 'none';
  });
})();
</script>

""" + COMMON_JS +  render_legend("forecast") + """
</body>
</html>
"""




MODEL_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ model_name }}</title>
""" + BASE_STYLE + """
</head>
<body>
""" + render_header("forecast") + """
<h1>{{ model_name }}</h1>
<div class="sub">Выберите станцию</div>

{% for key, s in stations.items() %}
<a class="card fade-in" href="/forecast/{{ model }}/{{ key }}">
  <span class="icon">📍</span><b>{{ s.name }}</b>
  <div class="coords">{{ s.lat }}, {{ s.lon }}</div>
</a>
{% endfor %}

<a class="card fade-in" href="/chart/{{ first_station }}" style="background:rgba(124,92,255,0.10);">
  <span class="icon">📈</span><b>Сравнить модели на графике</b>
</a>

<a class="card fade-in" href="/aviation/{{ model }}/{{ first_station }}" style="background:rgba(255,181,71,0.10);">
  <span class="icon">✈️</span><b>Авиационный прогноз</b>
  <div class="desc">K (Вайтинг), LI, CAPE, туман по Кирюхину</div>
</a>

<a class="card fade-in" href="/synoptic/{{ model }}/{{ first_station }}" style="background:rgba(255,84,112,0.10);">
  <span class="icon">🌡</span><b>Синоптика по уровням</b>
  <div class="desc">Профиль T, θ, RH на 925–300 гПа</div>
</a>

""" + COMMON_JS +  """
</body>
</html>
"""




TABLE_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ station }} — {{ model_name }}</title>
""" + BASE_STYLE + """
<style>
  .model-switcher {
    display: flex; gap: 8px; margin: 16px 0; flex-wrap: wrap;
  }
  .model-switcher a {
    padding: 8px 16px; border-radius: 10px; text-decoration: none;
    font-size: 13px; font-weight: 600; transition: all 0.2s;
    background: var(--card-bg); border: 1px solid var(--border);
    color: var(--text-1);
  }
  .model-switcher a:hover { border-color: var(--border-hover); }
  .model-switcher a.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25), rgba(124,92,255,0.25));
    border-color: var(--accent); color: var(--text-0);
  }

  .day-block {
    margin: 24px 0; padding: 16px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; backdrop-filter: blur(14px);
  }
  .day-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 12px; padding-bottom: 10px;
    border-bottom: 1px solid var(--border); flex-wrap: wrap; gap: 8px;
  }
  .day-title { font-size: 16px; font-weight: 700; }
  .day-events { font-size: 12px; color: var(--text-2); }

  .hour-table {
    width: 100%; border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace; font-size: 12px;
  }
  .hour-table th {
    text-align: left; padding: 8px 6px; color: var(--text-2);
    font-weight: 600; font-size: 11px;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }
  .hour-table td {
    padding: 8px 6px; border-bottom: 1px solid rgba(120,160,255,0.06);
    vertical-align: middle;
  }
  .hour-table tr:hover td { background: rgba(77,171,255,0.05); }

  .hour-cell { font-weight: 700; color: var(--accent); }
  .temp-cell { font-weight: 600; }
  .temp-freeze { color: #a78bfa; }
  .temp-cold   { color: #6bb6ff; }
  .temp-warm   { color: #ffb547; }
  .temp-hot    { color: #ff5470; }
  .precip-yes  { color: #4dabff; font-weight: 700; }
  .wind-cell   { color: var(--text-1); }
  .icon-cell   { text-align: center; }
  .icon-cell svg { width: 28px; height: 28px; vertical-align: middle; }
  .spark-cell  { text-align: center; }

  .event-badge {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 10px; font-weight: 600; margin: 1px 2px 1px 0;
  }

  .summary-bar {
    display: flex; gap: 16px; flex-wrap: wrap; margin: 12px 0 20px 0;
    padding: 12px 16px; background: var(--card-bg);
    border: 1px solid var(--border); border-radius: 14px;
    font-size: 12px; color: var(--text-1);
  }
  .summary-item b { color: var(--text-0); font-family: 'JetBrains Mono', monospace; }

  .error-box {
    background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    border-radius: 12px; padding: 16px; color: #ff5470;
    margin: 16px 0;
  }

  /* [PATCH ui.forecast.day_summary] */
  .day-summary {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin: 8px 0 12px 0;
    padding: 10px 14px;
    background: rgba(77, 171, 255, 0.06);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    font-size: 13px;
    color: var(--text-1);
  }
  .day-summary .situation {
    font-weight: 700;
    color: var(--accent);
  }
  .day-summary .phenomena {
    color: var(--text-0);
  }

  @media (max-width: 900px) {
    .hour-table { font-size: 11px; }
    .hour-table th, .hour-table td { padding: 6px 3px; }
    .spark-cell { display: none; }
    .hour-table th:nth-child(6),
    .hour-table td:nth-child(6) { display: none; }
  }
</style>
</head>
<body>

""" + render_header("forecast") + """
<h1>{{ station }}</h1>
<div class="sub">{{ model_name }} · {{ lat }}, {{ lon }} · прогноз на {{ days }} дня</div>

{% if error %}
<div class="error-box">⚠️ Ошибка: {{ error }}</div>
{% endif %}

<div class="model-switcher">
  {% for m in model_switcher %}
    <a href="{% if is_point %}/forecast/point?lat={{ lat }}&lon={{ lon }}&name={{ station }}&model={{ m.key }}{% else %}/forecast/{{ m.key }}/{{ station_key }}{% endif %}"
       class="{% if m.active %}active{% endif %}">{{ m.name }}</a>
  {% endfor %}
  <a href="{% if is_point %}/point-text?lat={{ lat }}&lon={{ lon }}&name={{ station }}&model={{ model }}{% else %}/text/{{ model }}/{{ station_key }}{% endif %}">📝 Текст</a>
  <a href="{% if is_point %}/point-aviation?lat={{ lat }}&lon={{ lon }}&name={{ station }}&model={{ model }}{% else %}/aviation/{{ model }}/{{ station_key }}{% endif %}">✈️ Авиация</a>
  <a href="{% if is_point %}/point-chart?lat={{ lat }}&lon={{ lon }}&name={{ station }}{% else %}/chart/{{ station_key }}{% endif %}">📈 График</a>
  <a href="{% if is_point %}/point-synoptic?lat={{ lat }}&lon={{ lon }}&name={{ station }}&model={{ model }}{% else %}/synoptic/{{ model }}/{{ station_key }}{% endif %}">🌡 Синоптика</a>
</div>

{% if events %}
<div class="summary-bar">
  <div class="summary-item">Событий: <b>{{ events|length }}</b></div>
  {% set cold = events | selectattr("type", "equalto", "cold_front") | list | length %}
  {% set warm = events | selectattr("type", "equalto", "warm_front") | list | length %}
  {% set cyc  = events | selectattr("type", "equalto", "cyclone")    | list | length %}
  {% set anti = events | selectattr("type", "equalto", "anticyclone")| list | length %}
  {% set fold = events | selectattr("type", "equalto", "fold")       | list | length %}
  {% if cold %}<div class="summary-item">❄️ Холодных фронтов: <b>{{ cold }}</b></div>{% endif %}
  {% if warm %}<div class="summary-item">🔥 Тёплых фронтов: <b>{{ warm }}</b></div>{% endif %}
  {% if cyc  %}<div class="summary-item">🌀 Циклонов: <b>{{ cyc }}</b></div>{% endif %}
  {% if anti %}<div class="summary-item">🔆 Антициклонов: <b>{{ anti }}</b></div>{% endif %}
  {% if fold %}<div class="summary-item">📉 Складок: <b>{{ fold }}</b></div>{% endif %}
</div>
{% endif %}

{% for day in days_list %}
<div class="day-block fade-in">
  <div class="day-header">
    <div class="day-title">📅 {{ day.date | date_ru }}</div>
    <div class="day-events">
      {% for ev in day.events[:6] %}
        <span class="event-badge synoptic-{{ ev.type }}">{{ ev.text }}</span>
      {% endfor %}
    </div>
  </div>

  <!-- [PATCH ui.forecast.day_summary] -->
  {% if day.summary %}
  <div class="day-summary">
    <span class="situation">🌍 {{ day.summary.situation }}</span>
    <span class="phenomena">{{ day.summary.phenomena }}</span>
  </div>
  {% endif %}

  <div style="overflow-x:auto;">
  <table class="hour-table">
    <thead>
      <tr>
        <th>Час</th>
        <th>Иконка</th>
        <th>T, °C</th>
        <th>Td, °C</th>
        <th>P, гПа</th>
        <th>θ, K</th>
        <th>Ветер</th>
        <th>Порыв</th>
        <th>RH, %</th>
        <th>Обл, %</th>
        <th>Осадки</th>
        <th>Явление</th>
        <th>ΣT</th>
        <th>ΣP</th>
      </tr>
    </thead>
    <tbody>
      {% for h in day.rows %}
      <tr>
        <td class="hour-cell">{{ h.time[11:16] }}</td>
        <td class="icon-cell">{{ h.icon_svg | safe }}</td>
        <td class="temp-cell
          {% if h.temp_c is not none %}
            {% if h.temp_c < 0 %}temp-freeze
            {% elif h.temp_c < 10 %}temp-cold
            {% elif h.temp_c < 25 %}temp-warm
            {% else %}temp-hot{% endif %}
          {% endif %}">
          {{ '%.1f'|format(h.temp_c) if h.temp_c is not none else '—' }}
        </td>
        <td>{{ '%.1f'|format(h.dew_point_c) if h.dew_point_c is not none else '—' }}</td>
        <td>{{ '%.0f'|format(h.pressure_hpa) if h.pressure_hpa is not none else '—' }}</td>
        <td>{{ '%.1f'|format(h.theta_k) if h.theta_k is not none else '—' }}</td>
        <td class="wind-cell">
          {% if h.wind_ms is not none %}
            {{ '%.0f'|format(h.wind_ms) }} м/с {{ h.wind_dir_text or '' }}
          {% else %}—{% endif %}
        </td>
        <td class="wind-cell">{{ '%.0f'|format(h.wind_gust) if h.wind_gust is not none else '—' }}</td>
        <td>{{ '%.0f'|format(h.humidity) if h.humidity is not none else '—' }}</td>
        <td>{{ '%.0f'|format(h.cloud_cover) if h.cloud_cover is not none else '—' }}</td>
        <td class="{% if h.is_precip %}precip-yes{% endif %}">
          {{ '%.1f'|format(h.precipitation_mm) if h.precipitation_mm else '—' }}
        </td>
        <td>
          {% if h.is_thunder %}
            <span class="event-badge synoptic-cold_front">⚡ Гроза</span>
          {% endif %}
          {% if h.is_fog %}
            <span class="event-badge synoptic-anticyclone">🌫 Туман</span>
          {% endif %}
          {% if h.av_thunder and h.av_thunder.combined_level and h.av_thunder.combined_level != 'нет' %}
            <span class="event-badge synoptic-cyclone" title="{{ h.av_thunder.combined_text }} ({{ h.av_thunder.combined_prob }}%)">
              ✈️ грозы: {{ h.av_thunder.combined_level }}
            </span>
          {% endif %}
          {% if h.av_fog and h.av_fog.level and h.av_fog.level != 'нет' %}
            <span class="event-badge synoptic-warm_front" title="{{ h.av_fog.text }} ({{ h.av_fog.probability }}%)">
              ✈️ туман: {{ h.av_fog.level }}
            </span>
          {% endif %}
        </td>
        <td class="spark-cell">{{ h.temp_spark | safe }}</td>
        <td class="spark-cell">{{ h.press_spark | safe }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  </div>
</div>
{% endfor %}

{% if not days_list and not error %}
<div style="color:var(--text-2);padding:20px;">Нет данных для отображения.</div>
{% endif %}

""" + COMMON_JS +  render_legend("forecast") + """
</body>
</html>
"""




TEXT_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ station }} — текст — {{ model_name }}</title>
""" + BASE_STYLE + """
<style>
  .model-switcher {
    display: flex; gap: 8px; margin: 16px 0; flex-wrap: wrap;
  }
  .model-switcher a {
    padding: 8px 16px; border-radius: 10px; text-decoration: none;
    font-size: 13px; font-weight: 600; transition: all 0.2s;
    background: var(--card-bg); border: 1px solid var(--border);
    color: var(--text-1);
  }
  .model-switcher a:hover { border-color: var(--border-hover); }
  .model-switcher a.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25), rgba(124,92,255,0.25));
    border-color: var(--accent); color: var(--text-0);
  }

  .controls {
    display: flex; gap: 12px; flex-wrap: wrap; align-items: center;
    margin: 16px 0 20px 0; padding: 14px 18px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 14px; backdrop-filter: blur(14px);
  }
  .controls label { color: var(--text-1); font-size: 13px; }
  .controls a {
    padding: 8px 14px; border-radius: 10px; font-size: 13px;
    background: var(--bg-1); border: 1px solid var(--border);
    color: var(--text-0); text-decoration: none; transition: all 0.2s;
  }
  .controls a:hover { border-color: var(--border-hover); }
  .controls a.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25), rgba(124,92,255,0.25));
    border-color: var(--accent);
  }

  .text-block {
    padding: 24px 28px; border-radius: 16px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border); backdrop-filter: blur(14px);
    margin: 20px 0;
  }
  .text-block pre {
    white-space: pre-wrap; word-wrap: break-word;
    font-family: 'Inter', -apple-system, sans-serif;
    font-size: 15px; line-height: 1.85; margin: 0;
    color: var(--text-0);
  }

  .action-row {
    display: flex; gap: 12px; flex-wrap: wrap; margin-top: 20px;
  }
  .action-row a {
    padding: 10px 20px; border-radius: 12px; text-decoration: none;
    font-size: 13px; font-weight: 600; transition: all 0.2s;
    background: rgba(77,171,255,0.10); border: 1px solid rgba(77,171,255,0.3);
    color: var(--accent);
  }
  .action-row a:hover {
    background: rgba(77,171,255,0.20);
    border-color: var(--border-hover);
  }

  .error-box {
    background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    border-radius: 12px; padding: 16px; color: #ff5470;
    margin: 16px 0;
  }
</style>
</head>
<body>

""" + render_header("forecast") + """
<h1>📝 {{ station }}</h1>
<div class="sub">{{ model_name }} · текстовый прогноз на {{ days }} дн.</div>

{% if error %}
  <div class="error-box">⚠️ {{ error }}</div>
{% endif %}

<div class="model-switcher">
  {% for m in model_switcher %}
    <a href="{% if is_point %}/point-text?lat={{ lat }}&lon={{ lon }}&name={{ station }}&model={{ m.key }}{% else %}/text/{{ m.key }}/{{ station_key }}?days={{ days }}{% endif %}"
       class="{% if m.active %}active{% endif %}">{{ m.name }}</a>
  {% endfor %}
</div>

<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    <a href="{% if is_point %}/point-text?lat={{ lat }}&lon={{ lon }}&name={{ station }}&model={{ model }}&days={{ d }}{% else %}/text/{{ model }}/{{ station_key }}?days={{ d }}{% endif %}"
       class="{% if d == days %}active{% endif %}">{{ d }} дн.</a>
  {% endfor %}
</div>

<div class="text-block">
  <pre>{{ text }}</pre>
</div>

<div class="action-row">
  <a href="{% if is_point %}/forecast/point?lat={{ lat }}&lon={{ lon }}&name={{ station }}&model={{ model }}{% else %}/forecast/{{ model }}/{{ station_key }}{% endif %}">📊 Таблица</a>
  <a href="{% if is_point %}/point-chart?lat={{ lat }}&lon={{ lon }}&name={{ station }}&days={{ days }}{% else %}/chart/{{ station_key }}?days={{ days }}{% endif %}">📈 График</a>
  <a href="{% if is_point %}/point-aviation?lat={{ lat }}&lon={{ lon }}&name={{ station }}&model={{ model }}&days={{ days }}{% else %}/aviation/{{ model }}/{{ station_key }}?days={{ days }}{% endif %}">✈️ Авиация</a>
  <a href="{% if is_point %}/point-synoptic?lat={{ lat }}&lon={{ lon }}&name={{ station }}&model={{ model }}&days={{ days }}{% else %}/synoptic/{{ model }}/{{ station_key }}?days={{ days }}{% endif %}">🌡 Синоптика</a>
</div>

""" + COMMON_JS +  render_legend("forecast") + """
</body>
</html>
"""




SEARCH_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Поиск точки — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .search-box {
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 14px; padding: 16px; margin-bottom: 16px;
    backdrop-filter: blur(14px);
  }
  .search-row {
    display: flex; gap: 10px; flex-wrap: wrap;
    align-items: center; margin-bottom: 12px;
  }
  .search-row:last-child { margin-bottom: 0; }
  .search-row label { color: var(--text-1); font-size: 13px; min-width: 110px; }
  .search-row input, .search-row select {
    padding: 10px 14px; background: var(--bg-1);
    border: 1px solid var(--border); border-radius: 10px;
    color: var(--text-0); font-size: 14px; outline: none;
    transition: border-color 0.2s;
  }
  .search-row input:focus, .search-row select:focus {
    border-color: var(--accent);
  }
  .search-row input.q {
    flex: 1; min-width: 220px;
  }
  .search-row input.coord {
    width: 130px;
    font-family: 'JetBrains Mono', monospace;
  }
  .search-row button {
    padding: 10px 22px; border: none; border-radius: 10px;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff; cursor: pointer; font-size: 14px; font-weight: 600;
    transition: opacity 0.2s;
  }
  .search-row button:hover { opacity: 0.9; }
  .search-row button.secondary {
    background: var(--bg-1); color: var(--text-0);
    border: 1px solid var(--border);
  }

  .hint {
    font-size: 12px; color: var(--text-2); margin-top: 4px;
  }

  .results-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 12px; margin-top: 12px;
  }
  .result-card {
    padding: 14px 18px; border-radius: 14px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    transition: all 0.2s;
    backdrop-filter: blur(14px);
  }
  .result-card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--card-shadow);
  }
  .result-card .place {
    font-size: 16px; font-weight: 700; margin-bottom: 4px;
  }
  .result-card .meta {
    color: var(--text-2); font-size: 12px; margin-bottom: 10px;
    font-family: 'JetBrains Mono', monospace;
  }
  .result-card .actions {
    display: flex; gap: 6px; flex-wrap: wrap;
  }
  .result-card .actions a {
    padding: 6px 12px; border-radius: 8px; text-decoration: none;
    font-size: 12px; font-weight: 600;
    background: rgba(77,171,255,0.10);
    border: 1px solid rgba(77,171,255,0.3);
    color: var(--accent);
    transition: all 0.15s;
  }
  .result-card .actions a:hover {
    background: rgba(77,171,255,0.20);
    border-color: var(--border-hover);
  }

  .loader {
    color: var(--accent); padding: 20px; text-align: center;
    font-size: 14px;
  }
  .empty {
    color: var(--text-2); padding: 20px; text-align: center;
    font-size: 14px;
  }
  .error-box {
    background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    border-radius: 12px; padding: 16px; color: #ff5470;
    margin: 16px 0;
  }
</style>
</head>
<body>

""" + render_header("forecast") + """
<h1>🔍 Поиск точки</h1>
<div class="sub">Введите название населённого пункта или координаты, затем выберите, что показать</div>

<div class="search-box">
  <div class="search-row">
    <label>По названию:</label>
    <input type="text" id="q" class="q"
           placeholder="Москва, Домодедово, Лондон, Tokyo..."
           value="{{ preset_name or '' }}"
           onkeydown="if(event.key==='Enter') doSearch()">
    <button onclick="doSearch()">🔍 Найти</button>
  </div>

  <div class="search-row">
    <label>По координатам:</label>
    <input type="text" id="lat" class="coord" placeholder="55.41"
           value="{{ preset_lat or '' }}">
    <input type="text" id="lon" class="coord" placeholder="37.90"
           value="{{ preset_lon or '' }}">
    <button onclick="doSearchCoords()" class="secondary">Перейти →</button>
  </div>

  <div class="search-row">
    <label>Модель:</label>
    <select id="model">
      {% for key, m in models.items() %}
        <option value="{{ key }}">{{ m.name }}</option>
      {% endfor %}
    </select>
    <span class="hint">Какие данные показывать — таблица или текст</span>
  </div>
</div>

<div id="results"></div>

<script>
  function actionsHtml(name, lat, lon, model) {
    var encName = encodeURIComponent(name);
    return ''
      + '<div class="actions">'
      + '  <a href="/forecast/point?lat=' + lat + '&lon=' + lon + '&name=' + encName + '&model=' + model + '">📊 Таблица</a>'
      + '  <a href="/point-text?lat=' + lat + '&lon=' + lon + '&name=' + encName + '&model=' + model + '">📝 Текст</a>'
      + '  <a href="/point-aviation?lat=' + lat + '&lon=' + lon + '&name=' + encName + '&model=' + model + '">✈️ Авиация</a>'
      + '  <a href="/point-chart?lat=' + lat + '&lon=' + lon + '&name=' + encName + '">📈 График</a>'
      + '  <a href="/point-synoptic?lat=' + lat + '&lon=' + lon + '&name=' + encName + '&model=' + model + '">🌡 Синоптика</a>'
      + '</div>';
  }

  async function doSearch() {
    var q = document.getElementById('q').value.trim();
    if (!q) return;
    var model = document.getElementById('model').value;
    var results = document.getElementById('results');

    var coordMatch = q.match(/^(-?\\d+\\.?\\d*)[\\s,]+(-?\\d+\\.?\\d*)$/);
    if (coordMatch) {
      var lat = parseFloat(coordMatch[1]);
      var lon = parseFloat(coordMatch[2]);
      if (lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
        var name = lat + ', ' + lon;
        var encName = encodeURIComponent(name);
        window.location.href = '/forecast/point?lat=' + lat + '&lon=' + lon + '&name=' + encName + '&model=' + model;
        return;
      }
    }

    results.innerHTML = '<div class="loader">⏳ Поиск...</div>';

    try {
      var resp = await fetch('/api/geocode?q=' + encodeURIComponent(q));
      var data = await resp.json();

      if (data.error) {
        results.innerHTML = '<div class="error-box">Ошибка: ' + data.error + '</div>';
        return;
      }

      if (!data.results || data.results.length === 0) {
        results.innerHTML = '<div class="empty">Ничего не найдено. Попробуйте другое название или введите координаты.</div>';
        return;
      }

      var html = '<div class="results-grid">';
      data.results.forEach(function(p) {
        var label = [p.name, p.admin1, p.country].filter(Boolean).join(', ');
        var meta = '';
        if (p.latitude !== undefined && p.longitude !== undefined) {
          meta += p.latitude.toFixed(3) + ', ' + p.longitude.toFixed(3);
        }
        if (p.elevation !== undefined && p.elevation !== null) {
          meta += ' · ' + p.elevation + ' м';
        }
        if (p.population) {
          meta += ' · ' + p.population.toLocaleString('ru-RU') + ' чел.';
        }
        if (p.timezone) {
          meta += ' · ' + p.timezone;
        }

        html += '<div class="result-card">'
              + '<div class="place">📍 ' + p.name + '</div>'
              + '<div class="meta">' + meta + '</div>'
              + actionsHtml(label, p.latitude, p.longitude, model)
              + '</div>';
      });
      html += '</div>';
      results.innerHTML = html;
    } catch (err) {
      results.innerHTML = '<div class="error-box">Ошибка: ' + err.message + '</div>';
    }
  }

  function doSearchCoords() {
    var lat = parseFloat(document.getElementById('lat').value);
    var lon = parseFloat(document.getElementById('lon').value);
    var model = document.getElementById('model').value;
    if (isNaN(lat) || isNaN(lon)) {
      alert('Введите корректные координаты');
      return;
    }
    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      alert('Широта: -90…90, долгота: -180…180');
      return;
    }
    var name = lat + ', ' + lon;
    var encName = encodeURIComponent(name);
    window.location.href = '/forecast/point?lat=' + lat + '&lon=' + lon + '&name=' + encName + '&model=' + model;
  }
</script>

""" + COMMON_JS +  """
</body>
</html>
"""




POINT_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Прогноз — {{ point_name }}</title>
""" + BASE_STYLE + """
</head>
<body>
<a class="back" href="/search">← Поиск</a>
<h1>{{ point_name }}</h1>
<div class="sub">{{ lat }}, {{ lon }} · модель: {{ model_name }}</div>
<p style="color:var(--text-1);font-size:14px;line-height:1.8;">
Раздел в разработке.
</p>
""" + COMMON_JS +  """
</body>
</html>
"""
