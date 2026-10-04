# -*- coding: utf-8 -*-
"""Карты погоды: интерактивная карта и архив."""

from ui.styles import (
    BASE_STYLE,
    COMMON_JS,
    render_header,
)
MAP_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Карта — weather-msk</title>
<link rel="stylesheet" href="/static/leaflet/leaflet.css" />
<link rel="stylesheet" href="/static/leaflet/Control.Geocoder.css" />
<script src="/static/leaflet/leaflet.js"></script>
<script src="/static/leaflet/Control.Geocoder.js"></script>
""" + BASE_STYLE + """
<style>
  #map { height: 78vh; min-height: 520px; border-radius: 16px;
         border: 1px solid var(--border); overflow: hidden; }
  .map-controls {
    display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0;
    padding: 12px 16px; background: var(--card-bg);
    border: 1px solid var(--border); border-radius: 14px;
    backdrop-filter: blur(14px);
  }
  .map-controls button {
    padding: 8px 14px; border-radius: 10px; font-size: 13px;
    background: var(--bg-1); border: 1px solid var(--border);
    color: var(--text-0); cursor: pointer;
    transition: all 0.2s;
  }
  .map-controls button:hover { border-color: var(--border-hover); }
  .map-controls button.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25), rgba(124,92,255,0.25));
    border-color: var(--accent);
  }
  .leaflet-popup-content {
    font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.7;
  }
  .leaflet-popup-content a {
    color: #2563eb; font-weight: 600; text-decoration: none;
  }
  .leaflet-popup-content a:hover { text-decoration: underline; }
</style>
</head>
<body>

""" + render_header("maps") + """
<h1>🗺 Карта погоды</h1>
<div class="sub">OpenStreetMap · спутник · радар · поиск по населённым пунктам</div>

<div class="map-controls">
  <button id="btn-osm"  class="active" onclick="setLayer('osm')">🗺 Карта</button>
  <button id="btn-sat"                 onclick="setLayer('sat')">🛰 Спутник</button>
  <button id="btn-rain"                onclick="setLayer('rain')">🌧 Радар (RainViewer)</button>
</div>

<div id="map"></div>

