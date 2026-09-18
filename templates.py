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
<title>Складки тропопаузы — weather-msk</title>
""" + BASE_STYLE + """
</head>
<body>
<a class="back" href="/theory">← Теория</a>
<h1>🌀 Складки тропопаузы</h1>
<div class="sub">EPV (Ertel PV) · динамическая тропопауза 2 PVU</div>
<p style="color:var(--text-1);font-size:14px;line-height:1.8;max-width:800px;">
Складка тропопаузы — область, где стратосферный воздух (PV &gt; 2 PVU)
спускается в тропосферу. Расчёт основан на данных Open-Meteo.
</p>
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
</head>
<body>
<a class="back" href="/analysis">← Анализ</a>
<h1>Проверка моделей</h1>
<div class="sub">{{ station_name }} · сравнение прогноза с фактом</div>
<p style="color:var(--text-1);font-size:14px;line-height:1.8;">
Раздел в разработке. Скоро здесь появится таблица MAE / RMSE / Bias по каждой модели.
</p>
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
</head>
<body>
<a class="back" href="/verify/{{ station_key }}">← К проверке</a>
<h1>История ошибок</h1>
<div class="sub">{{ station_name }} · последние {{ history_days }} дней</div>
<p style="color:var(--text-1);font-size:14px;line-height:1.8;">
Раздел в разработке.
</p>
""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


ANALYZE_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Анализ — {{ station_name }}</title>
""" + BASE_STYLE + """
</head>
<body>
<a class="back" href="/analysis">← Анализ</a>
<h1>Статистический анализ</h1>
<div class="sub">{{ station_name }}</div>
<p style="color:var(--text-1);font-size:14px;line-height:1.8;">
Раздел в разработке.
</p>
""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


AVIATION_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Авиация — {{ station_name }}</title>
""" + BASE_STYLE + """
</head>
<body>
<a class="back" href="/theory">← Теория</a>
<h1>Авиационные прогнозы</h1>
<div class="sub">{{ station_name }}</div>
<p style="color:var(--text-1);font-size:14px;line-height:1.8;">
Раздел в разработке.
</p>
""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


ALT_VERIFY_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Матрица — {{ title }}</title>
""" + BASE_STYLE + """
</head>
<body>
<a class="back" href="/theory">← Теория</a>
<h1>Матрица альтернативных прогнозов</h1>
<div class="sub">{{ title }}</div>
<p style="color:var(--text-1);font-size:14px;line-height:1.8;">
Раздел в разработке.
</p>
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
</head>
<body>
<a class="back" href="/theory">← Теория</a>
<h1>Сравнение моделей по матрицам</h1>
<div class="sub">{{ station_name }}</div>
<p style="color:var(--text-1);font-size:14px;line-height:1.8;">
Раздел в разработке.
</p>
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
</head>
<body>
<a class="back" href="/forecast">← Прогноз</a>
<h1>Сравнение моделей</h1>
<div class="sub">{{ station_name }} · {{ lat }}, {{ lon }}</div>
<p style="color:var(--text-1);font-size:14px;line-height:1.8;">
Раздел в разработке.
</p>
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
</head>
<body>
<a class="back" href="/model/{{ model }}">← Назад</a>
<h1>{{ station }}</h1>
<div class="sub">Модель: {{ model_name }} · {{ lat }}, {{ lon }} · прогноз на {{ days }} дня</div>
<p style="color:var(--text-1);font-size:14px;line-height:1.8;">
Раздел в разработке.
</p>
""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


TEXT_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ station }} — текст</title>
""" + BASE_STYLE + """
</head>
<body>
<a class="back" href="/model/{{ model }}">← Назад</a>
<h1>{{ station }}</h1>
<div class="sub">Модель: {{ model_name }} · текстовый прогноз на {{ days }} дня</div>
<div class="card" style="background:var(--card-bg);border:1px solid var(--border);border-radius:16px;padding:24px;margin-top:16px;">
<pre style="white-space:pre-wrap;font-family:'Inter',sans-serif;font-size:15px;line-height:1.8;margin:0;color:var(--text-0);">{{ text }}</pre>
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