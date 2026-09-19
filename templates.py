# -*- coding: utf-8 -*-
"""
Шаблоны и стили для server.py.
Только константы и функции рендера, без маршрутов.
"""

from core.dictionaries import CODE_TO_TEXT, WEATHER_ICONS
from core.config import DEFAULT_LOCATION


BASE_STYLE = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root, [data-theme="dark"] {
    --bg-0: #0a0e1a; --bg-1: #0f1524; --bg-2: #161d2f;
    --border: rgba(120, 160, 255, 0.15);
    --border-hover: rgba(120, 200, 255, 0.4);
    --text-0: #e8eefc; --text-1: #a8b4d0; --text-2: #6b7694;
    --accent: #4dabff;
    --card-shadow: 0 20px 40px -20px rgba(77, 171, 255, 0.4);
    --card-bg: rgba(22, 29, 47, 0.85);
    --card-bg-2: rgba(15, 21, 36, 0.85);
  }
  [data-theme="light"] {
    --bg-0: #f5f7fb; --bg-1: #ffffff; --bg-2: #eef2f9;
    --border: rgba(30, 60, 120, 0.12);
    --border-hover: rgba(30, 100, 200, 0.4);
    --text-0: #131a2b; --text-1: #4a5570; --text-2: #8892b0;
    --accent: #2563eb;
    --card-shadow: 0 12px 30px -12px rgba(37, 99, 235, 0.25);
    --card-bg: rgba(255, 255, 255, 0.85);
    --card-bg-2: rgba(238, 242, 249, 0.85);
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    color: var(--text-0);
    font-family: 'Inter', -apple-system, sans-serif;
    font-size: 14px; line-height: 1.5; min-height: 100vh;
    transition: color 0.3s;
    position: relative;
    overflow-x: hidden;
  }
  body { padding: 20px; max-width: 1200px; margin: 0 auto; }

  body::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: -2;
    background: var(--bg-0);
    transition: background 1.5s ease-in-out;
  }
  body[data-tod="dawn"]::before {
    background: linear-gradient(180deg,
      #1a1533 0%, #4a2954 35%, #b85c4a 75%, #e8a06a 100%);
  }
  body[data-tod="day"]::before {
    background: linear-gradient(180deg,
      #0a1e3d 0%, #1a3a6b 40%, #2d5a9e 100%);
  }
  body[data-tod="dusk"]::before {
    background: linear-gradient(180deg,
      #1a1533 0%, #4a2954 30%, #a8474a 65%, #e07a4a 100%);
  }
  body[data-tod="night"]::before {
    background: linear-gradient(180deg,
      #050810 0%, #0a1228 50%, #111c3a 100%);
  }
  [data-theme="light"] body[data-tod="dawn"]::before {
    background: linear-gradient(180deg, #ffd7c4 0%, #ffb59a 50%, #ff9e7a 100%);
  }
  [data-theme="light"] body[data-tod="day"]::before {
    background: linear-gradient(180deg, #c8e3ff 0%, #a3d0ff 60%, #7cbaff 100%);
  }
  [data-theme="light"] body[data-tod="dusk"]::before {
    background: linear-gradient(180deg, #ffc4a0 0%, #ff8f7a 50%, #e56a7a 100%);
  }
  [data-theme="light"] body[data-tod="night"]::before {
    background: linear-gradient(180deg, #2a3a6b 0%, #1a2545 60%, #0f1832 100%);
  }

  h1 {
    font-size: 26px; font-weight: 700; margin: 0 0 6px 0;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: -0.5px;
  }
  .sub { color: var(--text-2); font-size: 13px; margin-bottom: 20px; }
  a.back {
    display: inline-flex; align-items: center; gap: 6px;
    margin-bottom: 14px; color: var(--accent); text-decoration: none;
    font-size: 13px; font-weight: 500; padding: 6px 12px; border-radius: 8px;
    background: rgba(77, 171, 255, 0.08);
    border: 1px solid rgba(77, 171, 255, 0.2); transition: all 0.2s ease;
    backdrop-filter: blur(10px);
  }
  a.back:hover {
    background: rgba(77, 171, 255, 0.15);
    border-color: var(--border-hover); transform: translateX(-2px);
  }
  a.card {
    display: block; padding: 22px 24px; margin: 12px 0;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    text-decoration: none; color: var(--text-0);
    font-size: 16px; font-weight: 500; position: relative;
    overflow: hidden; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  a.card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0; transition: opacity 0.3s;
  }
  a.card:hover {
    transform: translateY(-3px); border-color: var(--border-hover);
    box-shadow: var(--card-shadow);
  }
  a.card:hover::before { opacity: 1; }
  .icon { font-size: 22px; margin-right: 12px; }
  .desc { color: var(--text-2); font-size: 12px; margin-top: 6px; }
  .coords { color: var(--text-2); font-size: 12px; margin-top: 4px;
            font-family: 'JetBrains Mono', monospace; }
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .fade-in { animation: fadeInUp 0.4s ease-out backwards; }

  .synoptic-badge {
    display: inline-block; padding: 4px 10px; border-radius: 6px;
    font-size: 11px; font-weight: 600; margin: 2px 4px 2px 0;
    font-family: 'Inter', sans-serif; backdrop-filter: blur(6px);
  }
  .synoptic-cold_front   { background: rgba(77,171,255,0.15); color: #4dabff; border: 1px solid rgba(77,171,255,0.3); }
  .synoptic-warm_front   { background: rgba(255,181,71,0.15); color: #ffb547; border: 1px solid rgba(255,181,71,0.3); }
  .synoptic-cyclone      { background: rgba(124,92,255,0.15); color: #a78bfa; border: 1px solid rgba(124,92,255,0.3); }
  .synoptic-anticyclone  { background: rgba(0,229,160,0.15); color: #00e5a0; border: 1px solid rgba(0,229,160,0.3); }
  .synoptic-fold         { background: rgba(255,84,112,0.15); color: #ff5470; border: 1px solid rgba(255,84,112,0.3); }

  .top-controls {
    position: fixed; top: 16px; left: 16px; z-index: 9999;
    display: flex; gap: 8px;
  }
  .top-controls > button {
    background: var(--card-bg); border: 1px solid var(--border);
    color: var(--text-0); width: 38px; height: 38px; border-radius: 10px;
    cursor: pointer; font-size: 16px; display: inline-flex;
    align-items: center; justify-content: center;
    transition: all 0.2s; backdrop-filter: blur(10px);
  }
  .top-controls > button:hover {
    border-color: var(--border-hover); box-shadow: var(--card-shadow);
  }

  @media (max-width: 600px) {
    .top-controls { top: 8px; left: 8px; }
  }
</style>
"""


COMMON_JS = """
<script>
(function() {
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('weather-theme', theme);
  }
  var savedTheme = localStorage.getItem('weather-theme');
  if (!savedTheme) {
    savedTheme = window.matchMedia &&
                 window.matchMedia('(prefers-color-scheme: light)').matches
                 ? 'light' : 'dark';
  }
  applyTheme(savedTheme);

  window.toggleTheme = function() {
    var cur = document.documentElement.getAttribute('data-theme') || 'dark';
    applyTheme(cur === 'dark' ? 'light' : 'dark');
    var btn = document.getElementById('theme-btn');
    if (btn) btn.textContent = (cur === 'dark') ? '☀️' : '🌙';
  };

  window.__currentTheme = savedTheme;

  window.MyPlaces = {
    KEY: 'weather-places',
    list: function() {
      try { return JSON.parse(localStorage.getItem(this.KEY) || '[]'); }
      catch(e) { return []; }
    },
    add: function(name, lat, lon, model) {
      var list = this.list();
      list = list.filter(function(p) {
        return !(Math.abs(p.lat - lat) < 0.001 && Math.abs(p.lon - lon) < 0.001);
      });
      list.unshift({
        name: name, lat: lat, lon: lon,
        model: model || 'gfs',
        added: new Date().toISOString()
      });
      if (list.length > 10) list = list.slice(0, 10);
      localStorage.setItem(this.KEY, JSON.stringify(list));
      return list;
    },
    remove: function(lat, lon) {
      var list = this.list().filter(function(p) {
        return !(Math.abs(p.lat - lat) < 0.001 && Math.abs(p.lon - lon) < 0.001);
      });
      localStorage.setItem(this.KEY, JSON.stringify(list));
      return list;
    },
    clear: function() { localStorage.removeItem(this.KEY); }
  };

  window.addCurrentPlace = function() {
    var el = document.getElementById('place-data');
    if (!el) return;
    try {
      var data = JSON.parse(el.textContent);
      window.MyPlaces.add(data.name, data.lat, data.lon, data.model);
      alert('Добавлено в «Мои места»: ' + data.name);
    } catch(e) { alert('Не удалось добавить'); }
  };

  window.removePlace = function(lat, lon) {
    window.MyPlaces.remove(lat, lon);
    window.location.reload();
  };

  window.setWeather = function(w) {
    document.body.setAttribute('data-weather', w);
    localStorage.setItem('weather-bg-weather', w);
  };
})();
</script>
"""


def render_top_controls():
    return """
    <div class="top-controls">
      <button id="theme-btn" onclick="toggleTheme()" title="Сменить тему">🌙</button>
    </div>
    <script>
      (function(){
        var b = document.getElementById('theme-btn');
        if (b) b.textContent = (window.__currentTheme === 'light') ? '☀️' : '🌙';
      })();
    </script>
    """


FORECAST_HUB_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Прогноз — weather-msk</title>
""" + BASE_STYLE + """
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>🌍 Прогноз погоды</h1>
<div class="sub">Численные модели, поиск по точке, сравнение</div>

<a class="card fade-in" href="/model/gfs" style="animation-delay: 0.05s">
  <span class="icon">🌐</span><b>Модель GFS (США)</b>
  <div class="desc">Глобальная модель NOAA, ~13 км · таблица, текст, график</div>
</a>

<a class="card fade-in" href="/model/ecmwf" style="animation-delay: 0.10s">
  <span class="icon">🌐</span><b>Модель ECMWF (Европа)</b>
  <div class="desc">Эталонная европейская модель, ~9–25 км</div>
</a>

<a class="card fade-in" href="/model/icon" style="animation-delay: 0.15s">
  <span class="icon">🌐</span><b>Модель ICON (Германия)</b>
  <div class="desc">Модель DWD, ~11 км</div>
</a>

<a class="card fade-in" href="/search" style="animation-delay: 0.20s;background:rgba(124,92,255,0.10);">
  <span class="icon">🔍</span><b>Поиск прогноза для любой точки</b>
  <div class="desc">Город, координаты, индекс — с таблицей, текстом и графиком</div>
</a>

<a class="card fade-in" href="/chart/tushino" style="animation-delay: 0.25s">
  <span class="icon">📈</span><b>Сравнить модели на графике</b>
  <div class="desc">Температура, θ, ветер, осадки, давление</div>
</a>

<a class="card fade-in" href="/map" style="animation-delay: 0.30s">
  <span class="icon">🗺</span><b>Карта + спутник + радар</b>
  <div class="desc">OSM · Meteosat · RainViewer · поиск · клик</div>
</a>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


ANALYSIS_HUB_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Анализ — weather-msk</title>
""" + BASE_STYLE + """
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>📊 Анализ и проверка</h1>
<div class="sub">Сравнение с фактом, статистика, история ошибок</div>

<a class="card fade-in" href="/verify/tushino" style="animation-delay: 0.05s;background:rgba(0,229,160,0.08);">
  <span class="icon">✅</span><b>Проверка моделей</b>
  <div class="desc">Сравнение с фактом (станция / ERA5) — MAE, RMSE, Bias</div>
</a>

<a class="card fade-in" href="/verify/tushino/history" style="animation-delay: 0.10s;background:rgba(0,229,160,0.06);">
  <span class="icon">📉</span><b>История ошибок</b>
  <div class="desc">Как менялась MAE и Bias за последние дни</div>
</a>

<a class="card fade-in" href="/analyze/tushino" style="animation-delay: 0.15s;background:rgba(124,92,255,0.10);">
  <span class="icon">📊</span><b>Статистический анализ</b>
  <div class="desc">Корреляция, R², MAPE, гистограмма ошибок, F1 по осадкам</div>
</a>

<a class="card fade-in" href="/compare/tushino" style="animation-delay: 0.20s">
  <span class="icon">🔀</span><b>Сводка явлений</b>
  <div class="desc">Сколько часов тумана, грозы, осадков по каждой модели</div>
</a>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


THEORY_HUB_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Теория — weather-msk</title>
""" + BASE_STYLE + """
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>📚 Теория и методы</h1>
<div class="sub">Авиационные методы, матрицы Хандожко, складки тропопаузы, учебные примеры</div>

<a class="card fade-in" href="/aviation/gfs/tushino" style="animation-delay: 0.05s;background:rgba(255,181,71,0.10);">
  <span class="icon">✈️</span><b>Авиационные прогнозы</b>
  <div class="desc">Методы Богаткина: Вайтинг (K), LI, CAPE, туман по Кирюхину</div>
</a>

<a class="card fade-in" href="/alt-verify/tushino" style="animation-delay: 0.10s;background:rgba(0,229,160,0.10);">
  <span class="icon">📋</span><b>Матрица альтернативных прогнозов</b>
  <div class="desc">Критерии Хандожко: p, H, Q, v, τ, A</div>
</a>

<a class="card fade-in" href="/compare-matrices/tushino" style="animation-delay: 0.15s;background:rgba(255,181,71,0.15);">
  <span class="icon">🔀</span><b>Сравнить модели по матрицам</b>
  <div class="desc">GFS vs ECMWF vs ICON — p, H, Q, v, τ, A, S Хайдке</div>
</a>

<a class="card fade-in" href="/tropopause" style="animation-delay: 0.20s;background:rgba(124,92,255,0.10);">
  <span class="icon">🌀</span><b>Складки тропопаузы</b>
  <div class="desc">EPV (Ertel PV), динамическая тропопауза 2 PVU, анализ профиля</div>
</a>

<a class="card fade-in" href="/teaching" style="animation-delay: 0.25s;background:rgba(0,229,160,0.08);">
  <span class="icon">📚</span><b>Учебные примеры</b>
  <div class="desc">Разборы из учебника Дробжевой и Волобуевой</div>
</a>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


INDEX_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Прогноз погоды — weather-msk</title>
""" + BASE_STYLE + """
</head>
<body>

<h1>Прогноз погоды</h1>
<div class="sub">Выберите раздел</div>

<a class="card fade-in" href="/forecast" style="animation-delay: 0.05s;background:rgba(77,171,255,0.10);">
  <span class="icon">🌍</span><b>Прогноз погоды</b>
  <div class="desc">Численные модели GFS / ECMWF / ICON, поиск по точке, сравнение на графике</div>
</a>

<a class="card fade-in" href="/analysis" style="animation-delay: 0.10s;background:rgba(0,229,160,0.10);">
  <span class="icon">📊</span><b>Анализ и проверка</b>
  <div class="desc">Сравнение с фактом, MAE / RMSE / Bias, история ошибок, статистика</div>
</a>

<a class="card fade-in" href="/theory" style="animation-delay: 0.15s;background:rgba(255,181,71,0.10);">
  <span class="icon">📚</span><b>Теория и методы</b>
  <div class="desc">Авиационные прогнозы, матрицы Хандожко, критерии успешности, складки тропопаузы</div>
</a>

<a class="card fade-in" href="/map" style="animation-delay: 0.20s;background:rgba(124,92,255,0.10);">
  <span class="icon">🗺</span><b>Карта + спутник + радар</b>
  <div class="desc">OSM · Meteosat · RainViewer · поиск · клик по точке</div>
</a>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""

# ============================================================
# ОСТАЛЬНЫЕ СТРАНИЦЫ
# ============================================================
ABOUT_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>О проекте — weather-msk</title>
""" + BASE_STYLE + """
</head>
<body>
<a class="back" href="/">← На главную</a>
<h1>О проекте</h1>
<div class="sub">Источники данных, модели, метрики</div>
<p style="color:var(--text-1);font-size:14px;line-height:1.8;max-width:800px;">
<b>weather-msk</b> — учебно-исследовательский проект: сравнение прогнозов
нескольких численных моделей атмосферы между собой и с фактическими данными.
</p>
""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


MAP_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Карта — weather-msk</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
""" + BASE_STYLE + """
<style>
  #map { height: 75vh; min-height: 480px; border-radius: 16px;
         border: 1px solid var(--border); overflow: hidden; }
</style>
</head>
<body>
<a class="back" href="/">← Главная</a>
<h1>Карта</h1>
<div id="map"></div>
<script>
  var map = L.map('map').setView([55.7558, 37.6173], 6);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO', maxZoom: 19
  }).addTo(map);
</script>
""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


TEACHING_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Учебные примеры — weather-msk</title>
""" + BASE_STYLE + """
</head>
<body>
<a class="back" href="/theory">← Теория</a>
<h1>Учебные примеры</h1>
<div class="sub">По учебнику Дробжевой и Волобуевой (СПб, 2016)</div>
<p style="color:var(--text-1);font-size:14px;line-height:1.8;max-width:800px;">
Разборы примеров из глав 3–5. Для каждого примера можно открыть
интерактивную страницу <code>/alt-verify</code> с предустановленными параметрами.
</p>
""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


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
  }
  .controls label { color: var(--text-1); font-size: 13px; }
  .controls a {
    padding: 8px 14px; border-radius: 10px; font-size: 13px;
    background: var(--bg-1); border: 1px solid var(--border);
    color: var(--text-0); text-decoration: none;
  }
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
</style>
</head>
<body>

<a class="back" href="/theory">← Теория</a>
<h1>🌀 Складки тропопаузы</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · {{ target_date }} · EPV (Ertel PV) · 2 PVU</div>

{% if error %}
  <div class="error-box">⚠️ {{ error }}</div>
{% endif %}

<!-- Станции -->
<div class="controls">
  <label>Станция:</label>
  {% for key, st in stations.items() %}
    <a href="/tropopause?station={{ key }}&hour={{ hour_index }}&date={{ target_date }}"
       class="{% if key == station_key %}active{% endif %}">{{ st.name }}</a>
  {% endfor %}
</div>

<!-- Часы -->
<div class="controls">
  <label>Час (МСК):</label>
  {% for h in hours_options %}
    <a href="/tropopause?station={{ station_key }}&hour={{ h }}&date={{ target_date }}"
       class="{% if h == hour_index %}active{% endif %}">{{ '%02d'|format(h) }}:00</a>
  {% endfor %}
</div>

{% if analysis and summary %}
<!-- Сводка -->
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

<!-- График: PV по часам -->
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

<!-- Описание текущего часа -->
{% if selected %}
<div class="section">
  <h2>🔍 Анализ часа {{ '%02d'|format(hour_index) }}:00</h2>
  <div class="description-box {% if selected.has_fold %}desc-fold{% else %}desc-no-fold{% endif %}">
    {% if selected.has_fold %}⚠️{% else %}✅{% endif %}
    {{ selected.description }}
  </div>
</div>

<!-- Профиль по уровням -->
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

<!-- Методика -->
<div class="methodology">
  <h2>📚 Методика расчёта EPV</h2>
  <p>
    <b>Ertel PV (Potential Vorticity)</b> в изобарических координатах:<br>
    <code>PV = −g · (ζ + f) · (Δθ / Δp)</code>
  </p>
  <p>
    где:
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

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


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
    border-radius: 14px;
  }
  .controls label { color: var(--text-1); font-size: 13px; }
  .controls select, .controls a {
    padding: 8px 14px; border-radius: 10px; font-size: 13px;
    background: var(--bg-1); border: 1px solid var(--border);
    color: var(--text-0); text-decoration: none; cursor: pointer;
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

<a class="back" href="/analysis">← Анализ</a>
<h1>Проверка моделей</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · период: {{ days }} дней</div>

<!-- Контролы -->
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

<!-- Карточки моделей -->
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
          <span class="val {% if st.temp.bias is not none and st.temp.bias|abs < 0.5 %}good{% elif st.temp.bias is not none and st.temp.bias|abs < 1.5 %}warn{% else %}bad{% endif %}">
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

<!-- Детали выбранной модели -->
{% if detail and not detail.error %}
<div class="detail-section">
  <h2>🔬 Детали: {{ detail.model_name }}</h2>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">
    <!-- Scatter -->
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
            <!-- Оси -->
            <line x1="5" y1="95" x2="95" y2="95" stroke="var(--text-2)" stroke-width="0.3"/>
            <line x1="5" y1="5"  x2="5"  y2="95" stroke="var(--text-2)" stroke-width="0.3"/>
            <!-- Диагональ y=x -->
            <line x1="5" y1="95" x2="95" y2="5"
                  stroke="rgba(255,181,71,0.5)" stroke-width="0.4"
                  stroke-dasharray="1 1"/>
            <!-- Точки -->
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

    <!-- Гистограмма ошибок -->
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

<!-- Ссылка на историю -->
<div style="margin: 24px 0;">
  <a class="card fade-in" href="/verify/{{ station_key }}/history"
     style="background:rgba(0,229,160,0.08);">
    <span class="icon">📉</span><b>История ошибок по дням</b>
    <div class="desc">Как менялась MAE и Bias за последние {{ history_days }} дней</div>
  </a>
</div>

""" + COMMON_JS + render_top_controls() + """
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
    border-radius: 14px;
  }
  .controls label { color: var(--text-1); font-size: 13px; }
  .controls a {
    padding: 8px 14px; border-radius: 10px; font-size: 13px;
    background: var(--bg-1); border: 1px solid var(--border);
    color: var(--text-0); text-decoration: none;
  }
  .controls a.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25), rgba(124,92,255,0.25));
    border-color: var(--accent);
  }

  .legend {
    display: flex; gap: 16px; flex-wrap: wrap;
    padding: 12px 18px; margin-bottom: 16px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 14px; font-size: 13px;
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
    border-radius: 16px;
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

<a class="back" href="/verify/{{ station_key }}">← К проверке</a>
<h1>📉 История ошибок по дням</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · последние {{ days }} дней</div>

{% if error %}
  <div class="error-box">⚠️ {{ error }}</div>
{% endif %}

<!-- Период -->
<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    <a href="/verify/{{ station_key }}/history?days={{ d }}"
       class="{% if d == days %}active{% endif %}">{{ d }} дней</a>
  {% endfor %}
</div>

{% if dates %}
<!-- Легенда -->
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

<!-- MAE -->
<div class="chart-block">
  <h2>📊 MAE по дням (°C)</h2>
  {{ svg_mae | safe }}
</div>

<!-- Bias -->
<div class="chart-block">
  <h2>📊 Bias по дням (°C)</h2>
  {{ svg_bias | safe }}
</div>

<!-- RMSE -->
<div class="chart-block">
  <h2>📊 RMSE по дням (°C)</h2>
  {{ svg_rmse | safe }}
</div>

<!-- Таблица -->
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

""" + COMMON_JS + render_top_controls() + """
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
    border-radius: 14px;
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

<a class="back" href="/analysis">← Анализ</a>
<h1>Расширенный анализ</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · {{ days }} дней</div>

<!-- Контролы -->
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

<!-- KPI-панель -->
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

<!-- График по дням -->
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

<!-- Таблица по дням -->
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

<!-- Scatter + гистограмма -->
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

<!-- Сравнение всех моделей -->
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

""" + COMMON_JS + render_top_controls() + """
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
    border-radius: 14px;
  }
  .controls label { color: var(--text-1); font-size: 13px; }
  .controls a {
    padding: 8px 14px; border-radius: 10px; font-size: 13px;
    background: var(--bg-1); border: 1px solid var(--border);
    color: var(--text-0); text-decoration: none;
  }
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

<a class="back" href="/theory">← Теория</a>
<h1>✈️ Авиационные прогнозы</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · {{ model_name }} · {{ days }} дня</div>

{% if error %}
  <div class="error-box">⚠️ {{ error }}</div>
{% endif %}

<!-- Модели -->
<div class="model-switcher">
  {% for m in model_switcher %}
    <a href="/aviation/{{ m.key }}/{{ station_key }}?days={{ days }}"
       class="{% if m.active %}active{% endif %}">{{ m.name }}</a>
  {% endfor %}
</div>

<!-- Период -->
<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    <a href="/aviation/{{ model }}/{{ station_key }}?days={{ d }}"
       class="{% if d == days %}active{% endif %}">{{ d }} дн.</a>
  {% endfor %}
</div>

<!-- Сводка -->
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

<!-- Таблицы по дням -->
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

<!-- Методика -->
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
    облачность &lt; 30%, ночные часы (0–9), RH ≥ 90%.<br>
    Каждое условие даёт +1 балл. Итог: 0–1 — нет, 2 — слабая, 3 — умеренная, 4 — высокая, 5 — очень высокая.
  </p>
</div>

""" + COMMON_JS + render_top_controls() + """
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
    border-radius: 14px;
  }
  .controls label { color: var(--text-1); font-size: 13px; }
  .controls a {
    padding: 8px 14px; border-radius: 10px; font-size: 13px;
    background: var(--bg-1); border: 1px solid var(--border);
    color: var(--text-0); text-decoration: none;
  }
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

<a class="back" href="/theory">← Теория</a>
<h1>📋 Матрица альтернативных прогнозов</h1>
<div class="sub">{{ title }} · {{ lat }}, {{ lon }} · {{ phenomena[phenomenon].name }} · {{ days }} дней</div>

<!-- Явление -->
<div class="controls">
  <label>Явление:</label>
  {% for key, ph in phenomena.items() %}
    {% set url = ('/alt-verify/' ~ station_key) if station_key else '/alt-verify' %}
    <a href="{{ url }}?phenomenon={{ key }}&days={{ days }}{% if not station_key %}&lat={{ lat }}&lon={{ lon }}&name={{ title }}{% endif %}"
       class="{% if phenomenon == key %}active{% endif %}">{{ ph.name }}</a>
  {% endfor %}
</div>

<!-- Период -->
<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    {% set url = ('/alt-verify/' ~ station_key) if station_key else '/alt-verify' %}
    <a href="{{ url }}?phenomenon={{ phenomenon }}&days={{ d }}{% if not station_key %}&lat={{ lat }}&lon={{ lon }}&name={{ title }}{% endif %}"
       class="{% if d == days %}active{% endif %}">{{ d }} дней</a>
  {% endfor %}
</div>

<!-- Матрицы по моделям -->
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

<!-- Сравнение по критериям -->
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

<!-- Методика -->
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

""" + COMMON_JS + render_top_controls() + """
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
    border-radius: 14px;
  }
  .controls label { color: var(--text-1); font-size: 13px; }
  .controls a {
    padding: 8px 14px; border-radius: 10px; font-size: 13px;
    background: var(--bg-1); border: 1px solid var(--border);
    color: var(--text-0); text-decoration: none;
  }
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

<a class="back" href="/theory">← Теория</a>
<h1>🔀 Сравнение моделей по матрицам Хандожко</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · {{ days }} дней</div>

<!-- Период -->
<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    <a href="/compare-matrices/{{ station_key }}?days={{ d }}"
       class="{% if d == days %}active{% endif %}">{{ d }} дней</a>
  {% endfor %}
</div>

{% if results_per_phenomenon %}
<!-- Сводная таблица: какая модель лучше по каждому явлению -->
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

<!-- Детальные таблицы по явлениям -->
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

<!-- Методика -->
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

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


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
    background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px; }
  .controls label { color: var(--text-1); font-size: 13px; }
  .controls a { padding: 8px 14px; border-radius: 10px; font-size: 13px;
    background: var(--bg-1); border: 1px solid var(--border);
    color: var(--text-0); text-decoration: none; }
  .controls a.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25), rgba(124,92,255,0.25));
    border-color: var(--accent); }
  .legend { display: flex; gap: 16px; flex-wrap: wrap;
    padding: 12px 18px; margin-bottom: 16px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 14px; font-size: 13px; }
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

<a class="back" href="/forecast">← Прогноз</a>
<h1>📈 Сравнение моделей</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }} · {{ days }} дней</div>

{% if error %}
  <div class="error-box">⚠️ {{ error }}</div>
{% endif %}

<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    <a href="/chart/{{ station_key }}?days={{ d }}&models={{ selected_models|join(',') }}"
       class="{% if d == days %}active{% endif %}">{{ d }} дней</a>
  {% endfor %}

  <label style="margin-left:12px;">Модели:</label>
  {% for key, m in models.items() %}
    <a href="/chart/{{ station_key }}?days={{ days }}&models={{ toggle_models[key]|join(',') }}"
       class="{% if key in selected_models %}active{% endif %}">{{ m.name }}</a>
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

""" + COMMON_JS + render_top_controls() + """
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
<a class="back" href="/analysis">← Анализ</a>
<h1>Сводка явлений</h1>
<div class="sub">{{ station_name }}</div>
<p style="color:var(--text-1);font-size:14px;line-height:1.8;">
Раздел в разработке.
</p>
""" + COMMON_JS + render_top_controls() + """
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
<a class="back" href="/forecast">← Прогноз</a>
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

""" + COMMON_JS + render_top_controls() + """
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

<a class="back" href="/model/{{ model }}">← {{ model_name }}</a>
<h1>{{ station }}</h1>
<div class="sub">{{ model_name }} · {{ lat }}, {{ lon }} · прогноз на {{ days }} дня</div>

{% if error %}
<div class="error-box">⚠️ Ошибка: {{ error }}</div>
{% endif %}

<!-- Переключатель моделей -->
<div class="model-switcher">
  {% for m in model_switcher %}
    <a href="/forecast/{{ m.key }}/{{ station_key }}"
       class="{% if m.active %}active{% endif %}">{{ m.name }}</a>
  {% endfor %}
  <a href="/text/{{ model }}/{{ station_key }}">📝 Текст</a>
  <a href="/chart/{{ station_key }}">📈 График</a>
</div>

<!-- Сводка событий -->
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

<!-- Таблицы по дням -->
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

""" + COMMON_JS + render_top_controls() + """
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
    border-radius: 14px;
  }
  .controls label { color: var(--text-1); font-size: 13px; }
  .controls a {
    padding: 8px 14px; border-radius: 10px; font-size: 13px;
    background: var(--bg-1); border: 1px solid var(--border);
    color: var(--text-0); text-decoration: none;
  }
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

<a class="back" href="/forecast/{{ model }}/{{ station_key }}">← Таблица</a>
<h1>📝 {{ station }}</h1>
<div class="sub">{{ model_name }} · текстовый прогноз на {{ days }} дн.</div>

{% if error %}
  <div class="error-box">⚠️ {{ error }}</div>
{% endif %}

<!-- Переключатель моделей -->
<div class="model-switcher">
  {% for m in model_switcher %}
    <a href="/text/{{ m.key }}/{{ station_key }}?days={{ days }}"
       class="{% if m.active %}active{% endif %}">{{ m.name }}</a>
  {% endfor %}
</div>

<!-- Период -->
<div class="controls">
  <label>Период:</label>
  {% for d in days_options %}
    <a href="/text/{{ model }}/{{ station_key }}?days={{ d }}"
       class="{% if d == days %}active{% endif %}">{{ d }} дн.</a>
  {% endfor %}
</div>

<!-- Текст -->
<div class="text-block">
  <pre>{{ text }}</pre>
</div>

<!-- Ссылки -->
<div class="action-row">
  <a href="/forecast/{{ model }}/{{ station_key }}">📊 Таблица</a>
  <a href="/chart/{{ station_key }}?days={{ days }}">📈 График</a>
  <a href="/aviation/{{ model }}/{{ station_key }}?days={{ days }}">✈️ Авиация</a>
</div>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


SEARCH_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Поиск — weather-msk</title>
""" + BASE_STYLE + """
</head>
<body>
<a class="back" href="/forecast">← Прогноз</a>
<h1>Поиск прогноза</h1>
<div class="sub">Введите город или координаты</div>

<div style="background:var(--card-bg);border:1px solid var(--border);border-radius:14px;padding:12px;display:flex;gap:10px;margin-bottom:16px;">
  <input type="text" id="q" placeholder="Москва, 55.41 37.90..."
         style="flex:1;padding:12px 16px;background:var(--bg-1);border:1px solid var(--border);border-radius:10px;color:var(--text-0);font-size:14px;outline:none;"
         onkeydown="if(event.key==='Enter') doSearch()">
  <button onclick="doSearch()"
          style="padding:12px 22px;border:none;border-radius:10px;background:linear-gradient(135deg,#4dabff,#7c5cff);color:#fff;cursor:pointer;font-size:14px;font-weight:600;">
    🔍 Найти
  </button>
</div>

<div style="background:var(--card-bg);border:1px solid var(--border);border-radius:14px;padding:12px;display:flex;align-items:center;gap:12px;margin-bottom:16px;">
  <label style="color:var(--text-1);font-size:13px;">Модель:</label>
  <select id="model" style="padding:10px 14px;background:var(--bg-1);border:1px solid var(--border);border-radius:10px;color:var(--text-0);font-size:14px;outline:none;">
    {% for key, m in models.items() %}
      <option value="{{ key }}">{{ m.name }}</option>
    {% endfor %}
  </select>
</div>

<div id="results"></div>

<script>
  async function doSearch() {
    var q = document.getElementById('q').value.trim();
    if (!q) return;
    var model = document.getElementById('model').value;
    var results = document.getElementById('results');
    results.innerHTML = '<div style="color:var(--accent);padding:20px;">⏳ Поиск...</div>';

    var coordMatch = q.match(/^(-?\\d+\\.?\\d*)[\\s,]+(-?\\d+\\.?\\d*)$/);
    if (coordMatch) {
      var lat = parseFloat(coordMatch[1]);
      var lon = parseFloat(coordMatch[2]);
      if (lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
        window.location.href = '/forecast/point?lat=' + lat + '&lon=' + lon +
          '&name=' + encodeURIComponent(lat + ', ' + lon) + '&model=' + model + '&view=table';
        return;
      }
    }

    try {
      var url = '/api/geocode?q=' + encodeURIComponent(q);
      var resp = await fetch(url);
      var data = await resp.json();

      if (!data.results || data.results.length === 0) {
        results.innerHTML = '<div style="color:var(--text-2);padding:20px;">Ничего не найдено.</div>';
        return;
      }

      var html = '';
      data.results.forEach(function(p) {
        var label = [p.name, p.admin1, p.country].filter(Boolean).join(', ');
        var url = '/forecast/point?lat=' + p.latitude + '&lon=' + p.longitude +
                  '&name=' + encodeURIComponent(label) + '&model=' + model + '&view=table';
        html += '<a href="' + url + '" style="display:block;padding:12px 16px;margin:6px 0;background:var(--card-bg);border:1px solid var(--border);border-radius:10px;text-decoration:none;color:var(--text-0);">' +
          '📍 <b>' + p.name + '</b> <span style="color:var(--text-2);font-size:12px;">' + label + '</span>' +
        '</a>';
      });
      results.innerHTML = html;
    } catch (err) {
      results.innerHTML = '<div style="color:#ff5470;padding:20px;">Ошибка: ' + err.message + '</div>';
    }
  }
</script>

""" + COMMON_JS + render_top_controls() + """
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
""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""