<script>
  var map = L.map('map').setView([55.7558, 37.6173], 6);

  var layers = {
    osm: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19
    }),
    sat: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      attribution: '&copy; Esri, Maxar, Earthstar Geographics',
      maxZoom: 19
    })
  };

  var rainLayer = null;
  var currentKey = 'osm';
  layers.osm.addTo(map);

  function setLayer(key) {
    document.querySelectorAll('.map-controls button').forEach(function(b){
      b.classList.remove('active');
    });
    var btnId = (key === 'osm') ? 'btn-osm' : (key === 'sat') ? 'btn-sat' : 'btn-rain';
    var btn = document.getElementById(btnId);
    if (btn) btn.classList.add('active');

    if (currentKey && layers[currentKey]) {
      try { map.removeLayer(layers[currentKey]); } catch(e) {}
    }
    if (rainLayer) { try { map.removeLayer(rainLayer); } catch(e) {} rainLayer = null; }

    if (key === 'rain') {
      fetch('https://api.rainviewer.com/public/weather-maps.json')
        .then(function(r){ return r.json(); })
        .then(function(data){
          var host = data.host;
          var frames = data.radar.past;
          var frame = frames[frames.length - 1];
          rainLayer = L.tileLayer(host + frame.path + '/256/{z}/{x}/{y}/2/1_1.png', {
            attribution: '&copy; RainViewer', opacity: 0.7, maxZoom: 12
          });
          rainLayer.addTo(map);
          currentKey = null;
        })
        .catch(function(e){
          alert('Не удалось загрузить радар: ' + e.message);
          layers.osm.addTo(map);
          currentKey = 'osm';
        });
    } else {
      layers[key].addTo(map);
      currentKey = key;
    }
  }

  // Поиск по населённым пунктам (Nominatim)
  L.Control.geocoder({
    defaultMarkGeocode: false,
    geocoder: L.Control.Geocoder.nominatim({
      geocodingQueryParams: { 'accept-language': 'ru' }
    }),
    placeholder: 'Поиск: город, адрес...'
  }).on('markgeocode', function(e) {
    var latlng = e.geocode.center;
    var name = e.geocode.name;
    map.setView(latlng, 10);

    var popup = '<b>' + name + '</b><br>' +
      latlng.lat.toFixed(4) + ', ' + latlng.lng.toFixed(4) + '<br><br>' +
      '<a href="/forecast/point?lat=' + latlng.lat + '&lon=' + latlng.lng + '&name=' + encodeURIComponent(name) + '&model=gfs">📊 Таблица прогноза</a><br>' +
      '<a href="/point-text?lat=' + latlng.lat + '&lon=' + latlng.lng + '&name=' + encodeURIComponent(name) + '&model=gfs">📝 Текст</a><br>' +
      '<a href="/point-chart?lat=' + latlng.lat + '&lon=' + latlng.lng + '&name=' + encodeURIComponent(name) + '">📈 График</a><br>' +
      '<a href="/point-aviation?lat=' + latlng.lat + '&lon=' + latlng.lng + '&name=' + encodeURIComponent(name) + '&model=gfs">✈️ Авиация</a><br>' +
      '<a href="/point-synoptic?lat=' + latlng.lat + '&lon=' + latlng.lng + '&name=' + encodeURIComponent(name) + '&model=gfs">🌡 Синоптика</a>';

    L.marker(latlng).addTo(map).bindPopup(popup).openPopup();
  }).addTo(map);

  // Клик по точке
  map.on('click', function(e) {
    var lat = e.latlng.lat.toFixed(4);
    var lon = e.latlng.lng.toFixed(4);
    var name = lat + ', ' + lon;
    var popup = '<b>' + name + '</b><br>' +
      '<a href="/forecast/point?lat=' + lat + '&lon=' + lon + '&name=' + encodeURIComponent(name) + '&model=gfs">📊 Таблица прогноза</a><br>' +
      '<a href="/point-text?lat=' + lat + '&lon=' + lon + '&name=' + encodeURIComponent(name) + '&model=gfs">📝 Текст</a><br>' +
      '<a href="/point-chart?lat=' + lat + '&lon=' + lon + '&name=' + encodeURIComponent(name) + '">📈 График моделей</a><br>' +
      '<a href="/point-aviation?lat=' + lat + '&lon=' + lon + '&name=' + encodeURIComponent(name) + '&model=gfs">✈️ Авиация</a><br>' +
      '<a href="/point-synoptic?lat=' + lat + '&lon=' + lon + '&name=' + encodeURIComponent(name) + '&model=gfs">🌡 Синоптика по уровням</a>';
    L.popup().setLatLng(e.latlng).setContent(popup).openOn(map);
  });

  // Маркеры станций из бэкенда
  try {
    var stations = {{ stations_json | safe }};
    if (Array.isArray(stations)) {
      stations.forEach(function(s){
        if (s.lat && s.lon) {
          L.circleMarker([s.lat, s.lon], {
            radius: 5, color: '#4dabff', fillColor: '#4dabff', fillOpacity: 0.8
          }).addTo(map).bindPopup('<b>' + (s.name || '') + '</b><br>' +
            '<a href="/forecast/gfs/' + (s.key || '') + '">📊 Прогноз</a><br>' +
            '<a href="/synoptic/gfs/' + (s.key || '') + '">🌡 Синоптика</a>');
        }
      });
    }
  } catch(e) { console.warn('stations_json:', e); }
</script>

