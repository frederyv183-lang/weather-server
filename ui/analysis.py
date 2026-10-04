# -*- coding: utf-8 -*-
"""Страницы анализа и верификации: verify, analyze, matrices."""

from ui.styles import (
    BASE_STYLE,
    COMMON_JS,
    render_header,
    render_legend,
    render_biblio_ref,
)
VERIFY_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Проверка — {{ station_name }}</title>
""" + BASE_STYLE + """
<style>
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

  .info-badge {
    display: inline-block; padding: 6px 12px; border-radius: 8px;
    font-size: 12px; font-weight: 600; margin-left: auto;
  }
  .info-station { background: rgba(0,229,160,0.15); color: #00e5a0;
                   border: 1px solid rgba(0,229,160,0.3); }
  .info-era5    { background: rgba(255,181,71,0.15); color: #ffb547;
                   border: 1px solid rgba(255,181,71,0.3); }

  .stats-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 14px; margin: 16px 0;
  }
  .stat-card {
    padding: 18px 20px; border-radius: 16px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border); backdrop-filter: blur(14px);
    position: relative; overflow: hidden;
  }
  .stat-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0.6;
  }
  .stat-card h3 {
    margin: 0 0 12px 0; font-size: 15px; font-weight: 700;
    display: flex; justify-content: space-between; align-items: center;
  }
  .stat-card .model-tag {
    font-size: 10px; padding: 3px 8px; border-radius: 4px;
    background: rgba(77,171,255,0.15); color: var(--accent);
    font-weight: 600; letter-spacing: 0.3px;
  }
  .stat-row {
    display: flex; justify-content: space-between; padding: 6px 0;
    font-size: 13px; border-bottom: 1px solid rgba(120,160,255,0.06);
  }
  .stat-row:last-child { border-bottom: none; }
  .stat-row .lbl { color: var(--text-2); }
  .stat-row .val {
    font-family: 'JetBrains Mono', monospace; font-weight: 600;
    color: var(--text-0);
  }
  .stat-row .val.good { color: #00e5a0; }
  .stat-row .val.warn { color: #ffb547; }
  .stat-row .val.bad  { color: #ff5470; }

  .error-card {
    padding: 16px; border-radius: 12px;
    background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    color: #ff5470; font-size: 13px;
  }

  .detail-section {
    margin: 28px 0; padding: 20px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; backdrop-filter: blur(14px);
  }
  .detail-section h2 {
    margin: 0 0 16px 0; font-size: 18px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }

  .histogram {
    display: flex; align-items: flex-end; gap: 4px;
    height: 120px; padding: 8px 0; margin-top: 12px;
  }
  .histogram .bar {
    flex: 1; background: linear-gradient(180deg, var(--accent), rgba(77,171,255,0.4));
    border-radius: 4px 4px 0 0; min-height: 2px; position: relative;
  }
  .histogram .bar:hover::after {
    content: attr(data-label);
    position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%);
    background: var(--bg-0); padding: 4px 8px; border-radius: 6px;
    font-size: 11px; white-space: nowrap; border: 1px solid var(--border);
  }
  .histogram-labels {
    display: flex; justify-content: space-between;
    font-size: 11px; color: var(--text-2); margin-top: 4px;
  }

  .scatter-wrap {
    position: relative; width: 100%; max-width: 500px; margin: 0 auto;
    aspect-ratio: 1 / 1; background: rgba(15,21,36,0.5);
    border: 1px solid var(--border); border-radius: 12px;
  }
  .scatter-wrap svg { width: 100%; height: 100%; }
</style>
</head>
<body>

""" + render_header("analysis") + """
<h1>Проверка моделей</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · период: {{ days }} дней</div>

<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    <a href="/verify/{{ station_key }}?days={{ d }}{% if selected_model %}&model={{ selected_model }}{% endif %}"
       class="{% if d == days %}active{% endif %}">{{ d }} дней</a>
  {% endfor %}

  <label style="margin-left:12px;">Модель:</label>
  <a href="/verify/{{ station_key }}?days={{ days }}"
     class="{% if not selected_model %}active{% endif %}">Все</a>
  {% for key, m in MODELS.items() %}
    <a href="/verify/{{ station_key }}?days={{ days }}&model={{ key }}"
       class="{% if selected_model == key %}active{% endif %}">{{ m.name }}</a>
  {% endfor %}

  <span class="info-badge {% if station_info.available %}info-station{% else %}info-era5{% endif %}">
    {% if station_info.available %}
      📡 Станция: {{ station_info.name }} ({{ station_info.distance_km }} км)
    {% else %}
      🛰 Источник: ERA5
      {% if station_info.reason %}· {{ station_info.reason }}{% endif %}
    {% endif %}
  </span>
</div>

<div class="stats-grid">
  {% for st in models_stats %}
    <div class="stat-card">
      <h3>
        {{ st.model_name }}
        <span class="model-tag">{{ st.model_key | upper }}</span>
      </h3>

      {% if st.error %}
        <div class="error-card">⚠️ {{ st.error }}</div>
      {% else %}
        <div class="stat-row">
          <span class="lbl">Часов сравнения</span>
          <span class="val">{{ st.hours_total }}</span>
        </div>

        {% if st.temp %}
        <div class="stat-row">
          <span class="lbl">MAE, °C</span>
          <span class="val {% if st.temp.mae < 1.5 %}good{% elif st.temp.mae < 3 %}warn{% else %}bad{% endif %}">
            {{ '%.2f'|format(st.temp.mae) if st.temp.mae is not none else '—' }}
          </span>
        </div>
        <div class="stat-row">
          <span class="lbl">RMSE, °C</span>
          <span class="val {% if st.temp.rmse < 2 %}good{% elif st.temp.rmse < 4 %}warn{% else %}bad{% endif %}">
            {{ '%.2f'|format(st.temp.rmse) if st.temp.rmse is not none else '—' }}
          </span>
        </div>
        <div class="stat-row">
          <span class="lbl">Bias, °C</span>
          <span class="val {% if st.temp.bias is not none and st.temp.bias|absval < 0.5 %}good{% elif st.temp.bias is not none and st.temp.bias|absval < 1.5 %}warn{% else %}bad{% endif %}">
            {{ '%+.2f'|format(st.temp.bias) if st.temp.bias is not none else '—' }}
          </span>
        </div>
        <div class="stat-row">
          <span class="lbl">Корреляция</span>
          <span class="val">
            {{ '%.3f'|format(st.temp.corr) if st.temp.corr is not none else '—' }}
          </span>
        </div>
        <div class="stat-row">
          <span class="lbl">R²</span>
          <span class="val">{{ '%.3f'|format(st.temp.r2) if st.temp.r2 is not none else '—' }}</span>
        </div>
        <div class="stat-row">
          <span class="lbl">P90 |ошибки|</span>
          <span class="val">{{ '%.2f'|format(st.temp.p90) if st.temp.p90 is not none else '—' }}</span>
        </div>
        {% endif %}

        {% if st.precip %}
        <div class="stat-row" style="margin-top:10px;border-top:1px solid var(--border);padding-top:10px;">
          <span class="lbl">Осадки: F1</span>
          <span class="val {% if st.precip.f1 is not none and st.precip.f1 > 0.5 %}good{% elif st.precip.f1 is not none and st.precip.f1 > 0.3 %}warn{% else %}bad{% endif %}">
            {{ '%.3f'|format(st.precip.f1) if st.precip.f1 is not none else '—' }}
          </span>
        </div>
        <div class="stat-row">
          <span class="lbl">Hit rate / Precision</span>
          <span class="val" style="font-size:11px;">
            {{ '%.2f'|format(st.precip.hit_rate) if st.precip.hit_rate is not none else '—' }}
            /
            {{ '%.2f'|format(st.precip.precision) if st.precip.precision is not none else '—' }}
          </span>
        </div>
        {% endif %}
      {% endif %}
    </div>
  {% endfor %}
</div>

{% if detail and not detail.error %}
<div class="detail-section">
  <h2>🔬 Детали: {{ detail.model_name }}</h2>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">
    <div>
      <div style="color:var(--text-1);font-size:13px;margin-bottom:8px;">
        Диаграмма рассеяния: прогноз vs факт (T, °C)
      </div>
      <div class="scatter-wrap">
        {% if detail.scatter %}
          {% set xs = detail.scatter | map(attribute='x') | list %}
          {% set ys = detail.scatter | map(attribute='y') | list %}
          {% set all_vals = xs + ys %}
          {% set vmin = all_vals | min %}
          {% set vmax = all_vals | max %}
          {% set vspan = (vmax - vmin) or 1 %}
          <svg viewBox="0 0 100 100" preserveAspectRatio="none">
            <line x1="5" y1="95" x2="95" y2="95" stroke="var(--text-2)" stroke-width="0.3"/>
            <line x1="5" y1="5"  x2="5"  y2="95" stroke="var(--text-2)" stroke-width="0.3"/>
            <line x1="5" y1="95" x2="95" y2="5"
                  stroke="rgba(255,181,71,0.5)" stroke-width="0.4"
                  stroke-dasharray="1 1"/>
            {% for pt in detail.scatter %}
              {% set px = 5 + 90 * (pt.x - vmin) / vspan %}
              {% set py = 95 - 90 * (pt.y - vmin) / vspan %}
              <circle cx="{{ '%.2f'|format(px) }}" cy="{{ '%.2f'|format(py) }}"
                      r="0.5" fill="var(--accent)" opacity="0.6"/>
            {% endfor %}
          </svg>
        {% else %}
          <div style="color:var(--text-2);padding:20px;text-align:center;">Нет данных</div>
        {% endif %}
      </div>
      <div class="histogram-labels">
        <span>факт: {{ '%.1f'|format(vmin) if detail.scatter else '—' }}</span>
        <span>факт: {{ '%.1f'|format(vmax) if detail.scatter else '—' }}</span>
      </div>
    </div>

    <div>
      <div style="color:var(--text-1);font-size:13px;margin-bottom:8px;">
        Гистограмма ошибок (прогноз − факт, °C)
      </div>
      {% if detail.histogram %}
        {% set max_count = detail.histogram | map(attribute='count') | max %}
        <div class="histogram">
          {% for b in detail.histogram %}
            <div class="bar"
                 style="height: {{ (b.count / max_count * 100) if max_count else 2 }}%;"
                 data-label="{{ b.x }} °C: {{ b.count }} ч">
            </div>
          {% endfor %}
        </div>
        <div class="histogram-labels">
          <span>{{ detail.histogram[0].x }} °C</span>
          <span>0</span>
          <span>{{ detail.histogram[-1].x }} °C</span>
        </div>
      {% else %}
        <div style="color:var(--text-2);padding:20px;">Нет данных</div>
      {% endif %}

      <div style="margin-top:20px;font-size:13px;">
        <div class="stat-row">
          <span class="lbl">MAPE</span>
          <span class="val">{{ '%.2f'|format(detail.temp.mape) if detail.temp.mape is not none else '—' }} %</span>
        </div>
        <div class="stat-row">
          <span class="lbl">P50 |ошибки|</span>
          <span class="val">{{ '%.2f'|format(detail.temp.p50) if detail.temp.p50 is not none else '—' }} °C</span>
        </div>
        <div class="stat-row">
          <span class="lbl">P95 |ошибки|</span>
          <span class="val">{{ '%.2f'|format(detail.temp.p95) if detail.temp.p95 is not none else '—' }} °C</span>
        </div>
      </div>
    </div>
  </div>
</div>
{% endif %}

<div style="margin: 24px 0;">
  <a class="card fade-in" href="/verify/{{ station_key }}/history"
     style="background:rgba(0,229,160,0.08);">
    <span class="icon">📉</span><b>История ошибок по дням</b>
    <div class="desc">Как менялась MAE и Bias за последние {{ history_days }} дней</div>
  </a>
</div>

""" + COMMON_JS +  render_legend("analysis") + """
</body>
</html>
"""




VERIFY_HISTORY_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>История ошибок — {{ station_name }}</title>
""" + BASE_STYLE + """
<style>
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

  .legend {
    display: flex; gap: 16px; flex-wrap: wrap;
    padding: 12px 18px; margin-bottom: 16px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 14px; font-size: 13px;
    backdrop-filter: blur(14px);
  }
  .legend-item { display: flex; align-items: center; gap: 8px; }
  .legend-dot { display: inline-block; width: 14px; height: 14px; border-radius: 3px; }

  .chart-block {
    margin: 24px 0; padding: 20px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; backdrop-filter: blur(14px);
  }
  .chart-block h2 {
    margin: 0 0 16px 0; font-size: 18px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .chart-block svg { display: block; }

  .table-block {
    margin: 24px 0; padding: 20px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; backdrop-filter: blur(14px);
  }
  .table-block h2 {
    margin: 0 0 16px 0; font-size: 18px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }

  .history-table {
    width: 100%; border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace; font-size: 12px;
  }
  .history-table th {
    text-align: left; padding: 8px 10px; color: var(--text-2);
    font-weight: 600; font-size: 11px; text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  .history-table td {
    padding: 8px 10px; border-bottom: 1px solid rgba(120,160,255,0.06);
  }
  .history-table tr:hover td { background: rgba(77,171,255,0.05); }
  .history-table td.num { font-weight: 600; }
  .history-table td.num.good { color: #00e5a0; }
  .history-table td.num.warn { color: #ffb547; }
  .history-table td.num.bad  { color: #ff5470; }
  .history-table td.model-cell {
    display: flex; align-items: center; gap: 8px;
    font-family: 'Inter', sans-serif; font-weight: 600;
  }
  .history-table td .dot {
    display: inline-block; width: 10px; height: 10px; border-radius: 2px;
  }

  .error-box {
    background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    border-radius: 12px; padding: 16px; color: #ff5470;
    margin: 16px 0;
  }
  .empty-note { color: var(--text-2); padding: 20px; font-size: 14px; }
</style>
</head>
<body>

""" + render_header("analysis") + """
<h1>📉 История ошибок по дням</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · последние {{ days }} дней</div>

{% if error %}
  <div class="error-box">⚠️ {{ error }}</div>
{% endif %}

<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    <a href="/verify/{{ station_key }}/history?days={{ d }}"
       class="{% if d == days %}active{% endif %}">{{ d }} дней</a>
  {% endfor %}
</div>

{% if dates %}
<div class="legend">
  {% for mk, data in per_model.items() %}
    {% if not data.error %}
      <div class="legend-item">
        <span class="legend-dot" style="background:{{ data.color }};"></span>
        <span>{{ data.model_name }}</span>
      </div>
    {% endif %}
  {% endfor %}
</div>

<div class="chart-block">
  <h2>📊 MAE по дням (°C)</h2>
  {{ svg_mae | safe }}
</div>

<div class="chart-block">
  <h2>📊 Bias по дням (°C)</h2>
  {{ svg_bias | safe }}
</div>

<div class="chart-block">
  <h2>📊 RMSE по дням (°C)</h2>
  {{ svg_rmse | safe }}
</div>

<div class="table-block">
  <h2>📋 Детализация по дням</h2>
  <div style="overflow-x:auto;">
  <table class="history-table">
    <thead>
      <tr>
        <th>Дата</th>
        <th>Модель</th>
        <th>MAE, °C</th>
        <th>Bias, °C</th>
        <th>RMSE, °C</th>
        <th>Корр.</th>
        <th>Часов</th>
      </tr>
    </thead>
    <tbody>
      {% for r in table_rows %}
      <tr>
        <td>{{ r.date | date_ru }}</td>
        <td class="model-cell">
          <span class="dot" style="background:{{ r.model_color }};"></span>
          {{ r.model_name }}
        </td>
        <td class="num {% if r.mae is not none and r.mae < 1.5 %}good{% elif r.mae is not none and r.mae < 3 %}warn{% else %}bad{% endif %}">
          {{ '%.2f'|format(r.mae) if r.mae is not none else '—' }}
        </td>
        <td class="num {% if r.bias is not none and r.bias|absval < 0.5 %}good{% elif r.bias is not none and r.bias|absval < 1.5 %}warn{% else %}bad{% endif %}">
          {{ '%+.2f'|format(r.bias) if r.bias is not none else '—' }}
        </td>
        <td class="num">
          {{ '%.2f'|format(r.rmse) if r.rmse is not none else '—' }}
        </td>
        <td class="num">
          {{ '%.3f'|format(r.corr) if r.corr is not none else '—' }}
        </td>
        <td class="num">{{ r.hours }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  </div>
</div>

{% else %}
  <div class="empty-note">Нет данных за выбранный период.</div>
{% endif %}

""" + COMMON_JS +  render_legend("analysis") + """
</body>
</html>
"""




ANALYZE_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Анализ — {{ station_name }} — {{ MODELS[selected_model].name }}</title>
""" + BASE_STYLE + """
<style>
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
    color: var(--text-0); text-decoration: none; cursor: pointer;
    transition: all 0.2s;
  }
  .controls a:hover { border-color: var(--border-hover); }
  .controls a.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25), rgba(124,92,255,0.25));
    border-color: var(--accent);
  }
  .info-badge {
    display: inline-block; padding: 6px 12px; border-radius: 8px;
    font-size: 12px; font-weight: 600; margin-left: auto;
  }
  .info-station { background: rgba(0,229,160,0.15); color: #00e5a0;
                   border: 1px solid rgba(0,229,160,0.3); }
  .info-era5    { background: rgba(255,181,71,0.15); color: #ffb547;
                   border: 1px solid rgba(255,181,71,0.3); }

  .kpi-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px; margin: 16px 0 24px 0;
  }
  .kpi {
    padding: 14px 16px; border-radius: 14px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border); text-align: center;
  }
  .kpi .lbl { color: var(--text-2); font-size: 11px;
              text-transform: uppercase; letter-spacing: 0.5px; }
  .kpi .val {
    font-family: 'JetBrains Mono', monospace; font-size: 22px;
    font-weight: 700; margin-top: 6px;
  }
  .kpi .val.good { color: #00e5a0; }
  .kpi .val.warn { color: #ffb547; }
  .kpi .val.bad  { color: #ff5470; }

  .section {
    margin: 24px 0; padding: 20px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; backdrop-filter: blur(14px);
  }
  .section h2 {
    margin: 0 0 16px 0; font-size: 18px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }

  .daily-table {
    width: 100%; border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace; font-size: 12px;
  }
  .daily-table th {
    text-align: left; padding: 8px 10px; color: var(--text-2);
    font-weight: 600; font-size: 11px; text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  .daily-table td {
    padding: 8px 10px; border-bottom: 1px solid rgba(120,160,255,0.06);
  }
  .daily-table tr:hover td { background: rgba(77,171,255,0.05); }
  .daily-table td.num {
    font-family: 'JetBrains Mono', monospace; font-weight: 600;
  }
  .daily-table td.num.good { color: #00e5a0; }
  .daily-table td.num.warn { color: #ffb547; }
  .daily-table td.num.bad  { color: #ff5470; }

  .bar-chart {
    display: flex; align-items: flex-end; gap: 6px;
    height: 160px; padding: 12px 0; margin-top: 12px;
    border-bottom: 1px solid var(--border);
  }
  .bar-chart .bar {
    flex: 1; min-height: 2px; border-radius: 4px 4px 0 0;
    position: relative; transition: opacity 0.2s;
  }
  .bar-chart .bar:hover { opacity: 0.75; }
  .bar-chart .bar:hover::after {
    content: attr(data-label);
    position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%);
    background: var(--bg-0); padding: 6px 10px; border-radius: 6px;
    font-size: 11px; white-space: nowrap; border: 1px solid var(--border);
    z-index: 10;
  }
  .bar-chart .bar.mae  { background: linear-gradient(180deg, #4dabff, rgba(77,171,255,0.3)); }
  .bar-chart .bar.bias { background: linear-gradient(180deg, #ffb547, rgba(255,181,71,0.3)); }

  .bar-labels {
    display: flex; gap: 6px; margin-top: 6px;
    font-size: 10px; color: var(--text-2);
  }
  .bar-labels span { flex: 1; text-align: center; }

  .histogram {
    display: flex; align-items: flex-end; gap: 4px;
    height: 120px; padding: 8px 0; margin-top: 12px;
  }
  .histogram .bar {
    flex: 1; background: linear-gradient(180deg, var(--accent), rgba(77,171,255,0.4));
    border-radius: 4px 4px 0 0; min-height: 2px; position: relative;
  }
  .histogram .bar:hover::after {
    content: attr(data-label);
    position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%);
    background: var(--bg-0); padding: 4px 8px; border-radius: 6px;
    font-size: 11px; white-space: nowrap; border: 1px solid var(--border);
  }
  .histogram-labels {
    display: flex; justify-content: space-between;
    font-size: 11px; color: var(--text-2); margin-top: 4px;
  }

  .scatter-wrap {
    position: relative; width: 100%; max-width: 460px; margin: 0 auto;
    aspect-ratio: 1 / 1; background: rgba(15,21,36,0.5);
    border: 1px solid var(--border); border-radius: 12px;
  }
  .scatter-wrap svg { width: 100%; height: 100%; }

  .stat-line {
    display: flex; justify-content: space-between; padding: 6px 0;
    font-size: 13px; border-bottom: 1px solid rgba(120,160,255,0.06);
  }
  .stat-line:last-child { border-bottom: none; }
  .stat-line .lbl { color: var(--text-2); }
  .stat-line .val {
    font-family: 'JetBrains Mono', monospace; font-weight: 600;
  }

  .compare-table {
    width: 100%; border-collapse: collapse; font-size: 13px;
  }
  .compare-table th {
    text-align: left; padding: 10px 12px; color: var(--text-2);
    font-weight: 600; font-size: 11px; text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  .compare-table td {
    padding: 10px 12px; border-bottom: 1px solid rgba(120,160,255,0.06);
  }
  .compare-table tr:hover td { background: rgba(77,171,255,0.05); }
  .compare-table td.num {
    font-family: 'JetBrains Mono', monospace; font-weight: 600;
  }
  .compare-table td.num.good { color: #00e5a0; }
  .compare-table td.num.warn { color: #ffb547; }
  .compare-table td.num.bad  { color: #ff5470; }
  .compare-table tr.best td { background: rgba(0,229,160,0.08); }

  .error-box {
    background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    border-radius: 12px; padding: 16px; color: #ff5470;
    margin: 16px 0;
  }

  @media (max-width: 700px) {
    .section > div[style*="grid-template-columns"] {
      grid-template-columns: 1fr !important;
    }
  }
</style>
</head>
<body>

""" + render_header("analysis") + """
<h1>Расширенный анализ</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · {{ days }} дней</div>

<div class="controls">
  <label>Модель:</label>
  {% for key, m in MODELS.items() %}
    <a href="/analyze/{{ station_key }}?days={{ days }}&model={{ key }}"
       class="{% if selected_model == key %}active{% endif %}">{{ m.name }}</a>
  {% endfor %}

  <label style="margin-left:12px;">Период:</label>
  {% for d in days_options %}
    <a href="/analyze/{{ station_key }}?days={{ d }}&model={{ selected_model }}"
       class="{% if d == days %}active{% endif %}">{{ d }} дней</a>
  {% endfor %}

  <span class="info-badge {% if station_info.available %}info-station{% else %}info-era5{% endif %}">
    {% if station_info.available %}
      📡 {{ station_info.name }} ({{ station_info.distance_km }} км)
    {% else %}
      🛰 ERA5{% if station_info.reason %} · {{ station_info.reason }}{% endif %}
    {% endif %}
  </span>
</div>

{% if detail.error %}
  <div class="error-box">⚠️ {{ detail.error }}</div>
{% else %}

<div class="kpi-grid">
  <div class="kpi">
    <div class="lbl">MAE, °C</div>
    <div class="val {% if detail.temp.mae < 1.5 %}good{% elif detail.temp.mae < 3 %}warn{% else %}bad{% endif %}">
      {{ '%.2f'|format(detail.temp.mae) if detail.temp.mae is not none else '—' }}
    </div>
  </div>
  <div class="kpi">
    <div class="lbl">RMSE, °C</div>
    <div class="val {% if detail.temp.rmse < 2 %}good{% elif detail.temp.rmse < 4 %}warn{% else %}bad{% endif %}">
      {{ '%.2f'|format(detail.temp.rmse) if detail.temp.rmse is not none else '—' }}
    </div>
  </div>
  <div class="kpi">
    <div class="lbl">Bias, °C</div>
    <div class="val {% if detail.temp.bias is not none and detail.temp.bias|absval < 0.5 %}good{% elif detail.temp.bias is not none and detail.temp.bias|absval < 1.5 %}warn{% else %}bad{% endif %}">
      {{ '%+.2f'|format(detail.temp.bias) if detail.temp.bias is not none else '—' }}
    </div>
  </div>
  <div class="kpi">
    <div class="lbl">Корреляция</div>
    <div class="val">{{ '%.3f'|format(detail.temp.corr) if detail.temp.corr is not none else '—' }}</div>
  </div>
  <div class="kpi">
    <div class="lbl">R²</div>
    <div class="val">{{ '%.3f'|format(detail.temp.r2) if detail.temp.r2 is not none else '—' }}</div>
  </div>
  <div class="kpi">
    <div class="lbl">MAPE, %</div>
    <div class="val">{{ '%.2f'|format(detail.temp.mape) if detail.temp.mape is not none else '—' }}</div>
  </div>
  <div class="kpi">
    <div class="lbl">P90 |ошибки|</div>
    <div class="val">{{ '%.2f'|format(detail.temp.p90) if detail.temp.p90 is not none else '—' }}</div>
  </div>
  <div class="kpi">
    <div class="lbl">Часов</div>
    <div class="val">{{ detail.hours_total }}</div>
  </div>
</div>

<div class="section">
  <h2>📅 Динамика по дням: MAE и Bias</h2>
  {% if by_day.days %}
    {% set valid_days = by_day.days | selectattr("mae", "ne", none) | list %}
    {% if valid_days %}
      {% set max_mae = valid_days | map(attribute="mae") | max %}
      {% set max_abs_bias = valid_days | map(attribute="bias") | map("absval") | max %}
      {% set scale = [max_mae, max_abs_bias] | max %}

      <div style="font-size:12px;color:var(--text-2);margin-bottom:6px;">MAE по дням (°C):</div>
      <div class="bar-chart">
        {% for d in valid_days %}
          <div class="bar mae"
               style="height: {{ (d.mae / scale * 100) if scale else 2 }}%;"
               data-label="{{ d.date }}: MAE {{ d.mae }} °C, {{ d.hours }} ч">
          </div>
        {% endfor %}
      </div>
      <div class="bar-labels">
        {% for d in valid_days %}
          <span>{{ d.date[8:10] }}.{{ d.date[5:7] }}</span>
        {% endfor %}
      </div>

      <div style="font-size:12px;color:var(--text-2);margin-top:24px;margin-bottom:6px;">
        Bias по дням (|смещение|, °C):
      </div>
      <div class="bar-chart" style="height:100px;">
        {% for d in valid_days %}
          {% set abs_b = d.bias | absval %}
          <div class="bar bias"
               style="height: {{ (abs_b / scale * 100) if scale else 2 }}%;"
               data-label="{{ d.date }}: Bias {{ '%+.2f'|format(d.bias) }} °C">
          </div>
        {% endfor %}
      </div>
    {% else %}
      <div style="color:var(--text-2);padding:20px;">Нет данных по дням.</div>
    {% endif %}
  {% else %}
    <div style="color:var(--text-2);padding:20px;">Нет данных по дням.</div>
  {% endif %}
</div>

<div class="section">
  <h2>📋 Детализация по дням</h2>
  {% if by_day.days %}
  <div style="overflow-x:auto;">
  <table class="daily-table">
    <thead>
      <tr>
        <th>Дата</th>
        <th>Часов</th>
        <th>MAE, °C</th>
        <th>Bias, °C</th>
        <th>RMSE, °C</th>
        <th>Корр.</th>
        <th>Оценка</th>
      </tr>
    </thead>
    <tbody>
      {% for d in by_day.days %}
      <tr>
        <td>{{ d.date | date_ru }}</td>
        <td class="num">{{ d.hours }}</td>
        {% if d.mae is not none %}
          <td class="num {% if d.mae < 1.5 %}good{% elif d.mae < 3 %}warn{% else %}bad{% endif %}">
            {{ '%.2f'|format(d.mae) }}
          </td>
          <td class="num {% if d.bias|absval < 0.5 %}good{% elif d.bias|absval < 1.5 %}warn{% else %}bad{% endif %}">
            {{ '%+.2f'|format(d.bias) }}
          </td>
          <td class="num {% if d.rmse < 2 %}good{% elif d.rmse < 4 %}warn{% else %}bad{% endif %}">
            {{ '%.2f'|format(d.rmse) }}
          </td>
          <td class="num">{{ '%.3f'|format(d.corr) if d.corr is not none else '—' }}</td>
          <td>
            {% if d.mae < 1.5 %}✅ Отлично
            {% elif d.mae < 3 %}⚠️ Средне
            {% else %}❌ Плохо{% endif %}
          </td>
        {% else %}
          <td colspan="6" style="color:var(--text-2);">{{ d.error or '—' }}</td>
        {% endif %}
      </tr>
      {% endfor %}
    </tbody>
  </table>
  </div>
  {% else %}
    <div style="color:var(--text-2);padding:20px;">Нет данных по дням.</div>
  {% endif %}
</div>

<div class="section">
  <h2>🔬 Детальный разбор: {{ MODELS[selected_model].name }}</h2>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">
    <div>
      <div style="color:var(--text-1);font-size:13px;margin-bottom:8px;">
        Диаграмма рассеяния: прогноз vs факт (T, °C)
      </div>
      <div class="scatter-wrap">
        {% if detail.scatter %}
          {% set xs = detail.scatter | map(attribute='x') | list %}
          {% set ys = detail.scatter | map(attribute='y') | list %}
          {% set all_vals = xs + ys %}
          {% set vmin = all_vals | min %}
          {% set vmax = all_vals | max %}
          {% set vspan = (vmax - vmin) or 1 %}
          <svg viewBox="0 0 100 100" preserveAspectRatio="none">
            <line x1="5" y1="95" x2="95" y2="95" stroke="var(--text-2)" stroke-width="0.3"/>
            <line x1="5" y1="5"  x2="5"  y2="95" stroke="var(--text-2)" stroke-width="0.3"/>
            <line x1="5" y1="95" x2="95" y2="5"
                  stroke="rgba(255,181,71,0.5)" stroke-width="0.4"
                  stroke-dasharray="1 1"/>
            {% for pt in detail.scatter %}
              {% set px = 5 + 90 * (pt.x - vmin) / vspan %}
              {% set py = 95 - 90 * (pt.y - vmin) / vspan %}
              <circle cx="{{ '%.2f'|format(px) }}" cy="{{ '%.2f'|format(py) }}"
                      r="0.5" fill="var(--accent)" opacity="0.6"/>
            {% endfor %}
          </svg>
        {% else %}
          <div style="color:var(--text-2);padding:20px;text-align:center;">Нет данных</div>
        {% endif %}
      </div>
      <div class="histogram-labels">
        <span>факт: {{ '%.1f'|format(vmin) if detail.scatter else '—' }}</span>
        <span>факт: {{ '%.1f'|format(vmax) if detail.scatter else '—' }}</span>
      </div>
    </div>

    <div>
      <div style="color:var(--text-1);font-size:13px;margin-bottom:8px;">
        Гистограмма ошибок (прогноз − факт, °C)
      </div>
      {% if detail.histogram %}
        {% set max_count = detail.histogram | map(attribute='count') | max %}
        <div class="histogram">
          {% for b in detail.histogram %}
            <div class="bar"
                 style="height: {{ (b.count / max_count * 100) if max_count else 2 }}%;"
                 data-label="{{ b.x }} °C: {{ b.count }} ч">
            </div>
          {% endfor %}
        </div>
        <div class="histogram-labels">
          <span>{{ detail.histogram[0].x }} °C</span>
          <span>0</span>
          <span>{{ detail.histogram[-1].x }} °C</span>
        </div>
      {% else %}
        <div style="color:var(--text-2);padding:20px;">Нет данных</div>
      {% endif %}

      <div style="margin-top:20px;font-size:13px;">
        <div class="stat-line">
          <span class="lbl">MAPE</span>
          <span class="val">{{ '%.2f'|format(detail.temp.mape) if detail.temp.mape is not none else '—' }} %</span>
        </div>
        <div class="stat-line">
          <span class="lbl">P50 |ошибки|</span>
          <span class="val">{{ '%.2f'|format(detail.temp.p50) if detail.temp.p50 is not none else '—' }} °C</span>
        </div>
        <div class="stat-line">
          <span class="lbl">P95 |ошибки|</span>
          <span class="val">{{ '%.2f'|format(detail.temp.p95) if detail.temp.p95 is not none else '—' }} °C</span>
        </div>
      </div>
    </div>
  </div>
</div>

{% endif %}

<div class="section">
  <h2>📊 Сравнение моделей за {{ days }} дней</h2>
  <div style="overflow-x:auto;">
  <table class="compare-table">
    <thead>
      <tr>
        <th>Модель</th>
        <th>MAE, °C</th>
        <th>RMSE, °C</th>
        <th>Bias, °C</th>
        <th>Корр.</th>
        <th>R²</th>
        <th>F1 осадки</th>
        <th>Часов</th>
      </tr>
    </thead>
    <tbody>
      {% set valid_stats = compare_stats | selectattr("temp", "defined") | list %}
      {% set best_mae = valid_stats | map(attribute="temp.mae") | select("ne", none) | list | min if valid_stats else None %}
      {% for st in compare_stats %}
      <tr {% if st.temp and best_mae is not none and st.temp.mae == best_mae %}class="best"{% endif %}>
        <td>
          {{ st.model_name }}
          {% if st.temp and best_mae is not none and st.temp.mae == best_mae %}🏆{% endif %}
        </td>
        {% if st.error %}
          <td colspan="7" style="color:#ff5470;">⚠️ {{ st.error }}</td>
        {% else %}
          <td class="num {% if st.temp.mae < 1.5 %}good{% elif st.temp.mae < 3 %}warn{% else %}bad{% endif %}">
            {{ '%.2f'|format(st.temp.mae) if st.temp.mae is not none else '—' }}
          </td>
          <td class="num">{{ '%.2f'|format(st.temp.rmse) if st.temp.rmse is not none else '—' }}</td>
          <td class="num">{{ '%+.2f'|format(st.temp.bias) if st.temp.bias is not none else '—' }}</td>
          <td class="num">{{ '%.3f'|format(st.temp.corr) if st.temp.corr is not none else '—' }}</td>
          <td class="num">{{ '%.3f'|format(st.temp.r2) if st.temp.r2 is not none else '—' }}</td>
          <td class="num {% if st.precip and st.precip.f1 is not none and st.precip.f1 > 0.5 %}good{% elif st.precip and st.precip.f1 is not none and st.precip.f1 > 0.3 %}warn{% else %}bad{% endif %}">
            {{ '%.3f'|format(st.precip.f1) if st.precip and st.precip.f1 is not none else '—' }}
          </td>
          <td class="num">{{ st.hours_total }}</td>
        {% endif %}
      </tr>
      {% endfor %}
    </tbody>
  </table>
  </div>
</div>

""" + COMMON_JS +  render_legend("analysis") + """
</body>
</html>
"""




COMPARE_MATRICES_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Сравнение матриц — {{ station_name }}</title>
""" + BASE_STYLE + """
<style>
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

  .phenom-block {
    margin: 24px 0; padding: 20px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; backdrop-filter: blur(14px);
  }
  .phenom-block h2 {
    margin: 0 0 16px 0; font-size: 18px;
    display: flex; justify-content: space-between; align-items: center;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .phenom-block h2 .winner {
    font-size: 12px; padding: 4px 10px; border-radius: 6px;
    background: rgba(0,229,160,0.15); color: #00e5a0;
    border: 1px solid rgba(0,229,160,0.3);
    -webkit-text-fill-color: #00e5a0;
  }

  .criteria-table {
    width: 100%; border-collapse: collapse; font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
  }
  .criteria-table th {
    text-align: left; padding: 8px 10px; color: var(--text-2);
    font-weight: 600; font-size: 11px; text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  .criteria-table td {
    padding: 8px 10px; border-bottom: 1px solid rgba(120,160,255,0.06);
  }
  .criteria-table tr:hover td { background: rgba(77,171,255,0.05); }
  .criteria-table td.num { font-weight: 600; }
  .criteria-table td.num.good { color: #00e5a0; }
  .criteria-table td.num.warn { color: #ffb547; }
  .criteria-table td.num.bad  { color: #ff5470; }
  .criteria-table tr.best td {
    background: rgba(0,229,160,0.08);
    font-weight: 700;
  }
  .criteria-table .model-tag {
    display: inline-flex; align-items: center; gap: 8px;
    font-family: 'Inter', sans-serif; font-weight: 600;
  }
  .criteria-table .dot {
    display: inline-block; width: 10px; height: 10px; border-radius: 2px;
  }

  .error-box {
    background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    border-radius: 12px; padding: 16px; color: #ff5470;
    margin: 16px 0;
  }
  .empty-note { color: var(--text-2); padding: 20px; font-size: 14px; }

  .overview-table {
    width: 100%; border-collapse: collapse; font-size: 13px;
    font-family: 'Inter', sans-serif;
    margin-top: 12px;
  }
  .overview-table th {
    text-align: left; padding: 10px 12px; color: var(--text-2);
    font-weight: 600; font-size: 11px; text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  .overview-table td {
    padding: 10px 12px; border-bottom: 1px solid rgba(120,160,255,0.06);
  }
  .overview-table tr:hover td { background: rgba(77,171,255,0.05); }

  .methodology {
    margin: 24px 0; padding: 20px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; font-size: 13px; color: var(--text-1);
    line-height: 1.7;
  }
  .methodology h2 {
    margin: 0 0 12px 0; font-size: 16px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .methodology code {
    background: rgba(120,160,255,0.08); padding: 2px 6px;
    border-radius: 4px; font-family: 'JetBrains Mono', monospace;
    font-size: 12px; color: var(--accent);
  }
</style>
</head>
<body>

""" + render_header("analysis") + """
<h1>🔀 Сравнение моделей по матрицам Хандожко</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · {{ days }} дней</div>

<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    <a href="/compare-matrices/{{ station_key }}?days={{ d }}"
       class="{% if d == days %}active{% endif %}">{{ d }} дней</a>
  {% endfor %}
</div>

{% if results_per_phenomenon %}
<div class="phenom-block">
  <h2>🏆 Лучшая модель по каждому явлению</h2>
  <table class="overview-table">
    <thead>
      <tr>
        <th>Явление</th>
        <th>Лучшая модель</th>
        <th>p (оправдываемость)</th>
      </tr>
    </thead>
    <tbody>
      {% for ph_key, ph in phenomena.items() %}
        {% set best_key = best_per_phenomenon[ph_key] %}
        {% set results = results_per_phenomenon[ph_key] %}
        <tr>
          <td>{{ ph.name }}</td>
          <td>
            {% if best_key %}
              🏆 <b>{{ results | selectattr("model_key", "equalto", best_key) | map(attribute="model_name") | first }}</b>
            {% else %}
              <span style="color:var(--text-2);">—</span>
            {% endif %}
          </td>
          <td>
            {% if best_key %}
              {% for r in results %}
                {% if r.model_key == best_key and r.criteria %}
                  {{ '%.3f'|format(r.criteria.p) if r.criteria.p is not none else '—' }}
                {% endif %}
              {% endfor %}
            {% else %}
              —
            {% endif %}
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

{% for ph_key, ph in phenomena.items() %}
  {% set results = results_per_phenomenon[ph_key] %}
  {% set best_key = best_per_phenomenon[ph_key] %}

  <div class="phenom-block">
    <h2>
      📋 {{ ph.name }}
      {% if best_key %}
        <span class="winner">🏆 {{ results | selectattr("model_key", "equalto", best_key) | map(attribute="model_name") | first }}</span>
      {% endif %}
    </h2>

    {% if results and results|length > 0 %}
    <div style="overflow-x:auto;">
    <table class="criteria-table">
      <thead>
        <tr>
          <th>Модель</th>
          <th>Hits</th>
          <th>Misses</th>
          <th>False</th>
          <th>p</th>
          <th>H</th>
          <th>τ</th>
          <th>v</th>
          <th>Q</th>
          <th>S</th>
          <th>F1</th>
          <th>Часов</th>
        </tr>
      </thead>
      <tbody>
        {% for r in results %}
        <tr {% if r.model_key == best_key %}class="best"{% endif %}>
          <td class="model-tag">
            <span class="dot" style="background:{{ r.color or '#888' }};"></span>
            {{ r.model_name }}
            {% if r.model_key == best_key %}🏆{% endif %}
          </td>
          {% if r.error %}
            <td colspan="11" style="color:#ff5470;">⚠️ {{ r.error }}</td>
          {% else %}
            {% set ct = r.contingency %}
            {% set cr = r.criteria %}
            <td class="num">{{ ct.hits }}</td>
            <td class="num">{{ ct.misses }}</td>
            <td class="num">{{ ct.false_alarms }}</td>
            <td class="num {% if cr and cr.p and cr.p > 0.9 %}good{% elif cr and cr.p and cr.p > 0.7 %}warn{% else %}bad{% endif %}">
              {{ '%.3f'|format(cr.p) if cr and cr.p is not none else '—' }}
            </td>
            <td class="num {% if cr and cr.H and cr.H > 0.6 %}good{% elif cr and cr.H and cr.H > 0.4 %}warn{% else %}bad{% endif %}">
              {{ '%.3f'|format(cr.H) if cr and cr.H is not none else '—' }}
            </td>
            <td class="num {% if cr and cr.tau and cr.tau > 0.6 %}good{% elif cr and cr.tau and cr.tau > 0.4 %}warn{% else %}bad{% endif %}">
              {{ '%.3f'|format(cr.tau) if cr and cr.tau is not none else '—' }}
            </td>
            <td class="num {% if cr and cr.v and cr.v > 0.3 %}good{% elif cr and cr.v and cr.v > 0 %}warn{% else %}bad{% endif %}">
              {{ '%.3f'|format(cr.v) if cr and cr.v is not none else '—' }}
            </td>
            <td class="num">{{ '%.3f'|format(cr.Q) if cr and cr.Q is not none else '—' }}</td>
            <td class="num">{{ '%.3f'|format(cr.S) if cr and cr.S is not none else '—' }}</td>
            <td class="num {% if cr and cr.f1 and cr.f1 > 0.5 %}good{% elif cr and cr.f1 and cr.f1 > 0.3 %}warn{% else %}bad{% endif %}">
              {{ '%.3f'|format(cr.f1) if cr and cr.f1 is not none else '—' }}
            </td>
            <td class="num">{{ ct.total }}</td>
          {% endif %}
        </tr>
        {% endfor %}
      </tbody>
    </table>
    </div>
    {% else %}
      <div class="empty-note">Нет данных за выбранный период.</div>
    {% endif %}
  </div>
{% endfor %}

{% else %}
  <div class="empty-note">Нет данных для отображения.</div>
{% endif %}

<div class="methodology">
  <h2>📚 Методика (критерии Хандожко)</h2>
  <p>
    Матрица 2×2: <b>Hits</b> (прогноз ДА / факт ДА),
    <b>False alarms</b> (прогноз ДА / факт НЕТ),
    <b>Misses</b> (прогноз НЕТ / факт ДА),
    <b>Correct negatives</b> (прогноз НЕТ / факт НЕТ).
  </p>
  <p>
    <b>p</b> — общая оправдываемость: <code>(Hits + Correct) / Total</code>.<br>
    <b>H</b> — точность попаданий: <code>Hits / (Hits + False)</code>.<br>
    <b>τ</b> — критерий Обухова (полнота): <code>Hits / (Hits + Misses)</code>.<br>
    <b>v</b> — критерий Хайдке: <code>(Hits − False) / (Hits + False)</code>.<br>
    <b>Q</b> — критерий Пирси-Обухова: <code>(Hits·Correct − False·Misses) / ((Hits+Misses)(False+Correct))</code>.<br>
    <b>S</b> — критерий Хайдке: <code>p − v</code>.<br>
    <b>F1</b> — гармоническое среднее precision и recall.
  </p>
  <p>
    <b>Явления:</b> туман (код 45, 48), гроза (95, 96, 99),
    заморозок (T &lt; 0 °C), сильный ветер (&gt; 15 м/с), осадки (&gt; 0.1 мм/ч).
  </p>
</div>

""" + COMMON_JS +  render_legend("matrices") + """
</body>
</html>
"""




COMPARE_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Сводка — {{ station_name }}</title>
""" + BASE_STYLE + """
</head>
<body>

""" + render_header("analysis") + """
<h1>📋 Сводка явлений</h1>
<div style="margin: 8px 0 16px 0;">
  <a href="/compare/point" class="back" style="background:rgba(124,92,255,0.10);">🔍 Другая точка (поиск по названию)</a>
</div>
<div class="sub">{{ station_name }}</div>
<div class="legend">
  {% for r in results %}
    {% if not r.error %}
      <div class="legend-item">
        <span class="legend-dot" style="background:{{ r.color }};"></span>
        <span>{{ r.model_name }}</span>
      </div>
    {% endif %}
  {% endfor %}
</div>

{% if results %}
<div style="overflow-x:auto;">
<table class="summary-table">
  <thead>
    <tr>
      <th>Модель</th>
      {% for key, name, icon, _ in phenomena %}
        <th>{{ icon }} {{ name }}</th>
      {% endfor %}
      <th>Часов всего</th>
    </tr>
  </thead>
  <tbody>
    {% for r in results %}
      <tr>
        <td class="model-name">
          <span class="dot" style="background:{{ r.color }};"></span>
          {{ r.model_name }}
        </td>
        {% if r.error %}
          <td colspan="{{ phenomena|length + 1 }}" class="error-box">⚠️ {{ r.error }}</td>
        {% else %}
          {% for p in r.phenomena %}
            {% set cls = 'zero' if p.hours == 0 else ('high' if p.percent >= 30 else ('med' if p.percent >= 10 else 'low')) %}
            <td class="num {{ cls }}">
              {{ p.hours }} ч
              {% if p.hours > 0 %}
                <span class="bar" style="width: {{ [p.percent * 2, 40]|min }}px;"></span>
              {% endif %}
            </td>
          {% endfor %}
          <td class="num">{{ r.phenomena[0].total }}</td>
        {% endif %}
      </tr>
    {% endfor %}
  </tbody>
</table>
</div>

{% for key, name, icon, _ in phenomena %}
  <div class="phenom-block">
    <h2>{{ icon }} {{ name }}</h2>
    <div class="phenom-grid">
      {% for r in results %}
        {% if r.error %}
          <div class="phenom-card">
            <div class="model-name">
              <span class="dot" style="background:{{ r.color }};"></span>
              {{ r.model_name }}
            </div>
            <div style="color:#ff5470;font-size:12px;">⚠️ {{ r.error }}</div>
          </div>
        {% else %}
          {% set p = r.phenomena | selectattr("key", "equalto", key) | first %}
          {% set cls = 'zero' if p.hours == 0 else ('high' if p.percent >= 30 else ('med' if p.percent >= 10 else 'low')) %}
          <div class="phenom-card">
            <div class="model-name">
              <span class="dot" style="background:{{ r.color }};"></span>
              {{ r.model_name }}
            </div>
            <div class="count {{ cls }}">{{ p.hours }} ч</div>
            <div class="meta">{{ p.percent }} % от {{ p.total }} ч</div>
            {% if p.hours > 0 %}
              <div class="time-range">
                с {{ p.first_time[11:16] }} {{ p.first_time[8:10] }}.{{ p.first_time[5:7] }}
                по {{ p.last_time[11:16] }} {{ p.last_time[8:10] }}.{{ p.last_time[5:7] }}
              </div>
            {% endif %}
          </div>
        {% endif %}
      {% endfor %}
    </div>
  </div>
{% endfor %}

{% else %}
  <div class="empty-note">Нет данных для отображения.</div>
{% endif %}

""" + COMMON_JS +  render_legend("analysis") + """
</body>
</html>
"""




ALT_VERIFY_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Матрица — {{ title }} — {{ phenomena[phenomenon].name }}</title>
""" + BASE_STYLE + """
<style>
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

  .matrix-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px; margin: 16px 0;
  }
  .matrix-card {
    padding: 20px; border-radius: 16px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border); backdrop-filter: blur(14px);
  }
  .matrix-card.best {
    border-color: rgba(0,229,160,0.5);
    box-shadow: 0 0 24px -8px rgba(0,229,160,0.4);
  }
  .matrix-card h3 {
    margin: 0 0 14px 0; font-size: 16px; font-weight: 700;
    display: flex; justify-content: space-between; align-items: center;
  }
  .matrix-card h3 .tag {
    font-size: 10px; padding: 3px 8px; border-radius: 4px;
    background: rgba(0,229,160,0.15); color: #00e5a0; font-weight: 600;
  }

  .matrix-2x2 {
    display: grid; grid-template-columns: 80px 1fr 1fr;
    gap: 4px; margin: 14px 0;
  }
  .matrix-cell {
    padding: 14px 12px; text-align: center; border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
  }
  .matrix-cell.header {
    background: transparent; color: var(--text-2);
    font-size: 11px; font-weight: 600; text-transform: uppercase;
  }
  .matrix-cell.axis {
    background: transparent; color: var(--text-2);
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    display: flex; align-items: center; justify-content: flex-end;
    padding-right: 10px;
  }
  .matrix-cell.hits {
    background: rgba(0,229,160,0.15); color: #00e5a0;
    border: 1px solid rgba(0,229,160,0.3);
  }
  .matrix-cell.correct {
    background: rgba(77,171,255,0.12); color: #4dabff;
    border: 1px solid rgba(77,171,255,0.25);
  }
  .matrix-cell.misses {
    background: rgba(255,84,112,0.15); color: #ff5470;
    border: 1px solid rgba(255,84,112,0.3);
  }
  .matrix-cell.false_alarms {
    background: rgba(255,181,71,0.15); color: #ffb547;
    border: 1px solid rgba(255,181,71,0.3);
  }
  .matrix-cell .num { font-size: 22px; font-weight: 700; display: block; }
  .matrix-cell .lbl { font-size: 10px; opacity: 0.75; display: block; }

  .criteria-table {
    width: 100%; border-collapse: collapse; font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 12px;
  }
  .criteria-table td {
    padding: 6px 8px; border-bottom: 1px solid rgba(120,160,255,0.06);
  }
  .criteria-table td.lbl {
    color: var(--text-2); font-family: 'Inter', sans-serif;
    font-size: 12px;
  }
  .criteria-table td.val {
    text-align: right; font-weight: 600;
  }
  .criteria-table td.val.good { color: #00e5a0; }
  .criteria-table td.val.warn { color: #ffb547; }
  .criteria-table td.val.bad  { color: #ff5470; }

  .by-day-table {
    width: 100%; border-collapse: collapse; font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
  }
  .by-day-table th {
    text-align: left; padding: 8px 10px; color: var(--text-2);
    font-weight: 600; font-size: 11px; text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  .by-day-table td {
    padding: 6px 10px;
    border-bottom: 1px solid rgba(120,160,255,0.06);
  }
  .by-day-table tr:hover td { background: rgba(77,171,255,0.05); }

  .section {
    margin: 24px 0; padding: 20px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; backdrop-filter: blur(14px);
  }
  .section h2 {
    margin: 0 0 16px 0; font-size: 18px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }

  .methodology {
    margin: 24px 0; padding: 20px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; font-size: 13px; color: var(--text-1);
    line-height: 1.7;
  }
  .methodology h2 {
    margin: 0 0 12px 0; font-size: 16px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .methodology code {
    background: rgba(120,160,255,0.08); padding: 2px 6px;
    border-radius: 4px; font-family: 'JetBrains Mono', monospace;
    font-size: 12px; color: var(--accent);
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

""" + render_header("analysis") + """
<h1>📋 Матрица альтернативных прогнозов</h1>
<div class="sub">{{ title }} · {{ lat }}, {{ lon }} · {{ phenomena[phenomenon].name }} · {{ days }} дней</div>

<div class="controls">
  <label>Явление:</label>
  {% for key, ph in phenomena.items() %}
    {% set url = ('/alt-verify/' ~ station_key) if station_key else '/alt-verify' %}
    <a href="{{ url }}?phenomenon={{ key }}&days={{ days }}{% if not station_key %}&lat={{ lat }}&lon={{ lon }}&name={{ title }}{% endif %}"
       class="{% if phenomenon == key %}active{% endif %}">{{ ph.name }}</a>
  {% endfor %}
</div>

<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    {% set url = ('/alt-verify/' ~ station_key) if station_key else '/alt-verify' %}
    <a href="{{ url }}?phenomenon={{ phenomenon }}&days={{ d }}{% if not station_key %}&lat={{ lat }}&lon={{ lon }}&name={{ title }}{% endif %}"
       class="{% if d == days %}active{% endif %}">{{ d }} дней</a>
  {% endfor %}
</div>

<div class="matrix-grid">
  {% for r in results %}
    {% if r.error %}
      <div class="matrix-card">
        <h3>{{ r.model_name }} <span class="tag" style="background:rgba(255,84,112,0.15);color:#ff5470;">ОШИБКА</span></h3>
        <div class="error-box">⚠️ {{ r.error }}</div>
      </div>
    {% else %}
      <div class="matrix-card {% if r.model_key == best_model_key %}best{% endif %}">
        <h3>
          {{ r.model_name }}
          {% if r.model_key == best_model_key %}
            <span class="tag">🏆 лучшая</span>
          {% else %}
            <span class="tag" style="background:rgba(77,171,255,0.15);color:var(--accent);">{{ r.model_key | upper }}</span>
          {% endif %}
        </h3>

        {% set ct = r.contingency %}
        <div class="matrix-2x2">
          <div class="matrix-cell header"></div>
          <div class="matrix-cell header">Факт: ДА</div>
          <div class="matrix-cell header">Факт: НЕТ</div>

          <div class="matrix-cell axis">Прогноз: ДА</div>
          <div class="matrix-cell hits">
            <span class="num">{{ ct.hits }}</span>
            <span class="lbl">Hits</span>
          </div>
          <div class="matrix-cell false_alarms">
            <span class="num">{{ ct.false_alarms }}</span>
            <span class="lbl">False alarms</span>
          </div>

          <div class="matrix-cell axis">Прогноз: НЕТ</div>
          <div class="matrix-cell misses">
            <span class="num">{{ ct.misses }}</span>
            <span class="lbl">Misses</span>
          </div>
          <div class="matrix-cell correct">
            <span class="num">{{ ct.correct_negatives }}</span>
            <span class="lbl">Correct neg.</span>
          </div>
        </div>

        <div style="color:var(--text-2);font-size:11px;text-align:center;margin:8px 0 4px 0;">
          Всего часов: {{ ct.total }} · Факт ДА: {{ ct.fact_yes }} · Прогноз ДА: {{ ct.fcst_yes }}
        </div>

        {% if r.criteria %}
          {% set cr = r.criteria %}
          <table class="criteria-table">
            <tr>
              <td class="lbl">p — общая оправдываемость</td>
              <td class="val {% if cr.p > 0.9 %}good{% elif cr.p > 0.7 %}warn{% else %}bad{% endif %}">
                {{ '%.3f'|format(cr.p) if cr.p is not none else '—' }}
              </td>
            </tr>
            <tr>
              <td class="lbl">H — точность попаданий</td>
              <td class="val {% if cr.H and cr.H > 0.6 %}good{% elif cr.H and cr.H > 0.4 %}warn{% else %}bad{% endif %}">
                {{ '%.3f'|format(cr.H) if cr.H is not none else '—' }}
              </td>
            </tr>
            <tr>
              <td class="lbl">τ — критерий Обухова (полнота)</td>
              <td class="val {% if cr.tau and cr.tau > 0.6 %}good{% elif cr.tau and cr.tau > 0.4 %}warn{% else %}bad{% endif %}">
                {{ '%.3f'|format(cr.tau) if cr.tau is not none else '—' }}
              </td>
            </tr>
            <tr>
              <td class="lbl">v — критерий Хайдке</td>
              <td class="val {% if cr.v and cr.v > 0.3 %}good{% elif cr.v and cr.v > 0 %}warn{% else %}bad{% endif %}">
                {{ '%.3f'|format(cr.v) if cr.v is not none else '—' }}
              </td>
            </tr>
            <tr>
              <td class="lbl">Q — критерий Пирси-Обухова</td>
              <td class="val {% if cr.Q and cr.Q > 0.5 %}good{% elif cr.Q and cr.Q > 0.2 %}warn{% else %}bad{% endif %}">
                {{ '%.3f'|format(cr.Q) if cr.Q is not none else '—' }}
              </td>
            </tr>
            <tr>
              <td class="lbl">A — критерий успешности</td>
              <td class="val">{{ '%.3f'|format(cr.A) if cr.A is not none else '—' }}</td>
            </tr>
            <tr>
              <td class="lbl">S — критерий Хайдке (p − v)</td>
              <td class="val">{{ '%.3f'|format(cr.S) if cr.S is not none else '—' }}</td>
            </tr>
            <tr>
              <td class="lbl">F1 (для сравнения)</td>
              <td class="val {% if cr.f1 and cr.f1 > 0.5 %}good{% elif cr.f1 and cr.f1 > 0.3 %}warn{% else %}bad{% endif %}">
                {{ '%.3f'|format(cr.f1) if cr.f1 is not none else '—' }}
              </td>
            </tr>
          </table>
        {% endif %}
      </div>
    {% endif %}
  {% endfor %}
</div>

{% if not results %}
  <div class="error-box">Нет данных для отображения. Проверьте параметры.</div>
{% endif %}

{% if results | length > 1 %}
<div class="section">
  <h2>📊 Сравнение критериев по моделям</h2>
  <div style="overflow-x:auto;">
  <table class="by-day-table">
    <thead>
      <tr>
        <th>Модель</th>
        <th>p</th>
        <th>H</th>
        <th>τ</th>
        <th>v</th>
        <th>Q</th>
        <th>S</th>
        <th>F1</th>
        <th>Часов</th>
      </tr>
    </thead>
    <tbody>
      {% for r in results %}
      <tr {% if r.model_key == best_model_key %}style="background:rgba(0,229,160,0.06);"{% endif %}>
        <td>
          {{ r.model_name }}
          {% if r.model_key == best_model_key %}🏆{% endif %}
        </td>
        {% if r.criteria %}
          <td>{{ '%.3f'|format(r.criteria.p) if r.criteria.p is not none else '—' }}</td>
          <td>{{ '%.3f'|format(r.criteria.H) if r.criteria.H is not none else '—' }}</td>
          <td>{{ '%.3f'|format(r.criteria.tau) if r.criteria.tau is not none else '—' }}</td>
          <td>{{ '%.3f'|format(r.criteria.v) if r.criteria.v is not none else '—' }}</td>
          <td>{{ '%.3f'|format(r.criteria.Q) if r.criteria.Q is not none else '—' }}</td>
          <td>{{ '%.3f'|format(r.criteria.S) if r.criteria.S is not none else '—' }}</td>
          <td>{{ '%.3f'|format(r.criteria.f1) if r.criteria.f1 is not none else '—' }}</td>
          <td>{{ r.contingency.total }}</td>
        {% else %}
          <td colspan="8" style="color:#ff5470;">{{ r.error or '—' }}</td>
        {% endif %}
      </tr>
      {% endfor %}
    </tbody>
  </table>
  </div>
</div>
{% endif %}

<div class="methodology">
  <h2>📚 Методика (критерии Хандожко)</h2>
  <p>
    Матрица 2×2: <b>Hits</b> (прогноз ДА / факт ДА),
    <b>False alarms</b> (прогноз ДА / факт НЕТ),
    <b>Misses</b> (прогноз НЕТ / факт ДА),
    <b>Correct negatives</b> (прогноз НЕТ / факт НЕТ).
  </p>
  <p>
    <b>p</b> — общая оправдываемость: <code>(Hits + Correct) / Total</code>.<br>
    <b>H</b> — точность попаданий: <code>Hits / (Hits + False)</code>.<br>
    <b>τ</b> — критерий Обухова (полнота): <code>Hits / (Hits + Misses)</code>.<br>
    <b>v</b> — критерий Хайдке: <code>(Hits − False) / (Hits + False)</code>.<br>
    <b>Q</b> — критерий Пирси-Обухова: <code>(Hits·Correct − False·Misses) / ((Hits+Misses)(False+Correct))</code>.<br>
    <b>A</b> — критерий успешности: <code>(Hits + Correct) / Total</code>.<br>
    <b>S</b> — критерий Хайдке: <code>p − v</code>.
  </p>
  <p>
    <b>Явления:</b> туман (код 45, 48), гроза (95, 96, 99),
    заморозок (T &lt; 0 °C), сильный ветер (&gt; 15 м/с), осадки (&gt; 0.1 мм/ч).
  </p>
</div>

""" + COMMON_JS +  render_legend("matrices") + """
</body>
</html>
"""




COMPARE_POINT_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Сводка явлений — {% if station_name %}{{ station_name }}{% else %}Поиск точки{% endif %}</title>
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
  .search-row input {
    padding: 10px 14px; background: var(--bg-1);
    border: 1px solid var(--border); border-radius: 10px;
    color: var(--text-0); font-size: 14px; outline: none;
    transition: border-color 0.2s;
  }
  .search-row input:focus { border-color: var(--accent); }
  .search-row input.q { flex: 1; min-width: 220px; }
  .search-row input.coord {
    width: 130px; font-family: 'JetBrains Mono', monospace;
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
  .hint { font-size: 12px; color: var(--text-2); }

  .results-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 12px; margin-top: 12px;
  }
  .result-card {
    padding: 14px 18px; border-radius: 14px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    backdrop-filter: blur(14px);
    transition: all 0.2s;
  }
  .result-card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--card-shadow);
  }
  .result-card .place { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
  .result-card .meta {
    color: var(--text-2); font-size: 12px; margin-bottom: 10px;
    font-family: 'JetBrains Mono', monospace;
  }
  .result-card .actions { display: flex; gap: 6px; flex-wrap: wrap; }
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

  .legend {
    display: flex; gap: 16px; flex-wrap: wrap;
    padding: 12px 18px; margin-bottom: 16px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 14px; font-size: 13px;
    backdrop-filter: blur(14px);
  }
  .legend-item { display: flex; align-items: center; gap: 8px; }
  .legend-dot { display: inline-block; width: 14px; height: 14px; border-radius: 3px; }

  .summary-table {
    width: 100%; border-collapse: collapse; font-size: 13px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; overflow: hidden;
    backdrop-filter: blur(14px);
    margin-bottom: 24px;
  }
  .summary-table th {
    text-align: left; padding: 12px 14px;
    color: var(--text-2); font-weight: 600; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.5px;
    border-bottom: 1px solid var(--border);
    background: rgba(15,21,36,0.4);
  }
  .summary-table td {
    padding: 12px 14px;
    border-bottom: 1px solid rgba(120,160,255,0.06);
    font-family: 'JetBrains Mono', monospace;
  }
  .summary-table tr:hover td { background: rgba(77,171,255,0.05); }
  .summary-table tr:last-child td { border-bottom: none; }
  .summary-table td.model-name {
    font-family: 'Inter', sans-serif; font-weight: 600;
    display: flex; align-items: center; gap: 10px;
  }
  .summary-table td .dot {
    display: inline-block; width: 10px; height: 10px; border-radius: 2px;
  }
  .summary-table td.num { font-weight: 700; }
  .summary-table td.num.zero { color: var(--text-2); font-weight: 500; }
  .summary-table td.num.low  { color: #00e5a0; }
  .summary-table td.num.med  { color: #ffb547; }
  .summary-table td.num.high { color: #ff5470; }

  .bar {
    display: inline-block; height: 6px; border-radius: 3px;
    background: linear-gradient(90deg, #4dabff, #7c5cff);
    vertical-align: middle; margin-left: 8px;
  }

  .phenom-block {
    margin: 24px 0; padding: 20px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; backdrop-filter: blur(14px);
  }
  .phenom-block h2 {
    margin: 0 0 16px 0; font-size: 18px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .phenom-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
  }
  .phenom-card {
    padding: 14px 16px; border-radius: 12px;
    background: rgba(15,21,36,0.4);
    border: 1px solid var(--border);
  }
  .phenom-card .model-name {
    font-size: 13px; color: var(--text-0); font-weight: 600;
    margin-bottom: 8px; display: flex; align-items: center; gap: 8px;
  }
  .phenom-card .model-name .dot {
    display: inline-block; width: 10px; height: 10px; border-radius: 2px;
  }
  .phenom-card .count {
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px; font-weight: 700;
  }
  .phenom-card .count.zero { color: var(--text-2); }
  .phenom-card .count.low  { color: #00e5a0; }
  .phenom-card .count.med  { color: #ffb547; }
  .phenom-card .count.high { color: #ff5470; }
  .phenom-card .meta {
    color: var(--text-2); font-size: 11px; margin-top: 6px;
    font-family: 'JetBrains Mono', monospace;
  }
  .phenom-card .time-range {
    color: var(--text-2); font-size: 11px; margin-top: 4px;
  }

  .error-box {
    background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    border-radius: 12px; padding: 16px; color: #ff5470;
    margin: 16px 0;
  }
  .empty-note { color: var(--text-2); padding: 20px; font-size: 14px; }
</style>
</head>
<body>

""" + render_header("analysis") + """
<h1>📋 Сводка явлений</h1>
<div class="sub">
  {% if station_name %}
    {{ station_name }} · {{ preset_lat }}, {{ preset_lon }} · прогноз на {{ days }} дней
  {% else %}
    Поиск любой точки: введите название или координаты
  {% endif %}
</div>

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
</div>

<div id="results"></div>

{% if results %}
  <div class="controls">
    <label>Период:</label>
    {% for d in days_options %}
      <a href="/compare/point?lat={{ preset_lat }}&lon={{ preset_lon }}&name={{ station_name }}&days={{ d }}"
         class="{% if d == days %}active{% endif %}">{{ d }} дней</a>
    {% endfor %}
  </div>

  <div class="legend">
    {% for r in results %}
      {% if not r.error %}
        <div class="legend-item">
          <span class="legend-dot" style="background:{{ r.color }};"></span>
          <span>{{ r.model_name }}</span>
        </div>
      {% endif %}
    {% endfor %}
  </div>

  <div style="overflow-x:auto;">
  <table class="summary-table">
    <thead>
      <tr>
        <th>Модель</th>
        {% for key, name, icon, _ in phenomena %}
          <th>{{ icon }} {{ name }}</th>
        {% endfor %}
        <th>Часов всего</th>
      </tr>
    </thead>
    <tbody>
      {% for r in results %}
        <tr>
          <td class="model-name">
            <span class="dot" style="background:{{ r.color }};"></span>
            {{ r.model_name }}
          </td>
          {% if r.error %}
            <td colspan="{{ phenomena|length + 1 }}" class="error-box">⚠️ {{ r.error }}</td>
          {% else %}
            {% for p in r.phenomena %}
              {% set cls = 'zero' if p.hours == 0 else ('high' if p.percent >= 30 else ('med' if p.percent >= 10 else 'low')) %}
              <td class="num {{ cls }}">
                {{ p.hours }} ч
                {% if p.hours > 0 %}
                  <span class="bar" style="width: {{ [p.percent * 2, 40]|min }}px;"></span>
                {% endif %}
              </td>
            {% endfor %}
            <td class="num">{{ r.phenomena[0].total }}</td>
          {% endif %}
        </tr>
      {% endfor %}
    </tbody>
  </table>
  </div>

  {% for key, name, icon, _ in phenomena %}
    <div class="phenom-block">
      <h2>{{ icon }} {{ name }}</h2>
      <div class="phenom-grid">
        {% for r in results %}
          {% if r.error %}
            <div class="phenom-card">
              <div class="model-name">
                <span class="dot" style="background:{{ r.color }};"></span>
                {{ r.model_name }}
              </div>
              <div style="color:#ff5470;font-size:12px;">⚠️ {{ r.error }}</div>
            </div>
          {% else %}
            {% set p = r.phenomena | selectattr("key", "equalto", key) | first %}
            {% set cls = 'zero' if p.hours == 0 else ('high' if p.percent >= 30 else ('med' if p.percent >= 10 else 'low')) %}
            <div class="phenom-card">
              <div class="model-name">
                <span class="dot" style="background:{{ r.color }};"></span>
                {{ r.model_name }}
              </div>
              <div class="count {{ cls }}">{{ p.hours }} ч</div>
              <div class="meta">{{ p.percent }} % от {{ p.total }} ч</div>
              {% if p.hours > 0 %}
                <div class="time-range">
                  с {{ p.first_time[11:16] }} {{ p.first_time[8:10] }}.{{ p.first_time[5:7] }}
                  по {{ p.last_time[11:16] }} {{ p.last_time[8:10] }}.{{ p.last_time[5:7] }}
                </div>
              {% endif %}
            </div>
          {% endif %}
        {% endfor %}
      </div>
    </div>
  {% endfor %}
{% endif %}

<script>
  function actionsHtml(name, lat, lon) {
    var encName = encodeURIComponent(name);
    return ''
      + '<div class="actions">'
      + '  <a href="/compare/point?lat=' + lat + '&lon=' + lon + '&name=' + encName + '">📋 Сводка явлений</a>'
      + '  <a href="/forecast/point?lat=' + lat + '&lon=' + lon + '&name=' + encName + '&model=gfs">📊 Таблица</a>'
      + '  <a href="/point-synoptic?lat=' + lat + '&lon=' + lon + '&name=' + encName + '&model=gfs">🌡 Синоптика</a>'
      + '</div>';
  }

  async function doSearch() {
    var q = document.getElementById('q').value.trim();
    if (!q) return;
    var results = document.getElementById('results');

    var coordMatch = q.match(/^(-?\\d+\\.?\\d*)[\\s,]+(-?\\d+\\.?\\d*)$/);
    if (coordMatch) {
      var lat = parseFloat(coordMatch[1]);
      var lon = parseFloat(coordMatch[2]);
      if (lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
        var name = lat + ', ' + lon;
        var encName = encodeURIComponent(name);
        window.location.href = '/compare/point?lat=' + lat + '&lon=' + lon + '&name=' + encName;
        return;
      }
    }

    results.innerHTML = '<div style="color:var(--accent);padding:20px;text-align:center;">⏳ Поиск...</div>';

    try {
      var resp = await fetch('/api/geocode?q=' + encodeURIComponent(q));
      var data = await resp.json();

      if (data.error) {
        results.innerHTML = '<div class="error-box">Ошибка: ' + data.error + '</div>';
        return;
      }
      if (!data.results || data.results.length === 0) {
        results.innerHTML = '<div class="empty-note">Ничего не найдено. Попробуйте другое название или введите координаты.</div>';
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

        html += '<div class="result-card">'
              + '<div class="place">📍 ' + p.name + '</div>'
              + '<div class="meta">' + meta + '</div>'
              + actionsHtml(label, p.latitude, p.longitude)
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
    if (isNaN(lat) || isNaN(lon)) { alert('Введите корректные координаты'); return; }
    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      alert('Широта: -90…90, долгота: -180…180');
      return;
    }
    var name = lat + ', ' + lon;
    var encName = encodeURIComponent(name);
    window.location.href = '/compare/point?lat=' + lat + '&lon=' + lon + '&name=' + encName;
  }
</script>

""" + COMMON_JS +  """
</body>
</html>
"""
