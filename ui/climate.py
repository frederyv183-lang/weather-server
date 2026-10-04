# -*- coding: utf-8 -*-
"""Климатические индексы (ENSO/SSW/PV)."""

from ui.styles import (
    BASE_STYLE,
    COMMON_JS,
    render_header,
    render_legend,
    render_biblio_ref,
)
CLIMATE_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Климатические индексы — ENSO / SSW / PV</title>
""" + BASE_STYLE + """
<style>
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
  .kpi-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px; margin: 16px 0 20px 0;
  }
  .kpi {
    padding: 14px 18px; border-radius: 14px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
  }
  .kpi .lbl {
    color: var(--text-2); font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .kpi .val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px; font-weight: 700; margin-top: 6px;
  }
  .kpi .val.good { color: #00e5a0; }
  .kpi .val.warn { color: #ffb547; }
  .kpi .val.bad  { color: #ff5470; }
  .kpi .sub {
    color: var(--text-2); font-size: 11px; margin-top: 4px;
  }
  .summary-box {
    margin: 12px 0 20px 0; padding: 14px 18px;
    background: rgba(15,21,36,0.5);
    border: 1px solid var(--border); border-radius: 12px;
    font-size: 14px; line-height: 1.6; color: var(--text-1);
  }
  .chart-block {
    margin: 16px 0; padding: 12px;
    background: rgba(15,21,36,0.4);
    border: 1px solid var(--border); border-radius: 12px;
  }
  .chart-block svg { display: block; }
  .events-list {
    margin-top: 12px; padding: 0; list-style: none;
  }
  .events-list li {
    padding: 8px 12px; margin-bottom: 6px;
    background: rgba(15,21,36,0.4);
    border-left: 3px solid #ff5470;
    border-radius: 6px;
    font-size: 13px; color: var(--text-1);
    font-family: 'JetBrains Mono', monospace;
  }
  .events-list li .date { color: #ffb547; font-weight: 700; }
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
  .empty-note { color: var(--text-2); padding: 20px; font-size: 14px; }
</style>
</head>
<body>

""" + render_header("theory") + """
<h1>🌍 Климатические индексы</h1>
<div class="sub">ENSO · SSW · Полярный вихрь · период: {{ period.start }} — {{ period.end }}</div>

{% if error %}
  <div class="error-box">⚠️ {{ error }}</div>
{% endif %}

<div class="controls">
  <label>Период:</label>
  <a href="/climate?days=90"  class="{% if days_back == 90  %}active{% endif %}">3 мес.</a>
  <a href="/climate?days=180" class="{% if days_back == 180 %}active{% endif %}">6 мес.</a>
  <a href="/climate?days=365" class="{% if days_back == 365 %}active{% endif %}">1 год</a>
  <a href="/climate?days=730" class="{% if days_back == 730 %}active{% endif %}">2 года</a>
</div>

{% if enso and not enso.error %}
<div class="section">
  <h2>🌊 ENSO — Эль-Ниньо / Ла-Нинья (Niño 3.4)</h2>
  <div class="kpi-grid">
    <div class="kpi">
      <div class="lbl">ONI, °C</div>
      <div class="val {% if enso.current_oni is not none and enso.current_oni >= 0.5 %}bad{% elif enso.current_oni is not none and enso.current_oni <= -0.5 %}warn{% else %}good{% endif %}">
        {{ '%+.2f'|format(enso.current_oni) if enso.current_oni is not none else '—' }}
      </div>
      <div class="sub">3-мес. скользящее</div>
    </div>
    <div class="kpi">
      <div class="lbl">Фаза</div>
      <div class="val" style="font-size:16px;">{{ enso.classification }}</div>
      <div class="sub">по порогам ±0.5 °C</div>
    </div>
  </div>
  <div class="summary-box">{{ enso.summary_text }}</div>
  <div class="chart-block">{{ enso.svg | safe }}</div>
</div>
{% elif enso and enso.error %}
  <div class="section">
    <h2>🌊 ENSO</h2>
    <div class="error-box">⚠️ {{ enso.error }}</div>
  </div>
{% endif %}

{% if ssw and not ssw.error %}
<div class="section">
  <h2>💥 SSW — Внезапные стратосферные потепления</h2>
  <div class="kpi-grid">
    <div class="kpi">
      <div class="lbl">Событий SSW</div>
      <div class="val {% if ssw.n_events == 0 %}good{% elif ssw.n_events < 3 %}warn{% else %}bad{% endif %}">
        {{ ssw.n_events }}
      </div>
      <div class="sub">за выбранный период</div>
    </div>
    <div class="kpi">
      <div class="lbl">Порог SSW</div>
      <div class="val" style="font-size:14px;">+25 °C</div>
      <div class="sub">за 7 суток на 10 гПа</div>
    </div>
  </div>
  <div class="summary-box">{{ ssw.summary_text }}</div>
  <div class="chart-block">{{ ssw.svg | safe }}</div>
  {% if ssw.events %}
    <h3 style="margin-top:16px;font-size:15px;color:var(--text-0);">Последние события</h3>
    <ul class="events-list">
      {% for ev in ssw.events %}
        <li><span class="date">{{ ev.date }}</span> — {{ ev.description }}</li>
      {% endfor %}
    </ul>
  {% endif %}
</div>
{% elif ssw and ssw.error %}
  <div class="section">
    <h2>💥 SSW</h2>
    <div class="error-box">⚠️ {{ ssw.error }}</div>
  </div>
{% endif %}

{% if pv and not pv.error %}
<div class="section">
  <h2>🌀 Полярный вихрь (10 гПа, 60°N)</h2>
  <div class="kpi-grid">
    <div class="kpi">
      <div class="lbl">Геопотенциал 10 гПа</div>
      <div class="val">
        {{ '%.0f'|format(pv.gph_mean) if pv.gph_mean is not none else '—' }} м
      </div>
      <div class="sub">средний за период</div>
    </div>
    <div class="kpi">
      <div class="lbl">Состояние PV</div>
      <div class="val" style="font-size:16px;">{{ pv.classification }}</div>
      <div class="sub">по порогам ERA5</div>
    </div>
  </div>
  <div class="summary-box">{{ pv.summary_text }}</div>
  <div class="chart-block">{{ pv.svg | safe }}</div>
</div>
{% elif pv and pv.error %}
  <div class="section">
    <h2>🌀 Полярный вихрь</h2>
    <div class="error-box">⚠️ {{ pv.error }}</div>
  </div>
{% endif %}

<div class="methodology">
  <h2>📚 Методика</h2>
  <p>
    <b>ENSO (El Niño — Southern Oscillation).</b>
    SST в области Niño 3.4 (5°N–5°S, 120°W–170°W).
    Аномалия относительно климата 1991–2020, 3-месячное скользящее — ONI.
    Пороги: <code>ONI ≥ +0.5</code> — Эль-Ниньо,
    <code>ONI ≤ −0.5</code> — Ла-Нинья,
    <code>|ONI| ≥ 1.5</code> — сильное событие.
  </p>
  <p>
    <b>SSW (Sudden Stratospheric Warming).</b>
    Резкое повышение T в стратосфере на 10 гПа (≈30 км) над Арктикой
    на +25 °C и более за неделю.
  </p>
  <p>
    <b>PV (Polar Vortex).</b>
    Геопотенциал 10 гПа в точке 60°N, 0°. Пороги (ERA5):
    <code>&lt; 29000 м</code> — очень сильный,
    <code>29000–30000</code> — сильный,
    <code>30000–30500</code> — норма,
    <code>30500–31000</code> — ослабленный,
    <code>&gt; 31000</code> — разрушенный.
  </p>
  <p><b>Источник:</b> Open-Meteo Archive API (ERA5 reanalysis).</p>
</div>

""" + render_biblio_ref("climate") + """
""" + COMMON_JS +  render_legend("climate") + """
</body>
</html>
"""