""" + COMMON_JS +  """
</body>
</html>
"""




ARCHIVE_HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Архив прогонов — weather-msk</title>
<link rel="stylesheet" href="/static/leaflet/leaflet.css"/>
<script src="/static/leaflet/leaflet.js"></script>
""" + BASE_STYLE + """
<style>
  .archive-layout {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 16px;
    align-items: start;
  }
  @media (max-width: 900px) {
    .archive-layout { grid-template-columns: 1fr; }
  }

  .runs-list {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
    padding: 12px;
    max-height: 78vh;
    overflow-y: auto;
  }
  .runs-list h3 {
    margin: 12px 0 6px 0;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-2);
    font-weight: 700;
  }
  .runs-list h3:first-child { margin-top: 0; }

  .run-item {
    display: block;
    padding: 10px 12px;
    margin: 4px 0;
    border-radius: 10px;
    background: var(--bg-1);
    border: 1px solid var(--border);
    color: var(--text-1);
    text-decoration: none;
    font-size: 13px;
    transition: all 0.15s;
    cursor: pointer;
  }
  .run-item:hover {
    border-color: var(--border-hover);
    background: var(--bg-2);
    color: var(--text-0);
  }
  .run-item.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25), rgba(124,92,255,0.25));
    border-color: var(--accent);
    color: var(--text-0);
  }
  .run-item .stamp {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 12px;
    display: block;
    margin-bottom: 3px;
  }
  .run-item .meta {
    font-size: 11px;
    color: var(--text-2);
  }
  .run-item.active .meta { color: var(--text-1); }

  #map {
    height: 78vh;
    min-height: 520px;
    border-radius: 16px;
    border: 1px solid var(--border);
    overflow: hidden;
    background: var(--bg-0);
  }

  .toolbar {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
    margin: 12px 0;
    padding: 12px 16px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    backdrop-filter: blur(14px);
  }
  .toolbar label {
    color: var(--text-1);
    font-size: 13px;
    margin-right: 6px;
  }
  .toolbar select {
    padding: 8px 12px;
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text-0);
    font-size: 13px;
    outline: none;
  }
  .toolbar select:focus { border-color: var(--accent); }
  .toolbar button, .toolbar a.btn {
    padding: 8px 16px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    border: none;
    cursor: pointer;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: opacity 0.2s;
  }
  .toolbar button:hover, .toolbar a.btn:hover { opacity: 0.9; }
  .toolbar button:disabled, .toolbar a.btn.disabled {
    opacity: 0.4;
    cursor: not-allowed;
    pointer-events: none;
  }

  .empty-note {
    color: var(--text-2);
    padding: 30px 20px;
    text-align: center;
    font-size: 14px;
  }
  .layer-toggles {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  .layer-toggles label {
    display: flex;
    align-items: center;
    gap: 6px;
    color: var(--text-1);
    font-size: 13px;
    cursor: pointer;
    margin: 0;
  }
</style>
</head>
<body>

""" + render_header("archive") + """
<h1>📂 Архив прогонов</h1>
<div class="sub">Выберите прогон слева — слои загрузятся из архива</div>

<div class="archive-layout">
  <div class="runs-list" id="runs-list">
    <div class="empty-note">Загрузка...</div>
  </div>

  <div>
    <div class="toolbar">
      <div class="layer-toggles">
        <label><input type="checkbox" id="layer-t2m" checked> 🌡 Температура</label>
        <label><input type="checkbox" id="layer-pmsl" checked> 📊 Давление</label>
        <label><input type="checkbox" id="layer-wind" checked> 💨 Ветер</label>
        <label><input type="checkbox" id="layer-prec"> 🌧 Осадки</label>
        <label><input type="checkbox" id="layer-clct"> ☁️ Облачность</label>
      </div>
    </div>

    <div class="toolbar">
      <label>Скачать слой:</label>
      <select id="download-layer">
        <option value="t2m">🌡 Температура</option>
        <option value="pmsl">📊 Давление</option>
        <option value="wind">💨 Ветер</option>
        <option value="prec">🌧 Осадки</option>
        <option value="clct">☁️ Облачность</option>
      </select>
      <a class="btn disabled" id="btn-download-one" href="#" download>💾 Скачать PNG</a>

      <a class="btn disabled" id="btn-download-zip" href="#" download style="margin-left:auto;">📦 Скачать ZIP</a>
    </div>

    <div id="map"></div>
  </div>
</div>

<script>
var map = L.map('map', { zoomControl: true })
             .setView([55.75, 37.62], 6);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors',
  maxZoom: 19,
}).addTo(map);

var BOUNDS = {{ meta.bounds | tojson }};
var overlays = {};
var activeRun = null;

function removeLayer(name) {
  if (overlays[name]) {
    map.removeLayer(overlays[name]);
    delete overlays[name];
  }
}

function addLayer(name, url, opacity) {
  removeLayer(name);
  overlays[name] = L.imageOverlay(url, BOUNDS, {
    opacity: opacity,
  }).addTo(map);
}

function updateLayers() {
  if (!activeRun) return;

  var layers = [
    ['t2m',  document.getElementById('layer-t2m').checked,  0.75],
    ['pmsl', document.getElementById('layer-pmsl').checked, 1.0],
    ['wind', document.getElementById('layer-wind').checked, 0.9],
    ['prec', document.getElementById('layer-prec').checked, 0.75],
    ['clct', document.getElementById('layer-clct').checked, 0.6],
  ];
  layers.forEach(function(item) {
    var name = item[0];
    var enabled = item[1];
    var opacity = item[2];
    if (enabled) {
      addLayer(name, activeRun.baseUrl + activeRun.step3 + '_' + name + '.png', opacity);
    } else {
      removeLayer(name);
    }
  });
}

// ---- Загрузка списка прогонов ----
function loadRuns() {
  fetch('/api/maps-archive')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var container = document.getElementById('runs-list');
      var runs = data.runs || [];

      if (!runs.length) {
        container.innerHTML = '<div class="empty-note">Архив пуст.<br>Нажмите «⚙ Генерировать» на <a href="/maps" style="color:var(--accent)">карте</a>.</div>';
        return;
      }

      // Группируем по модели (icon-eu, gfs, ...)
      var groups = {};
      runs.forEach(function(run) {
        var parts = run.stamp.split('_');
        var model = parts[0] || 'other';
        if (!groups[model]) groups[model] = [];
        groups[model].push(run);
      });

      var modelNames = { 'icon-eu': 'ICON-EU (DWD)', 'gfs': 'GFS (NOAA)' };

      var html = '';
      Object.keys(groups).sort().forEach(function(model) {
        html += '<h3>' + (modelNames[model] || model.toUpperCase()) + '</h3>';
        groups[model].forEach(function(run) {
          var dateStr = run.stamp.split('_')[1] || '';
          var year = dateStr.substr(0, 4);
          var month = dateStr.substr(4, 2);
          var day = dateStr.substr(6, 2);
          var hour = dateStr.substr(8, 2);
          var label = day + '.' + month + '.' + year + ' · ' + hour + ':00 UTC';

          var baseUrl = '/static/maps/archive/' + year + '/' + month + '/' + day + '/'
                      + model + '_' + dateStr + '_';

          var availableSteps = {};
          run.files.forEach(function(f) {
            var m = f.match(/_([0-9]{3})_/);
            if (m) availableSteps[m[1]] = true;
          });
          var steps = Object.keys(availableSteps).sort();
          var step3 = steps.length ? steps[steps.length - 1] : '012';

          html += '<a class="run-item" '
                + 'data-stamp="' + run.stamp + '" '
                + 'data-base="' + baseUrl + '" '
                + 'data-step="' + step3 + '" '
                + 'href="/archive/' + run.stamp + '">'
                + '<span class="stamp">' + label + '</span>'
                + '<span class="meta">' + run.files.length + ' файлов · шаг +' + parseInt(step3) + 'ч</span>'
                + '</a>';
        });
      });
      container.innerHTML = html;

      container.querySelectorAll('.run-item').forEach(function(el) {
        el.addEventListener('click', function(e) {
          e.preventDefault();
          selectRun(el);
          history.replaceState(null, '', '/archive/' + el.dataset.stamp);
        });
      });

      // Автовыбор: первый прогон или тот, что в URL
      var pathMatch = location.pathname.match(new RegExp('^/archive/(.+)$'));
      if (pathMatch) {
        var target = container.querySelector('[data-stamp="' + pathMatch[1] + '"]');
        if (target) {
          selectRun(target);
          return;
        }
      }
      var first = container.querySelector('.run-item');
      if (first) selectRun(first);
    })
    .catch(function(err) {
      document.getElementById('runs-list').innerHTML =
        '<div class="empty-note">Ошибка загрузки: ' + err.message + '</div>';
    });
}

function selectRun(el) {
  document.querySelectorAll('.run-item').forEach(function(x) {
    x.classList.remove('active');
  });
  el.classList.add('active');

  activeRun = {
    stamp: el.dataset.stamp,
    baseUrl: el.dataset.base,
    step3: el.dataset.step,
  };

  // Обновляем кнопки скачивания
  var dlOne = document.getElementById('btn-download-one');
  var dlZip = document.getElementById('btn-download-zip');
  dlOne.classList.remove('disabled');
  dlZip.classList.remove('disabled');
  dlZip.href = '/api/maps-archive-zip/' + activeRun.stamp;

  updateDownloadOne();
  updateLayers();
}

function updateDownloadOne() {
  if (!activeRun) return;
  var layer = document.getElementById('download-layer').value;
  var url = activeRun.baseUrl + activeRun.step3 + '_' + layer + '.png';
  var dlOne = document.getElementById('btn-download-one');
  dlOne.href = url;
  dlOne.download = activeRun.stamp + '_' + activeRun.step3 + '_' + layer + '.png';
}

['layer-t2m','layer-pmsl','layer-wind','layer-prec','layer-clct'].forEach(function(id) {
  document.getElementById(id).addEventListener('change', updateLayers);
});
document.getElementById('download-layer').addEventListener('change', updateDownloadOne);

loadRuns();
</script>

""" + COMMON_JS + """
</body>
</html>
"""




