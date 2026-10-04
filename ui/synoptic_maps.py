# -*- coding: utf-8 -*-
"""Страница синоптических карт АТ."""

from ui.styles import BASE_STYLE, COMMON_JS, render_header


SYNOPTIC_MAPS_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Синоптические карты — weather-msk</title>
<link rel="stylesheet" href="/static/leaflet/leaflet.css"/>
<script src="/static/leaflet/leaflet.js"></script>
""" + BASE_STYLE + """
<style>
  .synoptic-layout {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 16px;
    align-items: start;
  }
  @media (max-width: 1100px) {
    .synoptic-layout { grid-template-columns: 1fr; }
  }
  #at-map {
    height: 80vh;
    min-height: 600px;
    border-radius: 16px;
    border: 1px solid var(--border);
    background: #0a0e1a;
  }
  .panel {
    padding: 16px 18px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
  }
  .panel h3 {
    margin: 14px 0 8px 0;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-2);
    font-weight: 700;
  }
  .panel h3:first-child { margin-top: 0; }
  .panel label {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 5px 0;
    color: var(--text-1);
    font-size: 13px;
    cursor: pointer;
  }
  .panel select {
    width: 100%;
    padding: 8px 10px;
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-0);
    font-size: 13px;
  }
  .panel select:focus { border-color: var(--accent); }
  .level-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
  }
  .level-btn {
    padding: 8px 6px;
    text-align: center;
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-1);
    font-size: 12px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .level-btn:hover { border-color: var(--border-hover); }
  .level-btn.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25),
                                       rgba(124,92,255,0.25));
    border-color: var(--accent);
    color: var(--text-0);
    font-weight: 600;
  }
  .btn-row {
    display: flex;
    gap: 8px;
    margin-top: 16px;
  }
  .btn-row button {
    flex: 1;
    padding: 10px 14px;
    border-radius: 10px;
    border: none;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
  }
  .btn-row button.secondary {
    background: var(--bg-1);
    color: var(--text-0);
    border: 1px solid var(--border);
  }
  #status {
    margin-top: 10px;
    font-size: 11px;
    color: var(--text-2);
    font-family: 'JetBrains Mono', monospace;
    min-height: 16px;
  }
</style>
</head>
<body>

""" + render_header("synoptic_maps") + """
<h1>🌐 Синоптические карты</h1>
<div class="sub">Абсолютная топография (АТ) на разных уровнях · GFS · глобально</div>

<div class="synoptic-layout">
  <div class="panel">
    <h3>Модель</h3>
    <select id="model-select">
      {% for key, m in models.items() %}
        <option value="{{ key }}">{{ m.name }}</option>
      {% endfor %}
    </select>

    <h3>Уровень АТ</h3>
    <div class="level-grid" id="level-grid">
      {% for level, info in levels.items() %}
        <div class="level-btn {% if level == 500 %}active{% endif %}"
             data-level="{{ level }}">{{ info.name }}</div>
      {% endfor %}
    </div>

    <h3>Регион</h3>
    <select id="region-select">
      {% for key, r in regions.items() %}
        <option value="{{ key }}" {% if key == 'nh' %}selected{% endif %}>
          {{ r.name }}
        </option>
      {% endfor %}
    </select>

    <h3>Срок прогноза</h3>
    <select id="step-select">
      {% for step in steps %}
        <option value="{{ step }}">+{{ step }} ч</option>
      {% endfor %}
    </select>

    <h3>Доп. слои (скоро)</h3>
    {% for key, ov in overlays.items() %}
      <label>
        <input type="checkbox" class="overlay-check" data-key="{{ key }}" disabled>
        {{ ov.name }}
      </label>
    {% endfor %}

    <div class="btn-row">
      <button onclick="updateMap()">Обновить</button>
      <button class="secondary" onclick="generateMaps()">⚙ Сгенерировать</button>
    </div>
    <div id="status">Готов к работе</div>
  </div>

  <div id="at-map"></div>
</div>

<script>
var map = L.map('at-map', { zoomControl: true })
            .setView([50, 20], 3);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors',
  maxZoom: 10,
}).addTo(map);

var REGION_BOUNDS = {
  {% for key, r in regions.items() %}
    "{{ key }}": [ {{ r.bbox[2] }}, {{ r.bbox[0] }},
                   {{ r.bbox[3] }}, {{ r.bbox[1] }} ],
  {% endfor %}
};

var currentLevel = 500;

document.querySelectorAll('.level-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.level-btn').forEach(
      function(b) { b.classList.remove('active'); }
    );
    btn.classList.add('active');
    currentLevel = parseInt(btn.dataset.level);
    updateMap();
  });
});

function updateMap() {
  var model = document.getElementById('model-select').value;
  var region = document.getElementById('region-select').value;
  var step = document.getElementById('step-select').value;
  var status = document.getElementById('status');
  status.textContent = 'Поиск данных...';

  fetch('/api/synoptic-maps/list')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var files = data.files || [];
      var step3 = String(step).padStart(3, '0');
      var re = new RegExp(
        model + '_\\d{10}_' + step3
        + '_at' + currentLevel + '_' + region + '\\.png$'
      );
      var match = files.find(function(f) { return re.test(f); });

      if (!match) {
        status.textContent =
          'Нет данных. Нажмите «Сгенерировать».';
        if (window.atLayer) {
          map.removeLayer(window.atLayer);
          window.atLayer = null;
        }
        return;
      }

      var url = '/static/synoptic_maps/archive/' + match;
      var bbox = REGION_BOUNDS[region];

      if (window.atLayer) map.removeLayer(window.atLayer);
      window.atLayer = L.imageOverlay(
        url,
        [[bbox[0], bbox[1]], [bbox[2], bbox[3]]],
        { opacity: 0.85 }
      ).addTo(map);

      map.fitBounds([[bbox[0], bbox[1]], [bbox[2], bbox[3]]]);
      status.textContent = '✓ ' + match.split('/').pop();
    })
    .catch(function(e) { status.textContent = '✗ ' + e.message; });
}

function generateMaps() {
  var model = document.getElementById('model-select').value;
  var region = document.getElementById('region-select').value;
  var step = parseInt(document.getElementById('step-select').value);
  var status = document.getElementById('status');
  status.textContent = '⏳ Генерация... (1–3 минуты)';

  fetch('/api/synoptic-maps/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      levels: [currentLevel],
      steps: [step],
      regions: [region],
    }),
  })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.status === 'ok') {
        status.textContent = '✓ Готово: ' + data.files.length + ' файлов';
        setTimeout(updateMap, 1000);
      } else {
        status.textContent = '✗ ' + (data.message || '?');
      }
    })
    .catch(function(e) { status.textContent = '✗ ' + e.message; });
}

updateMap();
</script>

""" + COMMON_JS + """
</body>
</html>
"""
