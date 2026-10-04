# -*- coding: utf-8 -*-
"""Синоптика, авиация, тропопауза."""

from ui.styles import (
    BASE_STYLE,
    COMMON_JS,
    render_header,
    render_legend,
    render_biblio_ref,
)
TROPOPAUSE_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Тропопауза — {{ station_name }}</title>
""" + BASE_STYLE + """
<style>
  .controls {
    display: flex; gap: 12px; flex-wrap: wrap; align-items: center;
    margin: 16px 0 20px 0; padding: 14px 18px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 14px;
    backdrop-filter: blur(14px);
  }
  .controls label { color: var(--text-1); font-size: 13px; }
  .controls a {
    padding: 8px 14px; border-radius: 10px; font-size: 13px;
    background: var(--bg-1); border: 1px solid var(--border);
    color: var(--text-0); text-decoration: none;
    transition: all 0.2s;
  }
  .controls a:hover { border-color: var(--border-hover); }
  .controls a.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25), rgba(124,92,255,0.25));
    border-color: var(--accent);
  }

  .summary-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px; margin: 16px 0 24px 0;
  }
  .summary-card {
    padding: 14px 18px; border-radius: 14px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
  }
  .summary-card .lbl {
    color: var(--text-2); font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .summary-card .val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px; font-weight: 700; margin-top: 6px;
  }
  .summary-card .val.good { color: #00e5a0; }
  .summary-card .val.warn { color: #ffb547; }
  .summary-card .val.bad  { color: #ff5470; }

  .profile-table {
    width: 100%; border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace; font-size: 12px;
    margin-top: 12px;
  }
  .profile-table th {
    text-align: left; padding: 8px 10px; color: var(--text-2);
    font-weight: 600; font-size: 11px; text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  .profile-table td {
    padding: 8px 10px;
    border-bottom: 1px solid rgba(120,160,255,0.06);
  }
  .profile-table tr:hover td { background: rgba(77,171,255,0.05); }
  .profile-table tr.strato td { background: rgba(124,92,255,0.08); }
  .profile-table tr.tropo td  { background: rgba(77,171,255,0.06); }
  .profile-table tr.tropopause td {
    border-top: 2px solid #ffb547;
    border-bottom: 2px solid #ffb547;
    font-weight: 700;
  }
  .profile-table td.num { font-weight: 600; }
  .profile-table td.num.good { color: #00e5a0; }
  .profile-table td.num.warn { color: #ffb547; }
  .profile-table td.num.bad  { color: #ff5470; }

  .hour-chart {
    display: flex; align-items: flex-end; gap: 4px;
    height: 100px; padding: 8px 0; margin-top: 12px;
    border-bottom: 1px solid var(--border);
  }
  .hour-chart .bar {
    flex: 1; min-height: 2px; border-radius: 4px 4px 0 0;
    background: linear-gradient(180deg, var(--accent), rgba(77,171,255,0.3));
    position: relative; transition: opacity 0.2s;
  }
  .hour-chart .bar.fold {
    background: linear-gradient(180deg, #ff5470, rgba(255,84,112,0.3));
  }
  .hour-chart .bar:hover { opacity: 0.7; }
  .hour-chart .bar:hover::after {
    content: attr(data-label);
    position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%);
    background: var(--bg-0); padding: 6px 10px; border-radius: 6px;
    font-size: 11px; white-space: nowrap; border: 1px solid var(--border);
    z-index: 10;
  }

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

  .description-box {
    padding: 16px; border-radius: 12px; font-size: 14px;
    line-height: 1.6; margin-top: 12px;
  }
  .desc-fold    { background: rgba(255,84,112,0.12);
                  border: 1px solid rgba(255,84,112,0.4);
                  color: #ff5470; }
  .desc-no-fold { background: rgba(0,229,160,0.10);
                  border: 1px solid rgba(0,229,160,0.3);
                  color: #00e5a0; }

  .error-box {
    background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    border-radius: 12px; padding: 16px; color: #ff5470;
    margin: 16px 0;
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
  .methodology ul { padding-left: 22px; }
  .methodology ul li { margin: 4px 0; }
</style>
</head>
<body>

""" + render_header("theory") + """
<h1>🌀 Складки тропопаузы</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · {{ target_date }} · EPV (Ertel PV) · 2 PVU</div>

{% if error %}
  <div class="error-box">⚠️ {{ error }}</div>
{% endif %}

<div class="controls">
  <label>Станция:</label>
  {% for key, st in stations.items() %}
    <a href="/tropopause?station={{ key }}&hour={{ hour_index }}&date={{ target_date }}"
       class="{% if key == station_key %}active{% endif %}">{{ st.name }}</a>
  {% endfor %}
</div>

<div class="controls">
  <label>Час (МСК):</label>
  {% for h in hours_options %}
    <a href="/tropopause?station={{ station_key }}&hour={{ h }}&date={{ target_date }}"
       class="{% if h == hour_index %}active{% endif %}">{{ '%02d'|format(h) }}:00</a>
  {% endfor %}
</div>

{% if analysis and summary %}
<div class="summary-grid">
  <div class="summary-card">
    <div class="lbl">Всего часов</div>
    <div class="val">{{ summary.total_hours }}</div>
  </div>

  <div class="summary-card">
    <div class="lbl">Часов со складкой</div>
    <div class="val {% if summary.folds_count == 0 %}good{% elif summary.folds_count < 6 %}warn{% else %}bad{% endif %}">
      {{ summary.folds_count }}
    </div>
  </div>

  <div class="summary-card">
    <div class="lbl">Макс. PV за день</div>
    <div class="val {% if summary.max_pv_day >= 2 %}bad{% elif summary.max_pv_day >= 1 %}warn{% else %}good{% endif %}">
      {{ '%.2f'|format(summary.max_pv_day) }}
    </div>
    <div style="color:var(--text-2);font-size:11px;margin-top:4px;">PVU</div>
  </div>

  {% if selected %}
  <div class="summary-card">
    <div class="lbl">Уровень тропопаузы</div>
    <div class="val">
      {% if selected.tropopause_level_hPa %}
        {{ selected.tropopause_level_hPa }} гПа
      {% else %}—{% endif %}
    </div>
    <div style="color:var(--text-2);font-size:11px;margin-top:4px;">
      на {{ '%02d'|format(hour_index) }}:00
    </div>
  </div>
  {% endif %}
</div>

<div class="section">
  <h2>📊 Динамика PV по часам</h2>
  {% if all_hours and max_pv_day_scale %}
    <div class="hour-chart">
      {% for h in all_hours %}
        <div class="bar {% if h.has_fold %}fold{% endif %}"
             style="height: {{ (h.max_pv / max_pv_day_scale * 100) if max_pv_day_scale else 2 }}%;"
             data-label="{{ h.time[11:16] }}: PV={{ '%.2f'|format(h.max_pv) }} PVU">
        </div>
      {% endfor %}
    </div>
    <div style="font-size:11px;color:var(--text-2);text-align:center;margin-top:6px;">
      00:00 → 23:00 · красные бары — часы со складкой
    </div>
  {% else %}
    <div style="color:var(--text-2);padding:20px;">Нет данных для графика.</div>
  {% endif %}
</div>

{% if selected %}
<div class="section">
  <h2>🔍 Анализ часа {{ '%02d'|format(hour_index) }}:00</h2>
  <div class="description-box {% if selected.has_fold %}desc-fold{% else %}desc-no-fold{% endif %}">
    {% if selected.has_fold %}⚠️{% else %}✅{% endif %}
    {{ selected.description }}
  </div>
</div>

<div class="section">
  <h2>📋 Профиль атмосферы (PV, T, θ)</h2>
  {% if selected.profile %}
  <div style="overflow-x:auto;">
  <table class="profile-table">
    <thead>
      <tr>
        <th>Уровень</th>
        <th>Высота</th>
        <th>T, °C</th>
        <th>θ, K</th>
        <th>Ветер</th>
        <th>PV, PVU</th>
        <th>Слой</th>
      </tr>
    </thead>
    <tbody>
      {% for p in selected.profile %}
      <tr class="{% if p.level == selected.tropopause_level_hPa %}tropopause{% elif p.get('is_stratosphere') %}strato{% elif p.get('is_stratosphere') is not none %}tropo{% endif %}">
        <td class="num">{{ p.level }} гПа</td>
        <td class="num">{{ '%.0f'|format(p.height_m) if p.height_m is not none else '—' }} м</td>
        <td class="num">{{ '%.1f'|format(p.temp_c) if p.temp_c is not none else '—' }}</td>
        <td class="num">{{ '%.1f'|format(p.theta_k) if p.theta_k is not none else '—' }}</td>
        <td>
          {% if p.wind_ms is not none %}
            {{ '%.0f'|format(p.wind_ms) }} м/с {{ p.wind_dir or '' }}°
          {% else %}—{% endif %}
        </td>
        <td class="num {% if p.get('pv_pvu') is not none and p.get('pv_pvu') >= 2 %}bad{% elif p.get('pv_pvu') is not none and p.get('pv_pvu') >= 1 %}warn{% else %}good{% endif %}">
          {{ '%.2f'|format(p.get('pv_pvu')) if p.get('pv_pvu') is not none else '—' }}
        </td>
        <td>
          {% if p.level == selected.tropopause_level_hPa %}
            <span style="color:#ffb547;font-weight:700;">🌀 тропопауза</span>
          {% elif p.get('is_stratosphere') %}
            <span style="color:#a78bfa;">стратосфера</span>
          {% elif p.get('is_stratosphere') is not none %}
            <span style="color:#4dabff;">тропосфера</span>
          {% else %}—{% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  </div>
  {% else %}
    <div style="color:var(--text-2);padding:20px;">Нет данных профиля.</div>
  {% endif %}
</div>
{% endif %}

{% endif %}

<div class="methodology">
  <h2>📚 Методика расчёта EPV</h2>
  <p>
    <b>Ertel PV (Potential Vorticity)</b> в изобарических координатах:<br>
    <code>PV = −g · (ζ + f) · (Δθ / Δp)</code>
  </p>
  <p>где:
    <ul>
      <li><code>g = 9.81 м/с²</code> — ускорение свободного падения</li>
      <li><code>ζ</code> — относительная завихрённость (оценка через V/R)</li>
      <li><code>f = 2Ω·sin(φ)</code> — параметр Кориолиса</li>
      <li><code>Δθ</code> — разность потенциальных температур между уровнями</li>
      <li><code>Δp</code> — разность давлений (Па)</li>
    </ul>
  </p>
  <p>
    Единица: <code>1 PVU = 10⁻⁶ м²·К·кг⁻¹·с⁻¹</code>.
  </p>
  <p>
    <b>Динамическая тропопауза</b> — уровень, где PV = 2 PVU.
    <b>Складка тропопаузы</b> — область, где PV &gt; 2 PVU опускается
    ниже типичной высоты тропопаузы (ниже 300 гПа).
  </p>
</div>

""" + render_biblio_ref("dynamic") + """
""" + COMMON_JS +  render_legend("synoptic") + """
</body>
</html>
"""




AVIATION_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Авиация — {{ station_name }} — {{ model_name }}</title>
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

  .summary-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px; margin: 16px 0 24px 0;
  }
  .summary-card {
    padding: 14px 18px; border-radius: 14px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
  }
  .summary-card .lbl {
    color: var(--text-2); font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .summary-card .val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px; font-weight: 700; margin-top: 6px;
  }
  .summary-card .sub {
    color: var(--text-2); font-size: 11px; margin-top: 4px;
  }
  .summary-card .val.good { color: #00e5a0; }
  .summary-card .val.warn { color: #ffb547; }
  .summary-card .val.bad  { color: #ff5470; }

  .day-block {
    margin: 24px 0; padding: 16px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; backdrop-filter: blur(14px);
  }
  .day-header {
    margin-bottom: 12px; padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
  }
  .day-title { font-size: 16px; font-weight: 700; }

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
    padding: 8px 6px;
    border-bottom: 1px solid rgba(120,160,255,0.06);
    vertical-align: middle;
  }
  .hour-table tr:hover td { background: rgba(77,171,255,0.05); }

  .hour-cell { font-weight: 700; color: var(--accent); }
  .icon-cell { text-align: center; }
  .icon-cell svg { width: 26px; height: 26px; vertical-align: middle; }
  .num { font-weight: 600; }
  .num.good { color: #00e5a0; }
  .num.warn { color: #ffb547; }
  .num.bad  { color: #ff5470; }

  .badge {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 10px; font-weight: 600; margin: 1px 2px 1px 0;
  }
  .badge-thunder   { background: rgba(255,84,112,0.15); color: #ff5470;
                     border: 1px solid rgba(255,84,112,0.35); }
  .badge-fog       { background: rgba(124,92,255,0.15); color: #a78bfa;
                     border: 1px solid rgba(124,92,255,0.35); }
  .badge-none      { background: rgba(120,160,255,0.06); color: var(--text-2);
                     border: 1px solid var(--border); }

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

""" + render_header("forecast") + """
<h1>✈️ Авиационные прогнозы</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · {{ model_name }} · {{ days }} дня</div>

{% if error %}
  <div class="error-box">⚠️ {{ error }}</div>
{% endif %}

<div class="model-switcher">
  {% for m in model_switcher %}
    <a href="{% if is_point %}/point-aviation?lat={{ lat }}&lon={{ lon }}&name={{ station_name }}&model={{ m.key }}&days={{ days }}{% else %}/aviation/{{ m.key }}/{{ station_key }}?days={{ days }}{% endif %}"
       class="{% if m.active %}active{% endif %}">{{ m.name }}</a>
  {% endfor %}
</div>

<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    <a href="{% if is_point %}/point-aviation?lat={{ lat }}&lon={{ lon }}&name={{ station_name }}&model={{ model }}&days={{ d }}{% else %}/aviation/{{ model }}/{{ station_key }}?days={{ d }}{% endif %}"
       class="{% if d == days %}active{% endif %}">{{ d }} дн.</a>
  {% endfor %}
</div>

{% if summary and summary.hours_total %}
<div class="summary-grid">
  <div class="summary-card">
    <div class="lbl">Всего часов</div>
    <div class="val">{{ summary.hours_total }}</div>
    <div class="sub">в прогнозе</div>
  </div>

  <div class="summary-card">
    <div class="lbl">Часов с грозой</div>
    <div class="val {% if summary.thunder_hours == 0 %}good{% elif summary.thunder_hours < 6 %}warn{% else %}bad{% endif %}">
      {{ summary.thunder_hours }}
    </div>
    <div class="sub">макс. уровень: {{ summary.thunder_max_level }} ({{ summary.thunder_max_prob }}%)</div>
  </div>

  <div class="summary-card">
    <div class="lbl">Часов с туманом</div>
    <div class="val {% if summary.fog_hours == 0 %}good{% elif summary.fog_hours < 6 %}warn{% else %}bad{% endif %}">
      {{ summary.fog_hours }}
    </div>
    <div class="sub">макс. уровень: {{ summary.fog_max_level }} ({{ summary.fog_max_prob }}%)</div>
  </div>

  <div class="summary-card">
    <div class="lbl">Макс. K (Вайтинг)</div>
    <div class="val {% if summary.k_max is not none and summary.k_max < 20 %}good{% elif summary.k_max is not none and summary.k_max < 30 %}warn{% else %}bad{% endif %}">
      {{ '%.1f'|format(summary.k_max) if summary.k_max is not none else '—' }}
    </div>
    <div class="sub">порог грозы: K ≥ 20</div>
  </div>

  <div class="summary-card">
    <div class="lbl">Мин. LI</div>
    <div class="val {% if summary.li_min is not none and summary.li_min > 0 %}good{% elif summary.li_min is not none and summary.li_min > -2 %}warn{% else %}bad{% endif %}">
      {{ '%.1f'|format(summary.li_min) if summary.li_min is not none else '—' }}
    </div>
    <div class="sub">порог неустойчивости: LI &lt; 0</div>
  </div>

  <div class="summary-card">
    <div class="lbl">Макс. CAPE</div>
    <div class="val {% if summary.cape_max is not none and summary.cape_max < 300 %}good{% elif summary.cape_max is not none and summary.cape_max < 1500 %}warn{% else %}bad{% endif %}">
      {{ '%.0f'|format(summary.cape_max) if summary.cape_max is not none else '—' }}
    </div>
    <div class="sub">порог: CAPE ≥ 300 Дж/кг</div>
  </div>
</div>
{% endif %}

{% for day in days_list %}
<div class="day-block fade-in">
  <div class="day-header">
    <div class="day-title">📅 {{ day.date | date_ru }}</div>
  </div>

  <div style="overflow-x:auto;">
  <table class="hour-table">
    <thead>
      <tr>
        <th>Час</th>
        <th>Иконка</th>
        <th>T, °C</th>
        <th>Td, °C</th>
        <th>K</th>
        <th>LI</th>
        <th>CAPE</th>
        <th>Ветер</th>
        <th>Гроза</th>
        <th>Туман</th>
      </tr>
    </thead>
    <tbody>
      {% for h in day.rows %}
      {% set avt = h.av_thunder or {} %}
      {% set avf = h.av_fog or {} %}
      <tr>
        <td class="hour-cell">{{ h.time[11:16] }}</td>
        <td class="icon-cell">{{ h.icon_svg | safe }}</td>
        <td>{{ '%.1f'|format(h.temp_c) if h.temp_c is not none else '—' }}</td>
        <td>{{ '%.1f'|format(h.dew_point_c) if h.dew_point_c is not none else '—' }}</td>

        <td class="num {% if avt.k is not none and avt.k >= 30 %}bad{% elif avt.k is not none and avt.k >= 20 %}warn{% else %}good{% endif %}">
          {{ '%.1f'|format(avt.k) if avt.k is not none else '—' }}
        </td>
        <td class="num {% if avt.li is not none and avt.li <= -4 %}bad{% elif avt.li is not none and avt.li < 0 %}warn{% else %}good{% endif %}">
          {{ '%.1f'|format(avt.li) if avt.li is not none else '—' }}
        </td>
        <td class="num {% if avt.cape is not none and avt.cape >= 1500 %}bad{% elif avt.cape is not none and avt.cape >= 300 %}warn{% else %}good{% endif %}">
          {{ '%.0f'|format(avt.cape) if avt.cape is not none else '—' }}
        </td>

        <td>
          {% if h.wind_ms is not none %}
            {{ '%.0f'|format(h.wind_ms) }} м/с {{ h.wind_dir_text or '' }}
          {% else %}—{% endif %}
        </td>

        <td>
          {% if avt.combined_level and avt.combined_level not in ('нет', 'нет данных') %}
            <span class="badge badge-thunder" title="{{ avt.combined_text }} ({{ avt.combined_prob }}%)">
              ⚡ {{ avt.combined_level }} · {{ avt.combined_prob }}%
            </span>
          {% elif avt.combined_level %}
            <span class="badge badge-none">нет</span>
          {% else %}
            <span class="badge badge-none">—</span>
          {% endif %}
        </td>

        <td>
          {% if avf.level and avf.level not in ('нет', 'нет данных') %}
            <span class="badge badge-fog" title="{{ avf.text }} ({{ avf.probability }}%)">
              🌫 {{ avf.level }} · {{ avf.probability }}%
            </span>
          {% elif avf.level %}
            <span class="badge badge-none">нет</span>
          {% else %}
            <span class="badge badge-none">—</span>
          {% endif %}
        </td>
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

<div class="methodology">
  <h2>📚 Методика расчёта</h2>
  <p>
    <b>Индекс Вайтинга (K)</b> — по Богаткину:<br>
    <code>K = 2·T850 − T500 − (T850 − Td850) − (T700 − Td700)</code><br>
    Порог грозы: <code>K ≥ 20</code>. При <code>K ≥ 35</code> — повсеместные грозы с градом.
  </p>
  <p>
    <b>Lifted Index (LI)</b> — разность температур частицы и окружающей среды на 500 гПа:<br>
    <code>LI &lt; 0</code> — неустойчиво, <code>LI &lt; −4</code> — сильная неустойчивость.
  </p>
  <p>
    <b>CAPE</b> — доступная потенциальная энергия конвекции (Дж/кг):<br>
    <code>&lt; 300</code> — нет, <code>300–800</code> — слабая, <code>800–1500</code> — умеренная, <code>&gt; 1500</code> — сильная.
  </p>
  <p>
    <b>Вероятность грозы</b> — взвешенная сумма:<br>
    <code>P = 0.25·P(K) + 0.40·P(LI) + 0.35·P(CAPE)</code>
  </p>
  <p>
    <b>Туман</b> — по Кирюхину (модифицированный):
    проверяются 5 условий: дефицит точки росы ≤ 2 °C, ветер 0.5–3 м/с,
    облачность &lt; 30%, ночные часы (0–9), RH ≥ 90%.
    Каждое условие даёт +1 балл. Итог: 0–1 — нет, 2 — слабая, 3 — умеренная, 4 — высокая, 5 — очень высокая.
  </p>
</div>

""" + render_biblio_ref("aviation", "гл. 9–10") + """
""" + COMMON_JS +  render_legend("synoptic") + """
</body>
</html>
"""




SYNOPTIC_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Синоптика — {{ station_name }} — {{ model_name }}</title>
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

  .synoptic-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
    margin: 20px 0;
  }
  @media (max-width: 900px) {
    .synoptic-grid { grid-template-columns: 1fr; }
  }

  .section {
    padding: 20px; background: var(--card-bg);
    border: 1px solid var(--border); border-radius: 16px;
    backdrop-filter: blur(14px);
  }
  .section h2 {
    margin: 0 0 16px 0; font-size: 18px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }

  .profile-wrap {
    background: rgba(15,21,36,0.4);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px;
  }

  .text-block {
    white-space: pre-wrap; word-wrap: break-word;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px; line-height: 1.7;
    color: var(--text-1);
    background: rgba(15,21,36,0.4);
    padding: 16px; border-radius: 12px;
    border: 1px solid var(--border);
    max-height: 600px; overflow-y: auto;
  }

  .levels-table {
    width: 100%; border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace; font-size: 12px;
    margin-top: 12px;
  }
  .levels-table th {
    text-align: left; padding: 8px 10px; color: var(--text-2);
    font-weight: 600; font-size: 11px; text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  .levels-table td {
    padding: 8px 10px;
    border-bottom: 1px solid rgba(120,160,255,0.06);
  }
  .levels-table tr:hover td { background: rgba(77,171,255,0.05); }
  .levels-table td.num { font-weight: 600; }
  .levels-table td.num.good { color: #00e5a0; }
  .levels-table td.num.warn { color: #ffb547; }
  .levels-table td.num.bad  { color: #ff5470; }

  .badge {
    display: inline-block; padding: 3px 10px; border-radius: 6px;
    font-size: 11px; font-weight: 600; margin: 2px 4px 2px 0;
  }
  .badge-jet    { background: rgba(124,92,255,0.15); color: #a78bfa;
                  border: 1px solid rgba(124,92,255,0.35); }
  .badge-front  { background: rgba(255,84,112,0.15); color: #ff5470;
                  border: 1px solid rgba(255,84,112,0.35); }
  .badge-calm   { background: rgba(0,229,160,0.10); color: #00e5a0;
                  border: 1px solid rgba(0,229,160,0.3); }

  #synoptic-tooltip {
    position: fixed;
    pointer-events: none;
    z-index: 10000;
    background: var(--bg-0);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-0);
    box-shadow: 0 12px 30px rgba(0,0,0,0.45);
    display: none;
    white-space: nowrap;
    line-height: 1.6;
  }
  #synoptic-tooltip .tt-title {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 13px;
    margin-bottom: 6px;
    color: #ff5470;
  }
  #synoptic-tooltip .tt-row {
    display: flex;
    justify-content: space-between;
    gap: 16px;
  }
  #synoptic-tooltip .tt-row span:first-child {
    color: var(--text-2);
  }
  #synoptic-tooltip .tt-row span:last-child {
    font-weight: 600;
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

<body>
""" + render_header("forecast") + """
<h1>🌡 Синоптика по уровням</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · {{ model_name }} · {{ days }} дн.</div>

{% if error %}
  <div class="error-box">⚠️ {{ error }}</div>
{% endif %}

<div class="model-switcher">
  {% for m in model_switcher %}
    <a href="{% if is_point %}/point-synoptic?lat={{ lat }}&lon={{ lon }}&name={{ station_name }}&model={{ m.key }}&days={{ days }}&hour={{ hour_index }}{% else %}/synoptic/{{ m.key }}/{{ station_key }}?days={{ days }}&hour={{ hour_index }}{% endif %}"
       class="{% if m.active %}active{% endif %}">{{ m.name }}</a>
  {% endfor %}
</div>

<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    <a href="{% if is_point %}/point-synoptic?lat={{ lat }}&lon={{ lon }}&name={{ station_name }}&model={{ model }}&days={{ d }}&hour={{ hour_index }}{% else %}/synoptic/{{ model }}/{{ station_key }}?days={{ d }}&hour={{ hour_index }}{% endif %}"
       class="{% if d == days %}active{% endif %}">{{ d }} дн.</a>
  {% endfor %}
</div>

<div class="controls">
  <label>Час для профиля:</label>
  {% for h in hours_options %}
    <a href="{% if is_point %}/point-synoptic?lat={{ lat }}&lon={{ lon }}&name={{ station_name }}&model={{ model }}&days={{ days }}&hour={{ h }}{% else %}/synoptic/{{ model }}/{{ station_key }}?days={{ days }}&hour={{ h }}{% endif %}"
       class="{% if h == hour_index %}active{% endif %}">{{ '%02d'|format(h) }}:00</a>
  {% endfor %}
</div>

{% if hours %}
<div class="synoptic-grid">
  <div class="section">
    <h2>📈 Профиль T и θ ({{ '%02d'|format(hour_index) }}:00)</h2>
    <div class="profile-wrap">
      {{ profile_svg | safe }}
    </div>
  </div>

  <div class="section">
    <h2>📋 Текстовый разбор</h2>
    <div class="text-block">{{ text }}</div>
  </div>
</div>

<div class="section" style="margin-top:20px;">
  <h2>🔍 Данные по уровням ({{ '%02d'|format(hour_index) }}:00)</h2>
  {% set h = hours[hour_index] if hour_index < hours|length else hours[0] %}
  <div style="margin-bottom:12px;">
    {% if h.jet %}
      <span class="badge badge-jet">💨 Струя: {{ h.jet.speed }} м/с на 300 гПа ({{ h.jet.dir }}°)</span>
    {% else %}
      <span class="badge badge-calm">💨 Струя: нет</span>
    {% endif %}
    {% if h.frontal_zone %}
      <span class="badge badge-front">⚠️ Фронтальная зона{% if h.front_type %} ({{ h.front_type }}){% endif %}</span>
    {% else %}
      <span class="badge badge-calm">✓ Фронт: нет</span>
    {% endif %}
    {% if h.tropopause_hPa %}
      <span class="badge badge-jet">🌀 Тропопауза: {{ h.tropopause_hPa }} гПа{% if h.tropopause_type %} ({{ h.tropopause_type }}){% endif %}</span>
    {% else %}
      <span class="badge badge-calm">🌀 Тропопауза: не обнаружена</span>
    {% endif %}
  </div>
  <div style="overflow-x:auto;">
  <table class="levels-table">
    <thead>
      <tr>
        <th>Уровень</th>
        <th>H, м</th>
        <th>T, °C</th>
        <th>Td, °C</th>
        <th>θ, K</th>
        <th>RH, %</th>
        <th>mr, г/кг</th>
        <th>Ветер, м/с</th>
        <th>Напр.</th>
      </tr>
    </thead>
    <tbody>
      {% for lvl in levels %}
        {% set d = h.levels[lvl] if h.levels and lvl in h.levels else {} %}
        <tr>
          <td><b>{{ level_names[lvl] }}</b></td>
          <td class="num">{{ '%.0f'|format(d.height_m) if d.height_m is not none else '—' }}</td>
          <td class="num {% if d.t is not none and d.t < -50 %}bad{% elif d.t is not none and d.t < 0 %}warn{% else %}good{% endif %}">
            {{ '%.1f'|format(d.t) if d.t is not none else '—' }}
          </td>
          <td class="num">{{ '%.1f'|format(d.td) if d.td is not none else '—' }}</td>
          <td class="num">{{ '%.1f'|format(d.theta) if d.theta is not none else '—' }}</td>
          <td class="num {% if d.rh is not none and d.rh > 90 %}warn{% endif %}">
            {{ '%.0f'|format(d.rh) if d.rh is not none else '—' }}
          </td>
          <td class="num">{{ '%.1f'|format(d.mr) if d.mr is not none else '—' }}</td>
          <td class="num {% if d.wind_ms is not none and d.wind_ms > 30 %}bad{% elif d.wind_ms is not none and d.wind_ms > 15 %}warn{% endif %}">
            {{ '%.0f'|format(d.wind_ms) if d.wind_ms is not none else '—' }}
          </td>
          <td class="num">{{ '%.0f'|format(d.wind_dir) if d.wind_dir is not none else '—' }}°</td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
  </div>
</div>

<div class="section" style="margin-top:20px;">
  <h2>📊 Индексы неустойчивости ({{ '%02d'|format(hour_index) }}:00)</h2>
  {% set h2 = hours[hour_index] if hour_index < hours|length else hours[0] %}
  <table class="levels-table">
    <tbody>
      <tr>
        <td><b>Lifted Index (LI)</b></td>
        <td class="num {% if h2.indices.li is not none and h2.indices.li < -4 %}bad{% elif h2.indices.li is not none and h2.indices.li < 0 %}warn{% else %}good{% endif %}">
          {{ '%.1f'|format(h2.indices.li) if h2.indices.li is not none else '—' }}
        </td>
        <td>LI &lt; 0 — неустойчиво, LI &lt; −4 — сильная неустойчивость</td>
      </tr>
      <tr>
        <td><b>K-Index</b></td>
        <td class="num {% if h2.indices.k_index is not none and h2.indices.k_index > 35 %}bad{% elif h2.indices.k_index is not none and h2.indices.k_index > 25 %}warn{% else %}good{% endif %}">
          {{ '%.1f'|format(h2.indices.k_index) if h2.indices.k_index is not none else '—' }}
        </td>
        <td>K &gt; 25 — возможны грозы, K &gt; 35 — сильные грозы</td>
      </tr>
      <tr>
        <td><b>ΔT (850−500)</b></td>
        <td class="num">{{ '%.1f'|format(h2.indices.dt_850_500) if h2.indices.dt_850_500 is not none else '—' }} °C</td>
        <td>Грубый индикатор конвекции</td>
      </tr>
      <tr>
        <td><b>Сдвиг ветра 850→300</b></td>
        <td class="num">
          {% if h2.shear %}{{ '%.1f'|format(h2.shear[0]) }} м/с{% else %}—{% endif %}
        </td>
        <td>{% if h2.shear %}направление {{ '%.0f'|format(h2.shear[1]) }}°{% else %}—{% endif %}</td>
      </tr>
      <tr>
        <td><b>Адвекция (850 гПа)</b></td>
        <td class="num">
          {% if h2.advection == 'warm' %}<span style="color:#ffb547;">тёплая</span>
          {% elif h2.advection == 'cold' %}<span style="color:#4dabff;">холодная</span>
          {% else %}—{% endif %}
        </td>
        <td>Перенос тепла/холода ветром</td>
      </tr>
    </tbody>
  </table>
</div>

{% else %}
  <div class="empty-note">Нет данных для отображения.</div>
{% endif %}

<div id="synoptic-tooltip"></div>

<script>
(function() {
  var tt = document.getElementById('synoptic-tooltip');
  if (!tt) return;

  function buildHtml(el) {
    var lvl     = el.getAttribute('data-level') || '';
    var time    = el.getAttribute('data-time') || '';
    var t       = el.getAttribute('data-t');
    var td      = el.getAttribute('data-td');
    var theta   = el.getAttribute('data-theta');
    var wind    = el.getAttribute('data-wind');
    var wdir    = el.getAttribute('data-winddir');
    var rh      = el.getAttribute('data-rh');
    var mr      = el.getAttribute('data-mr');
    var height  = el.getAttribute('data-height');

    var html = '<div class="tt-title">' + lvl + ' гПа · ' + time + '</div>';
    if (t && t !== '—')         html += '<div class="tt-row"><span>T</span><span style="color:#ff5470;">' + t + ' °C</span></div>';
    if (td && td !== '—')       html += '<div class="tt-row"><span>Td</span><span style="color:#6bb6ff;">' + td + ' °C</span></div>';
    if (theta && theta !== '—') html += '<div class="tt-row"><span>θ</span><span style="color:#4dabff;">' + theta + ' K</span></div>';
    if (height && height !== '—') html += '<div class="tt-row"><span>H</span><span>' + height + ' м</span></div>';
    if (wind && wind !== '—') {
      var windStr = wind + ' м/с';
      if (wdir && wdir !== '—') windStr += ' · ' + wdir + '°';
      html += '<div class="tt-row"><span>Ветер</span><span style="color:#a78bfa;">' + windStr + '</span></div>';
    }
    if (rh && rh !== '—')       html += '<div class="tt-row"><span>RH</span><span>' + rh + ' %</span></div>';
    if (mr && mr !== '—')       html += '<div class="tt-row"><span>mr</span><span>' + mr + ' г/кг</span></div>';
    return html;
  }

  document.addEventListener('mouseover', function(e) {
    var el = e.target;
    if (!el || el.tagName !== 'circle') return;
    var lvl = el.getAttribute('data-level');
    if (!lvl) return;
    tt.innerHTML = buildHtml(el);
    tt.style.display = 'block';
  });

  document.addEventListener('mousemove', function(e) {
    if (tt.style.display !== 'block') return;
    var pad = 14;
    var x = e.clientX + pad;
    var y = e.clientY + pad;
    if (x + tt.offsetWidth > window.innerWidth)  x = e.clientX - tt.offsetWidth - pad;
    if (y + tt.offsetHeight > window.innerHeight) y = e.clientY - tt.offsetHeight - pad;
    tt.style.left = x + 'px';
    tt.style.top  = y + 'px';
  });

  document.addEventListener('mouseout', function(e) {
    if (e.target && e.target.tagName === 'circle') {
      tt.style.display = 'none';
    }
  });

  document.addEventListener('touchstart', function(e) {
    if (e.target && e.target.tagName === 'circle' && e.target.getAttribute('data-level')) {
      tt.innerHTML = buildHtml(e.target);
      tt.style.display = 'block';
      tt.style.left = (e.touches[0].clientX + 14) + 'px';
      tt.style.top  = (e.touches[0].clientY + 14) + 'px';
    } else {
      tt.style.display = 'none';
    }
  }, { passive: true });
})();
</script>

""" + render_biblio_ref("synoptic", "гл. 3–4") + """
""" + COMMON_JS +  render_legend("synoptic") + """
</body>
</html>
"""