MAPS_HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Карта погоды — weather-msk</title>
<link rel="stylesheet" href="/static/leaflet/leaflet.css"/>
<link rel="stylesheet" href="/static/leaflet/Control.Geocoder.css"/>
<script src="/static/leaflet/leaflet.js"></script>
<script src="/static/leaflet/Control.Geocoder.js"></script>
""" + BASE_STYLE + """
<style>
  #map {
    height: 78vh;
    min-height: 520px;
    border-radius: 16px;
    border: 1px solid var(--border);
    overflow: hidden;
    background: var(--bg-0);
  }
.maps-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 16px;
  align-items: start;
}
@media (max-width: 1100px) {
  .maps-layout { grid-template-columns: 1fr; }
}

.panel {
  position: sticky;
  top: 20px;
  width: 100%;
  padding: 16px 18px;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  backdrop-filter: blur(14px);
  box-shadow: var(--card-shadow);
  font-size: 13px;
  max-height: calc(78vh);
  overflow-y: auto;
}
  .panel h3 {
    margin: 12px 0 6px 0;
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
    padding: 4px 0;
    color: var(--text-1);
    cursor: pointer;
    font-size: 13px;
  }
  .panel label input { cursor: pointer; }
  .panel select {
    width: 100%;
    padding: 8px 10px;
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-0);
    font-size: 13px;
    outline: none;
  }
  .panel select:focus { border-color: var(--accent); }
  .panel .btn-row {
    display: flex;
    gap: 8px;
    margin-top: 14px;
  }
  .panel button {
    flex: 1;
    padding: 10px 14px;
    border-radius: 10px;
    border: none;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    transition: opacity 0.2s;
  }
  .panel button:hover { opacity: 0.9; }
  .panel button.secondary {
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
    line-height: 1.4;
  }
  .map-controls {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 12px 0;
    padding: 12px 16px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    backdrop-filter: blur(14px);
  }
  .map-controls button {
    padding: 8px 14px;
    border-radius: 10px;
    font-size: 13px;
    background: var(--bg-1);
    border: 1px solid var(--border);
    color: var(--text-0);
    cursor: pointer;
    transition: all 0.2s;
  }
  .map-controls button:hover { border-color: var(--border-hover); }
  .map-controls button.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25), rgba(124,92,255,0.25));
    border-color: var(--accent);
  }
  .leaflet-popup-content {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    line-height: 1.7;
  }
  .leaflet-popup-content a {
    color: #2563eb;
    font-weight: 600;
    text-decoration: none;
  }
  .leaflet-popup-content a:hover { text-decoration: underline; }
</style>
</head>
<body>

""" + render_header("maps") + """
<h1>🗺 Карта погоды</h1>
<div class="sub">OSM · спутник · интерактивные слои ICON-EU / GFS · поиск региона</div>

<div class="map-controls">
  <button id="btn-osm" class="active" onclick="setBase('osm')">🗺 Карта</button>
  <button id="btn-sat" onclick="setBase('sat')">🛰 Спутник</button>
</div>

<div class="maps-layout">
  <div class="map-wrapper" style="position: relative;">
    <div id="map"></div>
    <div id="map-timestamp" style="
      position: absolute;
      bottom: 16px;
      right: 16px;
      z-index: 1000;
      padding: 6px 12px;
      background: rgba(15, 21, 36, 0.85);
      border: 1px solid var(--border);
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: var(--text-0);
      backdrop-filter: blur(10px);
      pointer-events: none;
      display: none;
    "></div>
  </div>

    <div class="panel">
    <h3>Поиск региона</h3>
    <input type="text" id="search-box"
           placeholder="Москва, Тверь, Казань..."
           style="width:100%;padding:8px 10px;background:var(--bg-1);
                  border:1px solid var(--border);border-radius:8px;
                  color:var(--text-0);font-size:13px;outline:none;">
    <ul id="search-results"
        style="list-style:none;padding:0;margin:6px 0 0 0;
               max-height:140px;overflow-y:auto;font-size:12px;"></ul>

    <a class="back" href="/archive"
       style="display:block;width:100%;text-align:center;margin:12px 0 0 0;">
      📂 Все прогоны → архив
    </a>

    <h3>Модель</h3>
    <select id="model-select">
      <option value="icon-eu">ICON-EU (DWD)</option>
      <option value="gfs">GFS (NOAA)</option>
    </select>

    <h3>Шаг прогноза</h3>
    <select id="step-select">
      <option value="6">+6 ч</option>
      <option value="12" selected>+12 ч</option>
      <option value="18">+18 ч</option>
      <option value="24">+24 ч</option>
    </select>

    <h3>Слои</h3>
    <label><input type="checkbox" id="layer-t2m" checked> 🌡 Температура 2м</label>
    <label><input type="checkbox" id="layer-pmsl" checked> 📊 Давление (Pmsl)</label>
    <label><input type="checkbox" id="layer-wind" checked> 💨 Ветер 10м</label>
    <label><input type="checkbox" id="layer-prec"> 🌧 Осадки</label>
    <label><input type="checkbox" id="layer-clct"> ☁️ Облачность</label>

    <div class="btn-row">
      <button onclick="updateMaps()">Обновить</button>
      <button class="secondary" onclick="generateMaps()">⚙ Генерировать</button>
    </div>
    <div id="status"></div>
  </div>
</div>          <!-- ← закрываем .maps-layout -->


<script>
// ============================================================
// ИНИЦИАЛИЗАЦИЯ КАРТЫ
// ============================================================
var map = L.map('map', { zoomControl: true })
             .setView([55.75, 37.62], 6);

var baseLayers = {
  osm: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19,
  }),
  sat: L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/'
    + 'World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: '&copy; Esri, Maxar, Earthstar Geographics',
    maxZoom: 19,
  }),
};
var currentBase = 'osm';
baseLayers.osm.addTo(map);

function setBase(key) {
  if (currentBase && baseLayers[currentBase]) {
    map.removeLayer(baseLayers[currentBase]);
  }
  baseLayers[key].addTo(map);
  currentBase = key;
  document.querySelectorAll('.map-controls button').forEach(function(b) {
    b.classList.remove('active');
  });
  var btn = document.getElementById(key === 'osm' ? 'btn-osm' : 'btn-sat');
  if (btn) btn.classList.add('active');
}

// ============================================================
// СЛОИ КАРТ
// ============================================================
var BOUNDS = {{ meta.bounds | tojson }};
var overlays = {};
var activeStamp = null;

function addLayer(name, url, opacity) {
  if (overlays[name]) {
    map.removeLayer(overlays[name]);
  }
  overlays[name] = L.imageOverlay(url, BOUNDS, {
    opacity: opacity || 0.7,
  }).addTo(map);
}

function removeLayer(name) {
  if (overlays[name]) {
    map.removeLayer(overlays[name]);
    delete overlays[name];
  }
}

function toggleLayer(name, url, checked, opacity) {
  if (checked) addLayer(name, url, opacity);
  else removeLayer(name);
}

// ============================================================
// ПОИСК АКТУАЛЬНОГО STAMP
// ============================================================
function findStamp(model, step, callback) {
  fetch('/api/maps-list')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (!data.files || data.files.length === 0) {
        callback(null);
        return;
      }
      var stepStr = String(step).padStart(3, '0');
            var re = new RegExp('^' + model + '_([0-9]{10})_' + stepStr + '_');
      var match = data.files.find(function(f) { return re.test(f); });
      callback(match ? match.match(re)[1] : null);
    })
    .catch(function() { callback(null); });
}

// ============================================================
// ОБНОВЛЕНИЕ СЛОЁВ
// ============================================================
function updateMaps() {
  var model = document.getElementById('model-select').value;
  var step = document.getElementById('step-select').value;
  var status = document.getElementById('status');

  status.textContent = 'Поиск данных...';

  findStamp(model, step, function(stamp) {
    var tsEl = document.getElementById('map-timestamp');

    if (!stamp) {
      status.textContent = 'Нет данных для ' + model + ' +' + step + 'ч. Нажмите «Генерировать» или выберите архив.';
      ['t2m', 'pmsl', 'wind', 'prec', 'clct'].forEach(removeLayer);
      if (tsEl) tsEl.style.display = 'none';
      return;
    }
    activeStamp = stamp;
    var prefix = '/static/maps/' + model + '_' + stamp + '_'
                 + String(step).padStart(3, '0') + '_';

    toggleLayer('t2m', prefix + 't2m.png',
                document.getElementById('layer-t2m').checked, 0.7);
    toggleLayer('pmsl', prefix + 'pmsl.png',
                document.getElementById('layer-pmsl').checked, 1.0);
    toggleLayer('wind', prefix + 'wind.png',
                document.getElementById('layer-wind').checked, 0.9);
    toggleLayer('prec', prefix + 'prec.png',
                document.getElementById('layer-prec').checked, 0.7);
    toggleLayer('clct', prefix + 'clct.png',
                document.getElementById('layer-clct').checked, 0.6);

    var dt = stamp.slice(0, 8) + ' ' + stamp.slice(8, 10) + ':00 UTC';
    status.textContent = '✓ ' + model + ' · ' + step + 'ч · ' + dt;

    // Таймкод карты
    if (tsEl) {
      tsEl.textContent = '🕒 ' + model.toUpperCase() + ' · +' + step + 'ч · ' + dt;
      tsEl.style.display = 'block';
    }
  });
}

// ============================================================
// РУЧНАЯ ГЕНЕРАЦИЯ
// ============================================================
function generateMaps() {
  var model = document.getElementById('model-select').value;
  var step = parseInt(document.getElementById('step-select').value, 10);
  var fields = [];
  if (document.getElementById('layer-t2m').checked)  fields.push('t_2m');
  if (document.getElementById('layer-pmsl').checked) fields.push('pmsl');
  if (document.getElementById('layer-wind').checked) {
    fields.push('u_10m', 'v_10m');
  }
  if (document.getElementById('layer-prec').checked) fields.push('tot_prec');
  if (document.getElementById('layer-clct').checked) fields.push('clct');

  if (!fields.length) {
    alert('Выберите хотя бы один слой');
    return;
  }

  var status = document.getElementById('status');
  status.textContent = '⏳ Генерация... (может занять минуты)';

  fetch('/api/update-maps', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      models: [model],
      steps: [step],
      fields: fields,
    }),
  })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.status === 'ok') {
        status.textContent = '✓ Готово: ' + data.files.length + ' файлов';
        updateMaps();
      } else {
        status.textContent = '✗ Ошибка: ' + (data.message || '?');
      }
    })
    .catch(function(e) {
      status.textContent = '✗ Ошибка: ' + e.message;
    });
}

// ============================================================
// ПОИСК РЕГИОНА (Open-Meteo Geocoding)
// ============================================================
var searchBox = document.getElementById('search-box');
var resultsList = document.getElementById('search-results');
var searchTimer = null;

searchBox.addEventListener('input', function() {
  clearTimeout(searchTimer);
  var q = this.value.trim();
  if (q.length < 3) { resultsList.innerHTML = ''; return; }
  searchTimer = setTimeout(function() {
    fetch('/api/geocode?q=' + encodeURIComponent(q))
      .then(function(r) { return r.json(); })
      .then(function(data) {
        resultsList.innerHTML = '';
        (data.results || []).slice(0, 6).forEach(function(item) {
          var li = document.createElement('li');
          li.textContent = item.name +
            (item.admin1 ? ', ' + item.admin1 : '') +
            (item.country ? ', ' + item.country : '');
          li.style.cssText =
            'padding:6px 8px;cursor:pointer;border-radius:6px;' +
            'color:var(--text-1);';
          li.onmouseover = function() {
            li.style.background = 'rgba(77,171,255,0.12)';
          };
          li.onmouseout = function() {
            li.style.background = 'transparent';
          };
          li.onclick = function() {
            map.setView([item.latitude, item.longitude], 7);
            resultsList.innerHTML = '';
            searchBox.value = item.name;
          };
          resultsList.appendChild(li);
        });
      });
  }, 350);
});

// ============================================================
// КЛИК ПО КАРТЕ — ссылки на прогноз в точке
// ============================================================
map.on('click', function(e) {
  var lat = e.latlng.lat.toFixed(4);
  var lon = e.latlng.lng.toFixed(4);
  var name = lat + ', ' + lon;
  var enc = encodeURIComponent(name);
  var popup = '<b>' + name + '</b><br>'
    + '<a href="/forecast/point?lat=' + lat + '&lon=' + lon
    + '&name=' + enc + '&model=gfs">📊 Таблица прогноза</a><br>'
    + '<a href="/point-text?lat=' + lat + '&lon=' + lon
    + '&name=' + enc + '&model=gfs">📝 Текст</a><br>'
    + '<a href="/point-chart?lat=' + lat + '&lon=' + lon
    + '&name=' + enc + '">📈 График моделей</a><br>'
    + '<a href="/point-aviation?lat=' + lat + '&lon=' + lon
    + '&name=' + enc + '&model=gfs">✈️ Авиация</a><br>'
    + '<a href="/point-synoptic?lat=' + lat + '&lon=' + lon
    + '&name=' + enc + '&model=gfs">🌡 Синоптика</a>';
  L.popup().setLatLng(e.latlng).setContent(popup).openOn(map);
});

// ============================================================
// АВТОЗАГРУЗКА
// ============================================================
document.getElementById('model-select').addEventListener('change', updateMaps);
document.getElementById('step-select').addEventListener('change', updateMaps);
['t2m', 'pmsl', 'wind', 'prec', 'clct'].forEach(function(key) {
  document.getElementById('layer-' + key)
    .addEventListener('change', updateMaps);
});

// Автозагрузка при открытии
updateMaps();
</script>

""" + COMMON_JS + """
</body>
</html>
"""
