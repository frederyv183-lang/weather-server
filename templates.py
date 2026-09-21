# -*- coding: utf-8 -*-
"""
Шаблоны и стили для server.py.
Только константы и функции рендера, без маршрутов.

Структура:
    1. Импорты
    2. BASE_STYLE — базовые стили
    3. COMMON_JS — общий JavaScript
    4. render_top_controls() — кнопки темы/сезона
    5. render_legend() — легенда сокращений
    6. render_biblio_ref() — врезка «Источник»
    7. HTML-константы страниц (INDEX, FORECAST, ANALYSIS, THEORY, ...)
    8. Страницы теории по группам (METHODS, MATRICES, INDICES)
    9. BIBLIOGRAPHY_HTML
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
  body { padding: 20px; max-width: 1400px; margin: 0 auto; }

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

  body[data-season="winter"]::before {
    background: linear-gradient(180deg, #0a1228 0%, #1a2545 50%, #2a3a6b 100%);
  }
  body[data-season="spring"]::before {
    background: linear-gradient(180deg, #0a1e3d 0%, #1a4a3a 50%, #2d6b4a 100%);
  }
  body[data-season="summer"]::before {
    background: linear-gradient(180deg, #0a1e3d 0%, #1a3a6b 40%, #2d5a9e 100%);
  }
  body[data-season="autumn"]::before {
    background: linear-gradient(180deg, #1a1533 0%, #4a2954 35%, #8a4a3a 100%);
  }
  [data-theme="light"] body[data-season="winter"]::before {
    background: linear-gradient(180deg, #e8f0ff 0%, #c8d8f0 50%, #a8c0e0 100%);
  }
  [data-theme="light"] body[data-season="spring"]::before {
    background: linear-gradient(180deg, #d8f0d0 0%, #b8e0a8 50%, #90d080 100%);
  }
  [data-theme="light"] body[data-season="summer"]::before {
    background: linear-gradient(180deg, #c8e3ff 0%, #a3d0ff 60%, #7cbaff 100%);
  }
  [data-theme="light"] body[data-season="autumn"]::before {
    background: linear-gradient(180deg, #ffd7a0 0%, #ffb878 50%, #e08a5a 100%);
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
    position: fixed; top: 16px; right: 16px; z-index: 9999;
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


# ==================================================================
# COMMON_JS — общий JavaScript для всех страниц
# ==================================================================
COMMON_JS = """
<script>
(function() {
  // ============================================================
  // ТЕМА (тёмная / светлая)
  // ============================================================
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

  // ============================================================
  // ВРЕМЯ СУТОК
  // ============================================================
  function autoTod() {
    var h = new Date().getHours();
    if (h >= 5 && h < 9)  return 'dawn';
    if (h >= 9 && h < 17) return 'day';
    if (h >= 17 && h < 21) return 'dusk';
    return 'night';
  }
  document.body.setAttribute('data-tod', autoTod());

  // ============================================================
  // СЕЗОН
  // ============================================================
  function applySeason(season) {
    document.body.setAttribute('data-season', season);
  }
  function autoSeason() {
    var m = new Date().getMonth() + 1;
    if (m === 12 || m <= 2) return 'winter';
    if (m <= 5) return 'spring';
    if (m <= 8) return 'summer';
    return 'autumn';
  }
  var savedSeason = localStorage.getItem('weather-season');
  if (!savedSeason || savedSeason === 'auto') {
    applySeason(autoSeason());
  } else {
    applySeason(savedSeason);
  }
  window.__currentSeason = savedSeason || 'auto';

  window.cycleSeason = function() {
    var order = ['auto', 'winter', 'spring', 'summer', 'autumn'];
    var cur = localStorage.getItem('weather-season') || 'auto';
    var idx = order.indexOf(cur);
    var next = order[(idx + 1) % order.length];
    if (next === 'auto') {
      localStorage.removeItem('weather-season');
      applySeason(autoSeason());
      window.__currentSeason = 'auto';
    } else {
      localStorage.setItem('weather-season', next);
      applySeason(next);
      window.__currentSeason = next;
    }
    updateSeasonButton();
  };

  window.updateSeasonButton = function() {
    var btn = document.getElementById('season-btn');
    if (!btn) return;
    var cur = localStorage.getItem('weather-season') || 'auto';
    var icons = { 'auto': '🍂', 'winter': '❄️', 'spring': '🌸', 'summer': '☀️', 'autumn': '🍁' };
    btn.textContent = icons[cur] || '🍂';
    btn.title = 'Сезон: ' + cur + ' (клик — сменить)';
  };

  // ============================================================
  // МОИ МЕСТА (localStorage)
  // ============================================================
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
      list.unshift({ name: name, lat: lat, lon: lon,
        model: model || 'gfs', added: new Date().toISOString() });
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


# ==================================================================
# ВЕРХНИЕ КНОПКИ (тема + сезон)
# ==================================================================
def render_top_controls():
    return """
    <div class="top-controls">
      <button id="theme-btn" onclick="toggleTheme()" title="Сменить тему">🌙</button>
      <button id="season-btn" onclick="cycleSeason()" title="Сезон">🍂</button>
    </div>
    <script>
      (function(){
        var b = document.getElementById('theme-btn');
        if (b) b.textContent = (window.__currentTheme === 'light') ? '☀️' : '🌙';
        if (typeof updateSeasonButton === 'function') updateSeasonButton();
      })();
    </script>
    """


# ==================================================================
# ЛЕГЕНДА СОКРАЩЕНИЙ
# ==================================================================
def render_legend(section_key):
    """
    Возвращает HTML-блок легенды сокращений для указанного раздела.
    section_key — ключ из LEGEND_ITEMS в core/dictionaries.py.

    Использование в шаблоне:
        HTML = "..." + render_legend("forecast") + "..."
    """
    from core.dictionaries import LEGEND_ITEMS

    items = LEGEND_ITEMS.get(section_key)
    if not items:
        return ""

    rows = "".join(
        f'<div class="legend-row">'
        f'<span class="legend-key">{key}</span>'
        f'<span class="legend-val">{val}</span>'
        f'</div>'
        for key, val in items
    )

    return f"""
<details class="legend-block">
  <summary>📖 Легенда сокращений</summary>
  <div class="legend-grid">
    {rows}
  </div>
</details>
<style>
  .legend-block {{
    margin: 32px 0 20px 0;
    padding: 14px 18px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    font-size: 13px;
    color: var(--text-1);
    backdrop-filter: blur(14px);
  }}
  .legend-block summary {{
    cursor: pointer;
    font-weight: 600;
    color: var(--text-0);
    font-size: 14px;
    list-style: none;
    outline: none;
    user-select: none;
    padding: 2px 0;
  }}
  .legend-block summary::-webkit-details-marker {{ display: none; }}
  .legend-block summary::before {{
    content: '▸ ';
    display: inline-block;
    transition: transform 0.2s;
    color: var(--accent);
    margin-right: 4px;
  }}
  .legend-block[open] summary::before {{
    transform: rotate(90deg);
  }}
  .legend-block summary:hover {{ color: var(--accent); }}
  .legend-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 6px 24px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border);
  }}
  .legend-row {{
    display: flex;
    gap: 10px;
    padding: 4px 0;
    border-bottom: 1px solid rgba(120, 160, 255, 0.05);
  }}
  .legend-row:last-child {{ border-bottom: none; }}
  .legend-key {{
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    color: var(--accent);
    min-width: 60px;
    flex-shrink: 0;
  }}
  .legend-val {{
    color: var(--text-1);
    font-size: 12px;
    line-height: 1.5;
  }}
</style>
"""


# ==================================================================
# ВРЕЗКА «ИСТОЧНИК» ДЛЯ БЛОКОВ ТЕОРИИ
# ==================================================================
def render_biblio_ref(topic_key, chapter=None, page=None):
    """
    Возвращает HTML-врезку «📖 Источник» для блока теории.
    topic_key — ключ из BIBLIOGRAPHY_ITEMS в core/dictionaries.py.
    chapter, page — опционально, уточнение (например, "гл. 5.2", "с. 114–118").
    """
    from core.dictionaries import BIBLIOGRAPHY_ITEMS

    topic = BIBLIOGRAPHY_ITEMS.get(topic_key)
    if not topic:
        return ""

    primary = topic["sources"][0]
    authors = primary["authors"]
    title = primary["title"]
    year = primary.get("year", "")

    detail = ""
    if chapter or page:
        parts = [p for p in [chapter, page] if p]
        detail = f" · {', '.join(parts)}"

    return f"""
<div class="biblio-ref">
  <span class="biblio-icon">📖</span>
  <span class="biblio-text">
    <b>{authors}</b> «{title}» ({year}){detail}
  </span>
  <a href="/bibliography#{topic_key}" class="biblio-link">Все источники →</a>
</div>
<style>
  .biblio-ref {{
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    margin: 16px 0;
    padding: 12px 16px;
    background: rgba(77, 171, 255, 0.06);
    border: 1px solid rgba(77, 171, 255, 0.2);
    border-left: 3px solid var(--accent);
    border-radius: 10px;
    font-size: 13px;
    color: var(--text-1);
    line-height: 1.5;
  }}
  .biblio-icon {{ font-size: 18px; flex-shrink: 0; }}
  .biblio-text {{ flex: 1; min-width: 200px; }}
  .biblio-text b {{ color: var(--text-0); }}
  .biblio-link {{
    color: var(--accent);
    text-decoration: none;
    font-weight: 600;
    font-size: 12px;
    white-space: nowrap;
  }}
  .biblio-link:hover {{ text-decoration: underline; }}
</style>
"""


# ==================================================================
# ХАБ: ПРОГНОЗ
# ==================================================================
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
<div class="sub">Численные модели · поиск по точке · сравнение · синоптика</div>

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
  <div class="desc">Город, координаты, индекс — таблица, текст, график, авиация, синоптика</div>
</a>

<a class="card fade-in" href="/chart/tushino" style="animation-delay: 0.25s">
  <span class="icon">📈</span><b>Сравнить модели на графике</b>
  <div class="desc">Температура, давление, ветер, осадки · факт ERA5</div>
</a>

<a class="card fade-in" href="/synoptic/gfs/tushino" style="animation-delay: 0.28s;background:rgba(255,84,112,0.10);">
  <span class="icon">🌡</span><b>Синоптика по уровням</b>
  <div class="desc">Профиль T, θ, RH на 925–300 гПа · тропопауза · струя · фронты · LI, K-Index</div>
</a>

<a class="card fade-in" href="/map" style="animation-delay: 0.30s">
  <span class="icon">🗺</span><b>Карта + спутник + радар</b>
  <div class="desc">OSM · спутник · RainViewer · облачность · поиск · клик по точке</div>
</a>

""" + COMMON_JS + render_top_controls() + render_legend("forecast") + """
</body>
</html>
"""


# ==================================================================
# ХАБ: АНАЛИЗ
# ==================================================================
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
<div class="sub">Сравнение с фактом · статистика · история ошибок · матрицы</div>

<a class="card fade-in" href="/verify/tushino" style="animation-delay: 0.05s;background:rgba(0,229,160,0.08);">
  <span class="icon">✅</span><b>Проверка моделей</b>
  <div class="desc">Сравнение с фактом (станция / ERA5) — MAE, RMSE, Bias, R²</div>
</a>

<a class="card fade-in" href="/verify/tushino/history" style="animation-delay: 0.10s;background:rgba(0,229,160,0.06);">
  <span class="icon">📉</span><b>История ошибок</b>
  <div class="desc">Как менялась MAE и Bias за последние дни — по каждой модели</div>
</a>

<a class="card fade-in" href="/analyze/tushino" style="animation-delay: 0.15s;background:rgba(124,92,255,0.10);">
  <span class="icon">📊</span><b>Статистический анализ</b>
  <div class="desc">Корреляция, R², MAPE, гистограмма ошибок, F1 по осадкам</div>
</a>

<a class="card fade-in" href="/alt-verify/tushino" style="animation-delay: 0.18s;background:rgba(255,181,71,0.10);">
  <span class="icon">📋</span><b>Матрица альтернативных прогнозов</b>
  <div class="desc">Критерии Хандожко: p, H, τ, v, Q, S, F1 · по каждому явлению</div>
</a>

<a class="card fade-in" href="/compare-matrices/tushino" style="animation-delay: 0.22s;background:rgba(255,181,71,0.15);">
  <span class="icon">🔀</span><b>Сравнить модели по матрицам</b>
  <div class="desc">GFS vs ECMWF vs ICON — по каждому явлению · лучшая модель</div>
</a>

<a class="card fade-in" href="/compare/tushino" style="animation-delay: 0.25s">
  <span class="icon">📋</span><b>Сводка явлений</b>
  <div class="desc">Сколько часов тумана, грозы, осадков по каждой модели</div>
</a>

""" + COMMON_JS + render_top_controls() + render_legend("analysis") + """
</body>
</html>
"""


# ==================================================================
# ХАБ: ТЕОРИЯ (4 группы)
# ==================================================================
THEORY_HUB_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Теория — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .theory-group {
    margin: 28px 0;
  }
  .theory-group-title {
    font-size: 14px;
    font-weight: 700;
    color: var(--text-2);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 0 0 12px 0;
    padding-left: 12px;
    border-left: 3px solid var(--accent);
  }
  .theory-group-title .group-icon {
    margin-right: 8px;
    font-size: 16px;
  }
</style>
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>📚 Теория и методы</h1>
<div class="sub">Методы прогноза · матрицы · индексы · учебные примеры</div>

<div class="theory-group">
  <h2 class="theory-group-title">
    <span class="group-icon">🧭</span>Группа А — Методы прогноза
  </h2>

  <a class="card fade-in" href="/aviation/gfs/tushino" style="animation-delay: 0.05s;background:rgba(255,181,71,0.10);">
    <span class="icon">✈️</span><b>Авиационные прогнозы (Богаткин)</b>
    <div class="desc">Методы Вайтинга (K), LI, CAPE, туман по Кирюхину · гл. 5–12</div>
  </a>

  <a class="card fade-in" href="/theory/methods" style="animation-delay: 0.10s;background:rgba(77,171,255,0.10);">
    <span class="icon">📐</span><b>Изоэнтропический метод</b>
    <div class="desc">Анализ на поверхностях θ, потенциальная завихрённость, PV-аномалии</div>
  </a>

  <a class="card fade-in" href="/synoptic/gfs/tushino" style="animation-delay: 0.15s;background:rgba(255,84,112,0.10);">
    <span class="icon">🌡</span><b>Синоптический метод</b>
    <div class="desc">Профиль T, θ, RH на 925–300 гПа · тропопауза · струя · фронты</div>
  </a>
</div>

<div class="theory-group">
  <h2 class="theory-group-title">
    <span class="group-icon">📋</span>Группа Б — Матрицы и критерии
  </h2>

  <a class="card fade-in" href="/alt-verify/tushino" style="animation-delay: 0.05s;background:rgba(0,229,160,0.10);">
    <span class="icon">📋</span><b>Матрица сопряжённости (2×2)</b>
    <div class="desc">Hits · Misses · False alarms · Correct negatives</div>
  </a>

  <a class="card fade-in" href="/theory/matrices" style="animation-delay: 0.10s;background:rgba(255,181,71,0.15);">
    <span class="icon">📊</span><b>Критерии Хандожко</b>
    <div class="desc">p · H · τ · v · Q · S — формулы и интерпретация</div>
  </a>

  <a class="card fade-in" href="/compare-matrices/tushino" style="animation-delay: 0.15s;background:rgba(255,181,71,0.10);">
    <span class="icon">🔀</span><b>Сравнить модели по матрицам</b>
    <div class="desc">GFS vs ECMWF vs ICON — по каждому явлению</div>
  </a>
</div>

<div class="theory-group">
  <h2 class="theory-group-title">
    <span class="group-icon">🌊</span>Группа В — Индексы и явления
  </h2>

  <a class="card fade-in" href="/theory/indices" style="animation-delay: 0.05s;background:rgba(124,92,255,0.10);">
    <span class="icon">⚡</span><b>Индексы неустойчивости</b>
    <div class="desc">LI · K-Index · CAPE · ΔT(850−500) · сдвиг ветра</div>
  </a>

  <a class="card fade-in" href="/climate" style="animation-delay: 0.10s;background:rgba(0,229,160,0.10);">
    <span class="icon">🌊</span><b>ENSO / Эль-Ниньо / Ла-Нинья</b>
    <div class="desc">ONI, SST Niño 3.4, климатические аномалии</div>
  </a>

  <a class="card fade-in" href="/climate" style="animation-delay: 0.15s;background:rgba(255,84,112,0.10);">
    <span class="icon">💥</span><b>Полярный вихрь и SSW</b>
    <div class="desc">Внезапные стратосферные потепления, PV на 10 гПа</div>
  </a>

  <a class="card fade-in" href="/tropopause" style="animation-delay: 0.20s;background:rgba(124,92,255,0.10);">
    <span class="icon">🌀</span><b>Складки тропопаузы (EPV)</b>
    <div class="desc">Ertel PV, динамическая тропопауза 2 PVU, анализ профиля</div>
  </a>
</div>

<div class="theory-group">
  <h2 class="theory-group-title">
    <span class="group-icon">📚</span>Группа Г — Учебное
  </h2>

  <a class="card fade-in" href="/teaching" style="animation-delay: 0.05s;background:rgba(0,229,160,0.08);">
    <span class="icon">📚</span><b>Учебные примеры</b>
    <div class="desc">Разборы из Богаткина и Волобуевой — формулы, методы, примеры</div>
  </a>

  <a class="card fade-in" href="/tests" style="animation-delay: 0.10s;background:rgba(77,171,255,0.10);">
    <span class="icon">📝</span><b>Тесты по блокам</b>
    <div class="desc">Проверка знаний: 20 вопросов, результат сразу, разбор ошибок</div>
  </a>

  <a class="card fade-in" href="/bibliography" style="animation-delay: 0.15s;background:rgba(255,181,71,0.10);">
    <span class="icon">📖</span><b>Библиография</b>
    <div class="desc">Источники по всем разделам: авиация, матрицы, ДЗЗ, динамика, климат</div>
  </a>
</div>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ==================================================================
# ГЛАВНАЯ
# ==================================================================
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
  <div class="desc">Сравнение с фактом, MAE / RMSE / Bias, история ошибок, статистика, матрицы</div>
</a>

<a class="card fade-in" href="/theory" style="animation-delay: 0.15s;background:rgba(255,181,71,0.10);">
  <span class="icon">📚</span><b>Теория и методы</b>
  <div class="desc">Авиационные прогнозы, матрицы Хандожко, критерии успешности, складки тропопаузы</div>
</a>

<a class="card fade-in" href="/map" style="animation-delay: 0.20s;background:rgba(124,92,255,0.10);">
  <span class="icon">🗺</span><b>Карта + спутник + радар</b>
  <div class="desc">OSM · спутник · RainViewer · поиск · клик по точке</div>
</a>

<a class="card fade-in" href="/about" style="animation-delay: 0.25s">
  <span class="icon">ℹ️</span><b>О проекте</b>
  <div class="desc">Источники данных, модели, метрики, библиография</div>
</a>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ==================================================================
# О ПРОЕКТЕ
# ==================================================================
ABOUT_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>О проекте — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .about-block {
    margin: 20px 0;
    padding: 20px 24px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
    color: var(--text-1);
    font-size: 14px;
    line-height: 1.8;
  }
  .about-block h2 {
    margin: 0 0 12px 0;
    font-size: 17px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .about-block b { color: var(--text-0); }
  .about-block ul { padding-left: 22px; margin: 8px 0; }
  .about-block ul li { margin: 4px 0; }
  .about-block code {
    background: rgba(120,160,255,0.08); padding: 2px 6px;
    border-radius: 4px; font-family: 'JetBrains Mono', monospace;
    font-size: 12px; color: var(--accent);
  }
</style>
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>О проекте</h1>
<div class="sub">Источники данных, модели, метрики, библиография</div>

<div class="about-block">
  <h2>🎯 Назначение</h2>
  <p>
    <b>weather-msk</b> — учебно-исследовательский проект: сравнение прогнозов
    нескольких численных моделей атмосферы между собой и с фактическими данными.
    Используется для верификации моделей, анализа синоптических ситуаций
    и изучения методов прогноза погоды.
  </p>
</div>

<div class="about-block">
  <h2>🌐 Источники данных</h2>
  <ul>
    <li><b>Open-Meteo API</b> — GFS, ECMWF, ICON, ERA5, архив прогнозов</li>
    <li><b>ERA5 reanalysis</b> (ECMWF) — фактические данные для верификации</li>
    <li><b>Meteostat</b> — данные ближайших метеостанций (если доступны)</li>
    <li><b>NOAA / CPC</b> — климатические индексы (ONI, SST Niño 3.4)</li>
  </ul>
</div>

<div class="about-block">
  <h2>🧮 Модели</h2>
  <ul>
    <li><b>GFS</b> (NOAA, США) — глобальная модель, ~13 км</li>
    <li><b>ECMWF</b> (Европа) — эталонная модель, ~9–25 км</li>
    <li><b>ICON</b> (DWD, Германия) — ~11 км</li>
  </ul>
</div>

<div class="about-block">
  <h2>📊 Метрики</h2>
  <ul>
    <li><b>MAE</b> — средняя абсолютная ошибка</li>
    <li><b>RMSE</b> — среднеквадратичная ошибка</li>
    <li><b>Bias</b> — среднее смещение (прогноз − факт)</li>
    <li><b>Корреляция, R², MAPE</b> — статистические показатели</li>
    <li><b>Матрица 2×2</b> — Hits / Misses / False alarms / Correct negatives</li>
    <li><b>Критерии Хандожко</b> — p, H, τ, v, Q, S</li>
  </ul>
</div>

<div class="about-block">
  <h2>📖 Библиография</h2>
  <p>
    Все использованные источники собраны на странице
    <a href="/bibliography" style="color:var(--accent);text-decoration:none;font-weight:600;">📖 Библиография</a>:
    Богаткин, Волобуева, Хандожко, Хромов, Холтон, Кашкин, Chuvieco и др.
  </p>
</div>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ==================================================================
# КАРТА
# ==================================================================
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

<a class="back" href="/">← Главная</a>
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

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ==================================================================
# УЧЕБНЫЕ ПРИМЕРЫ
# ==================================================================
TEACHING_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Учебные примеры — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .topic-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    gap: 16px; margin: 20px 0;
  }
  .topic-card {
    padding: 20px 22px; border-radius: 16px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border); backdrop-filter: blur(14px);
    transition: all 0.25s;
  }
  .topic-card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--card-shadow);
    transform: translateY(-2px);
  }
  .topic-card h3 {
    margin: 0 0 8px 0; font-size: 17px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .topic-card .source {
    font-size: 11px; color: var(--text-2); margin-bottom: 10px;
    font-family: 'JetBrains Mono', monospace;
  }
  .topic-card p {
    color: var(--text-1); font-size: 13px; line-height: 1.6;
    margin: 0 0 12px 0;
  }
  .topic-card .formula {
    background: rgba(15,21,36,0.5); padding: 10px 14px;
    border-radius: 8px; border: 1px solid var(--border);
    font-family: 'JetBrains Mono', monospace; font-size: 12px;
    color: var(--accent); margin: 10px 0; overflow-x: auto;
  }
  .topic-card .links {
    display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px;
  }
  .topic-card .links a {
    padding: 6px 12px; border-radius: 8px; text-decoration: none;
    font-size: 12px; font-weight: 600;
    background: rgba(77,171,255,0.10);
    border: 1px solid rgba(77,171,255,0.3);
    color: var(--accent);
    transition: all 0.2s;
  }
  .topic-card .links a:hover {
    background: rgba(77,171,255,0.20);
    border-color: var(--border-hover);
  }
</style>
</head>
<body>

<a class="back" href="/theory">← Теория</a>
<h1>📚 Учебные примеры и методы</h1>
<div class="sub">По учебнику О. Г. Богаткина «Авиационные прогнозы погоды» (СПб, 2010)</div>

<div class="topic-grid">

  <div class="topic-card fade-in">
    <h3>🌡 Прогноз минимальной температуры</h3>
    <div class="source">Богаткин, гл. 5.2, с. 114–118</div>
    <p>Методы А. С. Зверева, М. Е. Берлянда, Михельсона, Куприянова.
       Учёт облачности и ветра через коэффициент <i>m</i>.</p>
    <div class="formula">T<sub>мин</sub> = T<sub>13</sub> − 0.5·(T<sub>13</sub> − T<sub>d13</sub>) − 6</div>
    <div class="formula">T<sub>мин</sub> = T<sub>макс</sub> − m·A</div>
    <div class="links">
      <a href="/forecast/gfs/tushino">📊 Таблица</a>
      <a href="/point-chart?lat=55.85&lon=37.44&name=Тушино">📈 График</a>
    </div>
  </div>

  <div class="topic-card fade-in">
    <h3>💨 Прогноз ветра у земли</h3>
    <div class="source">Богаткин, гл. 6.3, с. 131–138</div>
    <p>Метод А. С. Зверева (по градиенту давления), метод О. Г. Богаткина
       (по барической тенденции), определение порывов.</p>
    <div class="formula">U = 2·B − 1   (шкала Бофорта)</div>
    <div class="formula">U<sub>пор</sub> = U<sub>ср</sub> + 0.5·U<sub>ср</sub></div>
    <div class="links">
      <a href="/forecast/gfs/tushino">📊 Таблица</a>
      <a href="/point-chart?lat=55.85&lon=37.44&name=Тушино">📈 Ветер</a>
    </div>
  </div>

  <div class="topic-card fade-in">
    <h3>☁️ Прогноз низкой облачности</h3>
    <div class="source">Богаткин, гл. 8.3, с. 161–172</div>
    <p>Формулы Ипполитова, Ферреля, метод Е. И. Гоголевой, ГАМЦ,
       В. М. Ярковой, прогноз облачности ниже 400 м в Красноярске.</p>
    <div class="formula">H = 122·(T − T<sub>d</sub>)<sub>0</sub>   (Феррель)</div>
    <div class="formula">H = 24·(100 − R)   (Ипполитов)</div>
    <div class="links">
      <a href="/forecast/gfs/tushino">📊 Таблица</a>
      <a href="/point-synoptic?lat=55.85&lon=37.44&name=Тушино">🌡 Синоптика</a>
    </div>
  </div>

  <div class="topic-card fade-in">
    <h3>🌫 Прогноз туманов</h3>
    <div class="source">Богаткин, гл. 9, с. 176–202</div>
    <p>Методы Н. В. Петренко, Б. В. Кирюхина, А. С. Зверева, Д. Н. Лаврищева,
       Р. М. Меджитова. Радиационные и адвективные туманы. Морозные туманы.</p>
    <div class="formula">T<sub>т</sub> = T<sub>d</sub> − ΔT<sub>d</sub></div>
    <div class="formula">S<sub>м</sub> = 60 / q<sup>0.5</sup></div>
    <div class="links">
      <a href="/aviation/gfs/tushino">✈️ Авиация</a>
      <a href="/alt-verify/tushino?phenomenon=fog">📋 Матрица (туман)</a>
    </div>
  </div>

  <div class="topic-card fade-in">
    <h3>⛈ Прогноз гроз и града</h3>
    <div class="source">Богаткин, гл. 10, с. 203–238</div>
    <p>Метод частицы, методы Н. В. Лебедевой, Бейли, Вайтинга, Фауста,
       Г. Д. Решетова, И. А. Славина, Кокса. Прогноз града и смерчей.</p>
    <div class="formula">K = 2·T<sub>850</sub> − T<sub>500</sub> − D<sub>850</sub> − D<sub>700</sub>   (Вайтинг)</div>
    <div class="formula">A ≥ 0   →   гроза   (Фатеев)</div>
    <div class="links">
      <a href="/aviation/gfs/tushino">✈️ Авиация</a>
      <a href="/alt-verify/tushino?phenomenon=thunder">📋 Матрица (гроза)</a>
    </div>
  </div>

  <div class="topic-card fade-in">
    <h3>🌧 Прогноз осадков и видимости</h3>
    <div class="source">Богаткин, гл. 11–12, с. 239–263</div>
    <p>Моросящие, обложные, ливневые осадки. Гололёд и гололедица.
       Прогноз видимости в туманах, осадках, метелях, пыльных бурях.</p>
    <div class="formula">S<sub>м</sub> = 2.3·10<sup>4</sup> / (r·q)</div>
    <div class="formula">L = T<sub>инв</sub> − T<sub>0</sub> − (0.0778·D² + 0.67·D)</div>
    <div class="links">
      <a href="/forecast/gfs/tushino">📊 Таблица</a>
      <a href="/verify/tushino">✅ Проверка</a>
    </div>
  </div>

</div>

""" + render_biblio_ref("aviation", "гл. 5–12") + """
""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ==================================================================
# ТРОПОПАУЗА
# ==================================================================
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

<a class="back" href="/theory">← Теория</a>
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
""" + COMMON_JS + render_top_controls() + render_legend("synoptic") + """
</body>
</html>
"""


# ==================================================================
# ПРОВЕРКА МОДЕЛЕЙ
# ==================================================================
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

<a class="back" href="/analysis">← Анализ</a>
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

""" + COMMON_JS + render_top_controls() + render_legend("analysis") + """
</body>
</html>
"""


# ==================================================================
# ИСТОРИЯ ОШИБОК
# ==================================================================
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

<a class="back" href="/verify/{{ station_key }}">← К проверке</a>
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

""" + COMMON_JS + render_top_controls() + render_legend("analysis") + """
</body>
</html>
"""


# ==================================================================
# РАСШИРЕННЫЙ АНАЛИЗ
# ==================================================================
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

<a class="back" href="/analysis">← Анализ</a>
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

""" + COMMON_JS + render_top_controls() + render_legend("analysis") + """
</body>
</html>
"""


# ==================================================================
# АВИАЦИОННЫЕ ПРОГНОЗЫ
# ==================================================================
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

<a class="back" href="{% if is_point %}/search{% else %}/theory{% endif %}">
  ← {% if is_point %}Поиск{% else %}Теория{% endif %}
</a>
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
""" + COMMON_JS + render_top_controls() + render_legend("synoptic") + """
</body>
</html>
"""


# ==================================================================
# СРАВНЕНИЕ МАТРИЦ ПО ВСЕМ ЯВЛЕНИЯМ
# ==================================================================
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

<a class="back" href="/theory">← Теория</a>
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

""" + COMMON_JS + render_top_controls() + render_legend("matrices") + """
</body>
</html>
"""


# ==================================================================
# ГРАФИК СРАВНЕНИЯ МОДЕЛЕЙ
# ==================================================================
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

<a class="back" href="{% if is_point %}/search{% else %}/forecast{% endif %}">
  ← {% if is_point %}Поиск{% else %}Прогноз{% endif %}
</a>
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

""" + COMMON_JS + render_top_controls() + render_legend("forecast") + """
</body>
</html>
"""


# ==================================================================
# СВОДКА ЯВЛЕНИЙ
# ==================================================================
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

""" + COMMON_JS + render_top_controls() + render_legend("analysis") + """
</body>
</html>
"""

# ==================================================================
# СТРАНИЦА МОДЕЛИ
# ==================================================================
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

<a class="card fade-in" href="/aviation/{{ model }}/{{ first_station }}" style="background:rgba(255,181,71,0.10);">
  <span class="icon">✈️</span><b>Авиационный прогноз</b>
  <div class="desc">K (Вайтинг), LI, CAPE, туман по Кирюхину</div>
</a>

<a class="card fade-in" href="/synoptic/{{ model }}/{{ first_station }}" style="background:rgba(255,84,112,0.10);">
  <span class="icon">🌡</span><b>Синоптика по уровням</b>
  <div class="desc">Профиль T, θ, RH на 925–300 гПа</div>
</a>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ==================================================================
# ТАБЛИЦА ПРОГНОЗА
# ==================================================================
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

<a class="back" href="{% if is_point %}/search{% else %}/model/{{ model }}{% endif %}">
  ← {% if is_point %}Поиск{% else %}{{ model_name }}{% endif %}
</a>
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

""" + COMMON_JS + render_top_controls() + render_legend("forecast") + """
</body>
</html>
"""


# ==================================================================
# ТЕКСТОВЫЙ ПРОГНОЗ
# ==================================================================
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

<a class="back" href="{% if is_point %}/forecast/point?lat={{ lat }}&lon={{ lon }}&name={{ station }}&model={{ model }}{% else %}/forecast/{{ model }}/{{ station_key }}{% endif %}">
  ← Таблица
</a>
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

""" + COMMON_JS + render_top_controls() + render_legend("forecast") + """
</body>
</html>
"""


# ==================================================================
# ПОИСК ТОЧКИ
# ==================================================================
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

<a class="back" href="/forecast">← Прогноз</a>
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

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ==================================================================
# ШАБЛОН ТОЧКИ (заглушка)
# ==================================================================
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


# ==================================================================
# СИНОПТИКА ПО УРОВНЯМ
# ==================================================================
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

<a class="back" href="{% if is_point %}/search{% else %}/forecast{% endif %}">
  ← {% if is_point %}Поиск{% else %}Прогноз{% endif %}
</a>
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
""" + COMMON_JS + render_top_controls() + render_legend("synoptic") + """
</body>
</html>
"""


# ==================================================================
# КЛИМАТИЧЕСКИЕ ИНДЕКСЫ
# ==================================================================
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

<a class="back" href="/theory">← Теория</a>
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
""" + COMMON_JS + render_top_controls() + render_legend("climate") + """
</body>
</html>
"""


# ==================================================================
# МАТРИЦА АЛЬТЕРНАТИВНЫХ ПРОГНОЗОВ
# ==================================================================
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

<a class="back" href="/theory">← Теория</a>
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

""" + COMMON_JS + render_top_controls() + render_legend("matrices") + """
</body>
</html>
"""


# ==================================================================
# ТЕКСТОВЫЙ ПРОГНОЗ
# ==================================================================
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

<a class="back" href="{% if is_point %}/forecast/point?lat={{ lat }}&lon={{ lon }}&name={{ station }}&model={{ model }}{% else %}/forecast/{{ model }}/{{ station_key }}{% endif %}">
  ← Таблица
</a>
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

""" + COMMON_JS + render_top_controls() + render_legend("forecast") + """
</body>
</html>
"""


# ==================================================================
# ПОИСК ТОЧКИ
# ==================================================================
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

<a class="back" href="/forecast">← Прогноз</a>
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

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ==================================================================
# ШАБЛОН ТОЧКИ (заглушка)
# ==================================================================
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


# ==================================================================
# СИНОПТИКА ПО УРОВНЯМ
# ==================================================================
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

<a class="back" href="{% if is_point %}/search{% else %}/forecast{% endif %}">
  ← {% if is_point %}Поиск{% else %}Прогноз{% endif %}
</a>
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
""" + COMMON_JS + render_top_controls() + render_legend("synoptic") + """
</body>
</html>
"""


# ==================================================================
# КЛИМАТИЧЕСКИЕ ИНДЕКСЫ
# ==================================================================
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

<a class="back" href="/theory">← Теория</a>
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
""" + COMMON_JS + render_top_controls() + render_legend("climate") + """
</body>
</html>
"""


# ==================================================================
# БИБЛИОГРАФИЯ
# ==================================================================
BIBLIOGRAPHY_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Библиография — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .toc {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 20px 0 28px 0;
    padding: 14px 18px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    backdrop-filter: blur(14px);
  }
  .toc a {
    padding: 6px 12px;
    border-radius: 8px;
    text-decoration: none;
    font-size: 13px;
    font-weight: 500;
    background: rgba(77, 171, 255, 0.08);
    border: 1px solid rgba(77, 171, 255, 0.2);
    color: var(--accent);
    transition: all 0.2s;
  }
  .toc a:hover {
    background: rgba(77, 171, 255, 0.15);
    border-color: var(--border-hover);
  }

  .biblio-section {
    margin: 32px 0;
    padding: 22px 24px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
    scroll-margin-top: 20px;
  }
  .biblio-section h2 {
    margin: 0 0 18px 0;
    font-size: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .biblio-section h2 .icon {
    -webkit-text-fill-color: initial;
    color: var(--accent);
  }

  .biblio-item {
    margin: 14px 0;
    padding: 16px 18px;
    background: rgba(15, 21, 36, 0.5);
    border: 1px solid var(--border);
    border-radius: 12px;
    transition: all 0.2s;
  }
  .biblio-item:hover {
    border-color: var(--border-hover);
  }
  .biblio-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-0);
    margin-bottom: 4px;
    line-height: 1.4;
  }
  .biblio-authors {
    color: var(--text-1);
    font-size: 13px;
    margin-bottom: 4px;
  }
  .biblio-source {
    color: var(--text-2);
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 10px;
  }
  .biblio-note {
    color: var(--text-1);
    font-size: 13px;
    line-height: 1.6;
    padding-top: 10px;
    border-top: 1px solid rgba(120, 160, 255, 0.08);
  }
  .biblio-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 10px;
  }
  .biblio-tag {
    padding: 3px 9px;
    font-size: 11px;
    border-radius: 6px;
    background: rgba(77, 171, 255, 0.1);
    border: 1px solid rgba(77, 171, 255, 0.25);
    color: var(--accent);
    font-family: 'JetBrains Mono', monospace;
  }
</style>
</head>
<body>

<a class="back" href="/theory">← Теория</a>
<h1>📖 Библиография</h1>
<div class="sub">Источники, использованные в разделах сайта</div>

<div class="toc">
  {% for key, topic in bibliography.items() %}
    <a href="#{{ key }}">{{ topic.icon }} {{ topic.title }}</a>
  {% endfor %}
</div>

{% for key, topic in bibliography.items() %}
<div class="biblio-section" id="{{ key }}">
  <h2><span class="icon">{{ topic.icon }}</span>{{ topic.title }}</h2>

  {% for item in topic.sources %}
  <div class="biblio-item">
    <div class="biblio-title">«{{ item.title }}»{% if item.edition %} — {{ item.edition }}{% endif %}</div>
    <div class="biblio-authors">{{ item.authors }}</div>
    <div class="biblio-source">
      {{ item.source }}{% if item.year %}, {{ item.year }}{% endif %}{% if item.pages %}. {{ item.pages }}{% endif %}
    </div>
    {% if item.note %}
      <div class="biblio-note">{{ item.note }}</div>
    {% endif %}
    {% if item.tags %}
      <div class="biblio-tags">
        {% for tag in item.tags %}
          <span class="biblio-tag">{{ tag }}</span>
        {% endfor %}
      </div>
    {% endif %}
  </div>
  {% endfor %}
</div>
{% endfor %}

""" + COMMON_JS + render_top_controls() + render_legend("bibliography") + """
</body>
</html>
"""


# ==================================================================
# ТЕОРИЯ: МЕТОДЫ ПРОГНОЗА
# ==================================================================
THEORY_METHODS_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Методы прогноза — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .method-block {
    margin: 24px 0;
    padding: 22px 24px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
  }
  .method-block h2 {
    margin: 0 0 14px 0;
    font-size: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .method-block p {
    color: var(--text-1);
    font-size: 14px;
    line-height: 1.7;
    margin: 10px 0;
  }
  .formula {
    background: rgba(15, 21, 36, 0.6);
    padding: 14px 18px;
    border-radius: 10px;
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--accent);
    margin: 14px 0;
    overflow-x: auto;
    line-height: 1.8;
  }
  .method-block ul {
    color: var(--text-1);
    font-size: 14px;
    line-height: 1.8;
    padding-left: 22px;
  }
  .method-block ul li { margin: 6px 0; }
  .method-block ul li b { color: var(--text-0); }
</style>
</head>
<body>

<a class="back" href="/theory">← Теория</a>
<h1>📐 Методы прогноза</h1>
<div class="sub">Изоэнтропический анализ · потенциальная завихрённость · PV-аномалии</div>

<div class="method-block">
  <h2>🌀 Изоэнтропический анализ</h2>
  <p>
    <b>Идея.</b> Адиабатические процессы в атмосфере сохраняют потенциальную
    температуру θ. Движение воздуха происходит преимущественно вдоль
    изоэнтропических поверхностей (θ = const). Анализ на этих поверхностях
    выявляет динамически активные зоны, невидимые на изобарических картах.
  </p>

  <div class="formula">
θ = T · (p₀ / p)^(R/cp)
  </div>

  <p>
    где T — температура (K), p — давление (гПа), p₀ = 1000 гПа,
    R/cp ≈ 0.286 — отношение газовой постоянной к удельной теплоёмкости.
  </p>

  <p>
    <b>Применение.</b> Изоэнтропические карты используют для:
  </p>
  <ul>
    <li>выявления <b>складок тропопаузы</b> (где PV-аномалии опускаются в тропосферу);</li>
    <li>диагностики <b>струйных течений</b> и зон сильного ветра;</li>
    <li>анализа <b>фронтальных зон</b> — на изоэнтропах фронт виден как сгущение изолиний θ;</li>
    <li>прогноза <b>циклогенеза</b> — по аномалиям PV на 300–330 K.</li>
  </ul>
</div>

<div class="method-block">
  <h2>📊 Потенциальная завихрённость (PV)</h2>
  <p>
    <b>Ertel PV</b> — индикатор динамической устойчивости. Сохраняется при
    адиабатических процессах, что делает его идеальным трассером.
  </p>

  <div class="formula">
PV = −g · (ζ + f) · (∂θ / ∂p)
  </div>

  <p>
    где g = 9.81 м/с², ζ — относительная завихрённость, f = 2Ω·sin(φ) —
    параметр Кориолиса, θ — потенциальная температура, p — давление (Па).
  </p>

  <p>
    <b>Единица измерения:</b> 1 PVU = 10⁻⁶ м²·К·кг⁻¹·с⁻¹.
  </p>

  <p>
    <b>Пороги:</b>
  </p>
  <ul>
    <li><b>&lt; 0.5 PVU</b> — тропосферный воздух;</li>
    <li><b>2 PVU</b> — динамическая тропопауза (стандарт WMO);</li>
    <li><b>&gt; 4 PVU</b> — стратосферный воздух, вторгшийся в тропосферу.</li>
  </ul>

  <p>
    <b>PV-аномалии</b> — области с высоким PV, опустившиеся в тропосферу —
    связаны с:
  </p>
  <ul>
    <li>складками тропопаузы;</li>
    <li>струйными течениями на их периферии;</li>
    <li>циклогенезом (положительная PV-аномалия);</li>
    <li>турбулентностью в верхней тропосфере.</li>
  </ul>
</div>

<div class="method-block">
  <h2>🔬 Синоптический метод</h2>
  <p>
    Комплексный анализ приземных и высотных карт: приземное давление,
    барическая тенденция, геопотенциал H₅₀₀, адвекция температуры,
    фронтальные разделы, струйное течение.
  </p>

  <p>
    <b>Уровни анализа:</b>
  </p>
  <ul>
    <li><b>925 гПа</b> (~800 м) — приземный слой, инверсии, туманы;</li>
    <li><b>850 гПа</b> (~1500 м) — пограничный слой, адвекция тепла/холода;</li>
    <li><b>700 гПа</b> (~3000 м) — влагосодержание, слои конвекции;</li>
    <li><b>500 гПа</b> (~5500 м) — ведущий поток, гребни и ложбины;</li>
    <li><b>300 гПа</b> (~9000 м) — струйное течение, зона тропопаузы.</li>
  </ul>
</div>

""" + render_biblio_ref("synoptic", "гл. 3–4") + """
""" + COMMON_JS + render_top_controls() + render_legend("synoptic") + """
</body>
</html>
"""


# ==================================================================
# ТЕОРИЯ: МАТРИЦЫ И КРИТЕРИИ
# ==================================================================
THEORY_MATRICES_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Матрицы и критерии — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .crit-block {
    margin: 24px 0;
    padding: 22px 24px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
  }
  .crit-block h2 {
    margin: 0 0 14px 0;
    font-size: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .crit-block p {
    color: var(--text-1);
    font-size: 14px;
    line-height: 1.7;
  }
  .formula {
    background: rgba(15, 21, 36, 0.6);
    padding: 14px 18px;
    border-radius: 10px;
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--accent);
    margin: 14px 0;
    overflow-x: auto;
    line-height: 1.8;
  }

  .matrix-2x2 {
    display: grid;
    grid-template-columns: 100px 1fr 1fr;
    gap: 6px;
    margin: 20px 0;
    max-width: 520px;
  }
  .matrix-cell {
    padding: 16px 12px;
    text-align: center;
    border-radius: 10px;
    font-family: 'JetBrains Mono', monospace;
  }
  .matrix-cell.header {
    background: transparent;
    color: var(--text-2);
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .matrix-cell.axis {
    background: transparent;
    color: var(--text-2);
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 10px;
  }
  .matrix-cell.hits {
    background: rgba(0, 229, 160, 0.15);
    color: #00e5a0;
    border: 1px solid rgba(0, 229, 160, 0.3);
  }
  .matrix-cell.correct {
    background: rgba(77, 171, 255, 0.12);
    color: #4dabff;
    border: 1px solid rgba(77, 171, 255, 0.25);
  }
  .matrix-cell.misses {
    background: rgba(255, 84, 112, 0.15);
    color: #ff5470;
    border: 1px solid rgba(255, 84, 112, 0.3);
  }
  .matrix-cell.false {
    background: rgba(255, 181, 71, 0.15);
    color: #ffb547;
    border: 1px solid rgba(255, 181, 71, 0.3);
  }
  .matrix-cell .num { font-size: 22px; font-weight: 700; display: block; }
  .matrix-cell .lbl { font-size: 10px; opacity: 0.8; display: block; margin-top: 2px; }

  .crit-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin-top: 14px;
  }
  .crit-table th {
    text-align: left;
    padding: 10px 12px;
    color: var(--text-2);
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  .crit-table td {
    padding: 10px 12px;
    border-bottom: 1px solid rgba(120, 160, 255, 0.06);
    color: var(--text-1);
  }
  .crit-table tr:hover td { background: rgba(77, 171, 255, 0.05); }
  .crit-table td.formula-cell {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--accent);
  }
  .crit-table td.name { color: var(--text-0); font-weight: 600; }
</style>
</head>
<body>

<a class="back" href="/theory">← Теория</a>
<h1>📋 Матрицы и критерии успешности</h1>
<div class="sub">Матрица сопряжённости 2×2 · критерии Хандожко · интерпретация</div>

<div class="crit-block">
  <h2>📋 Матрица сопряжённости (2×2)</h2>
  <p>
    Основной инструмент верификации альтернативных прогнозов
    («явление будет / не будет»). Сопоставляет прогноз с фактом по 4 категориям.
  </p>

  <div class="matrix-2x2">
    <div class="matrix-cell header"></div>
    <div class="matrix-cell header">Факт: ДА</div>
    <div class="matrix-cell header">Факт: НЕТ</div>

    <div class="matrix-cell axis">Прогноз: ДА</div>
    <div class="matrix-cell hits">
      <span class="num">a</span>
      <span class="lbl">Hits</span>
    </div>
    <div class="matrix-cell false">
      <span class="num">b</span>
      <span class="lbl">False alarms</span>
    </div>

    <div class="matrix-cell axis">Прогноз: НЕТ</div>
    <div class="matrix-cell misses">
      <span class="num">c</span>
      <span class="lbl">Misses</span>
    </div>
    <div class="matrix-cell correct">
      <span class="num">d</span>
      <span class="lbl">Correct negatives</span>
    </div>
  </div>

  <p>
    где <b>a</b> — попадания (прогноз ДА / факт ДА),
    <b>b</b> — ложные тревоги (прогноз ДА / факт НЕТ),
    <b>c</b> — пропуски (прогноз НЕТ / факт ДА),
    <b>d</b> — правильные отрицания (прогноз НЕТ / факт НЕТ).
  </p>
</div>

<div class="crit-block">
  <h2>📊 Критерии Хандожко</h2>
  <p>
    Формулы для оценки качества альтернативных прогнозов
    (Хандожко Л. А., «Экономическая эффективность метеорологических прогнозов», Обнинск, 2008).
  </p>

  <table class="crit-table">
    <thead>
      <tr>
        <th>Критерий</th>
        <th>Формула</th>
        <th>Интерпретация</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="name">p — общая оправдываемость</td>
        <td class="formula-cell">(a + d) / (a + b + c + d)</td>
        <td>Доля всех правильных прогнозов. p → 1 — идеал.</td>
      </tr>
      <tr>
        <td class="name">H — точность попаданий</td>
        <td class="formula-cell">a / (a + b)</td>
        <td>Насколько оправданы «ДА»-прогнозы. H → 1 — нет ложных тревог.</td>
      </tr>
      <tr>
        <td class="name">τ — критерий Обухова (полнота)</td>
        <td class="formula-cell">a / (a + c)</td>
        <td>Доля пойманных событий. τ → 1 — нет пропусков.</td>
      </tr>
      <tr>
        <td class="name">v — критерий Хайдке</td>
        <td class="formula-cell">(a − b) / (a + b)</td>
        <td>Баланс попаданий и ложных тревог. v ∈ [−1, 1].</td>
      </tr>
      <tr>
        <td class="name">Q — критерий Пирси-Обухова</td>
        <td class="formula-cell">(a·d − b·c) / ((a+c)(b+d))</td>
        <td>Корреляция прогноза и факта. Q → 1 — идеал.</td>
      </tr>
      <tr>
        <td class="name">S — критерий Хайдке</td>
        <td class="formula-cell">p − v</td>
        <td>Компромисс между p и v. S → 1 — идеал.</td>
      </tr>
      <tr>
        <td class="name">A — критерий успешности</td>
        <td class="formula-cell">(a + d) / (a + b + c + d)</td>
        <td>Синоним p. Используется в некоторых источниках.</td>
      </tr>
      <tr>
        <td class="name">F1 — F-мера</td>
        <td class="formula-cell">2·a / (2a + b + c)</td>
        <td>Гармоническое среднее precision и recall. F1 → 1 — идеал.</td>
      </tr>
    </tbody>
  </table>
</div>

<div class="crit-block">
  <h2>🎯 Пороги интерпретации</h2>
  <table class="crit-table">
    <thead>
      <tr>
        <th>Критерий</th>
        <th>Плохо</th>
        <th>Средне</th>
        <th>Хорошо</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="name">p</td>
        <td>&lt; 0.7</td>
        <td>0.7 – 0.9</td>
        <td>&gt; 0.9</td>
      </tr>
      <tr>
        <td class="name">H</td>
        <td>&lt; 0.4</td>
        <td>0.4 – 0.6</td>
        <td>&gt; 0.6</td>
      </tr>
      <tr>
        <td class="name">τ</td>
        <td>&lt; 0.4</td>
        <td>0.4 – 0.6</td>
        <td>&gt; 0.6</td>
      </tr>
      <tr>
        <td class="name">v</td>
        <td>&lt; 0</td>
        <td>0 – 0.3</td>
        <td>&gt; 0.3</td>
      </tr>
      <tr>
        <td class="name">Q</td>
        <td>&lt; 0.2</td>
        <td>0.2 – 0.5</td>
        <td>&gt; 0.5</td>
      </tr>
      <tr>
        <td class="name">F1</td>
        <td>&lt; 0.3</td>
        <td>0.3 – 0.5</td>
        <td>&gt; 0.5</td>
      </tr>
    </tbody>
  </table>

  <p style="margin-top:16px;font-size:13px;">
    Пороги — ориентировочные, зависят от явления. Для редких явлений
    (гроза, туман) p легко завышается за счёт «правильных отрицаний»,
    поэтому смотреть надо в первую очередь на <b>H</b>, <b>τ</b> и <b>F1</b>.
  </p>
</div>

<div class="crit-block">
  <h2>⚖️ Сравнение моделей</h2>
  <p>
    Для сравнения моделей по матрицам переходи на страницу
    <a href="/compare-matrices/tushino" style="color:var(--accent);text-decoration:none;font-weight:600;">🔀 Сравнить модели по матрицам</a>
    — там для каждого явления строится матрица 2×2 по каждой модели
    и считается набор критериев.
  </p>
  <p>
    Для одной модели — страница
    <a href="/alt-verify/tushino" style="color:var(--accent);text-decoration:none;font-weight:600;">📋 Матрица альтернативных прогнозов</a>.
  </p>
</div>

""" + render_biblio_ref("matrices", "гл. 2–3") + """
""" + COMMON_JS + render_top_controls() + render_legend("matrices") + """
</body>
</html>
"""


# ==================================================================
# ТЕОРИЯ: ИНДЕКСЫ И ЯВЛЕНИЯ
# ==================================================================
THEORY_INDICES_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Индексы неустойчивости — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .idx-block {
    margin: 24px 0;
    padding: 22px 24px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
  }
  .idx-block h2 {
    margin: 0 0 14px 0;
    font-size: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .idx-block p {
    color: var(--text-1);
    font-size: 14px;
    line-height: 1.7;
  }
  .formula {
    background: rgba(15, 21, 36, 0.6);
    padding: 14px 18px;
    border-radius: 10px;
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--accent);
    margin: 14px 0;
    overflow-x: auto;
    line-height: 1.8;
  }
  .idx-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin-top: 14px;
  }
  .idx-table th {
    text-align: left;
    padding: 10px 12px;
    color: var(--text-2);
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  .idx-table td {
    padding: 10px 12px;
    border-bottom: 1px solid rgba(120, 160, 255, 0.06);
    color: var(--text-1);
  }
  .idx-table tr:hover td { background: rgba(77, 171, 255, 0.05); }
  .idx-table td.name { color: var(--text-0); font-weight: 600; }
  .idx-table td.good { color: #00e5a0; }
  .idx-table td.warn { color: #ffb547; }
  .idx-table td.bad  { color: #ff5470; }
</style>
</head>
<body>

<a class="back" href="/theory">← Теория</a>
<h1>⚡ Индексы неустойчивости</h1>
<div class="sub">LI · K-Index · CAPE · ΔT(850−500) · сдвиг ветра · интерпретация</div>

<div class="idx-block">
  <h2>⚡ K-Index (индекс Вайтинга)</h2>
  <p>
    Интегральный индекс конвективной неустойчивости. Учитывает
    вертикальный градиент температуры и влагосодержание в слое 850–500 гПа.
  </p>

  <div class="formula">
K = (T₈₅₀ − T₅₀₀) + Td₈₅₀ − (T₇₀₀ − Td₇₀₀)
  </div>

  <table class="idx-table">
    <thead>
      <tr>
        <th>Значение K</th>
        <th>Интерпретация</th>
        <th>Вероятность грозы</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">&lt; 15</td><td>Устойчиво</td><td class="good">0 %</td></tr>
      <tr><td class="name">15 – 20</td><td>Слабая неустойчивость</td><td class="good">до 20 %</td></tr>
      <tr><td class="name">20 – 25</td><td>Умеренная</td><td class="warn">20 – 40 %</td></tr>
      <tr><td class="name">25 – 30</td><td>Сильная</td><td class="warn">40 – 60 %</td></tr>
      <tr><td class="name">30 – 35</td><td>Очень сильная</td><td class="bad">60 – 80 %</td></tr>
      <tr><td class="name">&gt; 35</td><td>Экстремальная, грозы с градом</td><td class="bad">&gt; 80 %</td></tr>
    </tbody>
  </table>
</div>

<div class="idx-block">
  <h2>📈 Lifted Index (LI)</h2>
  <p>
    Разность температур между частицей, поднятой адиабатически до 500 гПа,
    и окружающей средой на том же уровне.
  </p>

  <div class="formula">
LI = T₅₀₀(окружение) − T₅₀₀(частица)
  </div>

  <table class="idx-table">
    <thead>
      <tr>
        <th>LI</th>
        <th>Интерпретация</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">&gt; +2</td><td class="good">Устойчиво</td></tr>
      <tr><td class="name">0 … +2</td><td class="good">Слабая неустойчивость</td></tr>
      <tr><td class="name">−2 … 0</td><td class="warn">Умеренная</td></tr>
      <tr><td class="name">−4 … −2</td><td class="warn">Сильная</td></tr>
      <tr><td class="name">−6 … −4</td><td class="bad">Очень сильная</td></tr>
      <tr><td class="name">&lt; −6</td><td class="bad">Экстремальная</td></tr>
    </tbody>
  </table>
</div>

<div class="idx-block">
  <h2>🔋 CAPE</h2>
  <p>
    Convective Available Potential Energy — доступная потенциальная
    энергия конвекции. Площадь на диаграмме T–ln p между кривой
    состояния частицы и кривой стратификации в слое положительной плавучести.
  </p>

  <div class="formula">
CAPE = g · ∫ (T_ч − T_окр) / T_окр · dz
  </div>

  <table class="idx-table">
    <thead>
      <tr>
        <th>CAPE, Дж/кг</th>
        <th>Интерпретация</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">&lt; 300</td><td class="good">Слабая конвекция</td></tr>
      <tr><td class="name">300 – 800</td><td class="good">Умеренная</td></tr>
      <tr><td class="name">800 – 1500</td><td class="warn">Сильная</td></tr>
      <tr><td class="name">1500 – 2500</td><td class="bad">Очень сильная</td></tr>
      <tr><td class="name">&gt; 2500</td><td class="bad">Экстремальная</td></tr>
    </tbody>
  </table>
</div>

<div class="idx-block">
  <h2>🌡 ΔT(850 − 500)</h2>
  <p>
    Грубый индикатор конвекции. Разность температур между 850 и 500 гПа.
  </p>

  <div class="formula">
ΔT = T₈₅₀ − T₅₀₀
  </div>

  <table class="idx-table">
    <thead>
      <tr>
        <th>ΔT, °C</th>
        <th>Интерпретация</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">&lt; 20</td><td class="good">Устойчиво</td></tr>
      <tr><td class="name">20 – 24</td><td class="good">Слабая</td></tr>
      <tr><td class="name">24 – 28</td><td class="warn">Умеренная</td></tr>
      <tr><td class="name">28 – 32</td><td class="bad">Сильная</td></tr>
      <tr><td class="name">&gt; 32</td><td class="bad">Экстремальная</td></tr>
    </tbody>
  </table>
</div>

<div class="idx-block">
  <h2>💨 Сдвиг ветра (850 → 300 гПа)</h2>
  <p>
    Векторная разность ветра между уровнями. Важен для организации
    конвекции: сильный сдвиг + высокая CAPE = угроза смерчей.
  </p>

  <div class="formula">
ΔV = √[(u₃₀₀ − u₈₅₀)² + (v₃₀₀ − v₈₅₀)²]
  </div>

  <table class="idx-table">
    <thead>
      <tr>
        <th>Сдвиг, м/с</th>
        <th>Интерпретация</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">&lt; 10</td><td>Слабый</td></tr>
      <tr><td class="name">10 – 15</td><td>Умеренный</td></tr>
      <tr><td class="name">15 – 20</td><td class="warn">Сильный — организация гроз</td></tr>
      <tr><td class="name">&gt; 20</td><td class="bad">Очень сильный — угроза смерчей</td></tr>
    </tbody>
  </table>
</div>

<div class="idx-block">
  <h2>📊 Комбинированная вероятность грозы</h2>
  <p>
    В проекте используется взвешенная сумма:
  </p>

  <div class="formula">
P = 0.25·P(K) + 0.40·P(LI) + 0.35·P(CAPE)
  </div>

  <p>
    где P(K), P(LI), P(CAPE) — вероятности по каждому индексу
    из таблиц выше. Веса подобраны эмпирически по Богаткину.
  </p>
</div>

<div class="idx-block">
  <h2>🌫 Туман (метод Кирюхина)</h2>
  <p>
    Модифицированный метод Б. В. Кирюхина. Проверяются 5 условий,
    каждое даёт +1 балл. Итоговый балл 0–5.
  </p>

  <table class="idx-table">
    <thead>
      <tr>
        <th>Условие</th>
        <th>Порог</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">Дефицит точки росы</td><td>ΔTd ≤ 2 °C</td></tr>
      <tr><td class="name">Ветер</td><td>0.5 – 3 м/с</td></tr>
      <tr><td class="name">Облачность</td><td>&lt; 30 %</td></tr>
      <tr><td class="name">Ночные часы</td><td>0 – 9 ч</td></tr>
      <tr><td class="name">Относительная влажность</td><td>RH ≥ 90 %</td></tr>
    </tbody>
  </table>

  <table class="idx-table" style="margin-top:16px;">
    <thead>
      <tr>
        <th>Балл</th>
        <th>Вероятность тумана</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">0 – 1</td><td class="good">Нет</td></tr>
      <tr><td class="name">2</td><td class="good">Слабая</td></tr>
      <tr><td class="name">3</td><td class="warn">Умеренная</td></tr>
      <tr><td class="name">4</td><td class="bad">Высокая</td></tr>
      <tr><td class="name">5</td><td class="bad">Очень высокая</td></tr>
    </tbody>
  </table>
</div>

""" + render_biblio_ref("aviation", "гл. 9–10") + """
""" + COMMON_JS + render_top_controls() + render_legend("synoptic") + """
</body>
</html>
"""
# ==================================================================
# ТЕСТЫ ПО БЛОКАМ
# ==================================================================
TESTS_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Тесты — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .block-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 14px; margin: 20px 0;
  }
  .block-card {
    padding: 20px 22px; border-radius: 16px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border); backdrop-filter: blur(14px);
    cursor: pointer; transition: all 0.25s;
    position: relative; overflow: hidden;
  }
  .block-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0; transition: opacity 0.3s;
  }
  .block-card:hover {
    transform: translateY(-3px); border-color: var(--border-hover);
    box-shadow: var(--card-shadow);
  }
  .block-card:hover::before { opacity: 1; }
  .block-card .icon { font-size: 28px; margin-bottom: 8px; display: block; }
  .block-card .title { font-size: 17px; font-weight: 700; margin-bottom: 6px; }
  .block-card .desc {
    color: var(--text-2); font-size: 12px; line-height: 1.5;
    margin-bottom: 10px;
  }
  .block-card .count {
    display: inline-block; padding: 3px 10px; border-radius: 6px;
    background: rgba(77,171,255,0.12); color: var(--accent);
    border: 1px solid rgba(77,171,255,0.25);
    font-size: 11px; font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
  }

  .test-area {
    margin: 20px 0; padding: 24px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; backdrop-filter: blur(14px);
    min-height: 200px;
  }
  .progress-bar {
    height: 6px; background: rgba(120,160,255,0.1);
    border-radius: 3px; overflow: hidden; margin-bottom: 16px;
  }
  .progress-fill {
    height: 100%; background: linear-gradient(90deg, #4dabff, #7c5cff);
    transition: width 0.3s ease;
  }
  .progress-text {
    color: var(--text-2); font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 16px;
  }
  .question {
    font-size: 18px; font-weight: 600; line-height: 1.5;
    color: var(--text-0); margin-bottom: 18px;
  }
  .options { display: flex; flex-direction: column; gap: 8px; }
  .option {
    padding: 12px 16px; border-radius: 10px;
    background: rgba(15,21,36,0.4);
    border: 1px solid var(--border);
    cursor: pointer; transition: all 0.15s;
    font-size: 14px; color: var(--text-1);
    display: flex; align-items: flex-start; gap: 10px;
  }
  .option:hover { border-color: var(--border-hover); color: var(--text-0); }
  .option.selected {
    background: rgba(77,171,255,0.15);
    border-color: var(--accent); color: var(--text-0);
  }
  .option.correct {
    background: rgba(0,229,160,0.15);
    border-color: #00e5a0; color: #00e5a0;
  }
  .option.wrong {
    background: rgba(255,84,112,0.15);
    border-color: #ff5470; color: #ff5470;
  }
  .option .num {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700; color: var(--accent);
    flex-shrink: 0;
  }
  .option.correct .num { color: #00e5a0; }
  .option.wrong .num { color: #ff5470; }

  .explain-box {
    margin-top: 16px; padding: 14px 18px;
    background: rgba(77,171,255,0.08);
    border-left: 3px solid var(--accent);
    border-radius: 10px;
    font-size: 13px; color: var(--text-1); line-height: 1.6;
  }
  .explain-box .ref {
    display: block; margin-top: 8px;
    color: var(--text-2); font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
  }

  .btn-row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 20px; }
  .btn {
    padding: 12px 24px; border-radius: 10px; border: none;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff; cursor: pointer; font-size: 14px; font-weight: 600;
    transition: opacity 0.2s;
  }
  .btn:hover { opacity: 0.9; }
  .btn:disabled {
    opacity: 0.4; cursor: not-allowed;
  }
  .btn.secondary {
    background: var(--bg-1); color: var(--text-0);
    border: 1px solid var(--border);
  }
  .btn.secondary:hover {
    background: var(--bg-2);
    border-color: var(--border-hover);
  }

  .result-box {
    text-align: center; padding: 30px 20px;
  }
  .result-score {
    font-size: 56px; font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 8px;
  }
  .result-score.good { color: #00e5a0; }
  .result-score.warn { color: #ffb547; }
  .result-score.bad  { color: #ff5470; }
  .result-text {
    color: var(--text-1); font-size: 16px;
    margin-bottom: 20px;
  }
  .result-detail {
    display: inline-block; padding: 8px 16px;
    background: rgba(15,21,36,0.4);
    border: 1px solid var(--border); border-radius: 10px;
    font-size: 13px; color: var(--text-2);
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 20px;
  }
</style>
</head>
<body>

<a class="back" href="/theory">← Теория</a>
<h1>📝 Тесты по блокам</h1>
<div class="sub">Выбери блок — проверь знания. 20–37 вопросов, результат сразу, разбор ошибок.</div>

<div id="block-selection">
  <div class="block-grid">
    {% for key, block in tests.items() %}
    <div class="block-card" onclick="startTest('{{ key }}')">
      <span class="icon">{{ block.icon }}</span>
      <div class="title">{{ block.title }}</div>
      <div class="desc">{{ block.description }}</div>
      <span class="count">{{ block.questions | length }} вопросов</span>
    </div>
    {% endfor %}
  </div>
</div>

<div id="test-area" class="test-area" style="display:none;"></div>

<script>
var TESTS_DATA = {{ tests_json | safe }};
var currentBlock = null;
var currentQuestions = [];
var currentIndex = 0;
var currentScore = 0;
var selectedAnswer = null;
var answered = false;

function startTest(blockKey) {
  var block = TESTS_DATA[blockKey];
  if (!block) return;

  currentBlock = blockKey;
  currentQuestions = block.questions.slice();
  shuffle(currentQuestions);
  currentIndex = 0;
  currentScore = 0;
  selectedAnswer = null;
  answered = false;

  document.getElementById('block-selection').style.display = 'none';
  document.getElementById('test-area').style.display = 'block';
  renderQuestion();
}

function shuffle(arr) {
  for (var i = arr.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
  }
}

function renderQuestion() {
  var area = document.getElementById('test-area');
  if (currentIndex >= currentQuestions.length) {
    renderResult();
    return;
  }

  var q = currentQuestions[currentIndex];
  var total = currentQuestions.length;
  var progress = (currentIndex / total) * 100;

  var html = ''
    + '<div class="progress-bar"><div class="progress-fill" style="width:' + progress + '%"></div></div>'
    + '<div class="progress-text">Вопрос ' + (currentIndex + 1) + ' из ' + total
    + ' · правильных: ' + currentScore + '</div>'
    + '<div class="question">' + escapeHtml(q.q) + '</div>'
    + '<div class="options" id="options">';

  for (var i = 0; i < q.options.length; i++) {
    html += '<div class="option" data-idx="' + i + '" onclick="selectOption(' + i + ')">'
          + '<span class="num">' + (i + 1) + '.</span>'
          + '<span>' + escapeHtml(q.options[i]) + '</span>'
          + '</div>';
  }
  html += '</div>';

  html += '<div class="btn-row">'
        + '<button class="btn" id="confirm-btn" onclick="confirmAnswer()" disabled>Ответить</button>'
        + '<button class="btn secondary" onclick="exitTest()">Выйти</button>'
        + '</div>';

  area.innerHTML = html;

  selectedAnswer = null;
  answered = false;
}

function selectOption(idx) {
  if (answered) return;
  selectedAnswer = idx;
  var opts = document.querySelectorAll('.option');
  for (var i = 0; i < opts.length; i++) {
    opts[i].classList.toggle('selected', i === idx);
  }
  document.getElementById('confirm-btn').disabled = false;
}

function confirmAnswer() {
  if (answered || selectedAnswer === null) return;
  answered = true;

  var q = currentQuestions[currentIndex];
  var correct = q.correct;
  var opts = document.querySelectorAll('.option');

  for (var i = 0; i < opts.length; i++) {
    opts[i].classList.remove('selected');
    if (i === correct) opts[i].classList.add('correct');
    if (i === selectedAnswer && i !== correct) opts[i].classList.add('wrong');
  }

  if (selectedAnswer === correct) currentScore++;

  var area = document.getElementById('test-area');
  var explain = document.createElement('div');
  explain.className = 'explain-box';
  explain.innerHTML = escapeHtml(q.explain)
    + '<span class="ref">📖 ' + escapeHtml(q.ref || '—') + '</span>';
  area.insertBefore(explain, area.querySelector('.btn-row'));

  var btn = document.getElementById('confirm-btn');
  btn.textContent = (currentIndex + 1 < currentQuestions.length) ? 'Следующий →' : 'Показать результат';
  btn.disabled = false;
  btn.onclick = nextQuestion;
}

function nextQuestion() {
  currentIndex++;
  renderQuestion();
}

function renderResult() {
  var total = currentQuestions.length;
  var percent = Math.round((currentScore / total) * 100);
  var cls = percent >= 80 ? 'good' : percent >= 50 ? 'warn' : 'bad';
  var emoji = percent >= 80 ? '🎉' : percent >= 50 ? '👍' : '📚';
  var text = percent >= 80 ? 'Отличный результат!' : percent >= 50 ? 'Неплохо, но есть куда расти.' : 'Стоит повторить материал.';

  var block = TESTS_DATA[currentBlock];
  var area = document.getElementById('test-area');
  area.innerHTML = ''
    + '<div class="result-box">'
    + '  <div class="result-score ' + cls + '">' + percent + '%</div>'
    + '  <div class="result-text">' + emoji + ' ' + text + '</div>'
    + '  <div class="result-detail">' + currentScore + ' из ' + total + ' правильных</div>'
    + '  <div class="btn-row" style="justify-content:center;">'
    + '    <button class="btn" id="retry-btn">Пройти заново</button>'
    + '    <button class="btn secondary" id="exit-btn">К списку блоков</button>'
    + '  </div>'
    + '</div>';

  document.getElementById('retry-btn').onclick = function() {
    startTest(currentBlock);
  };
  document.getElementById('exit-btn').onclick = exitTest;
}

function escapeHtml(s) {
  if (s === null || s === undefined) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
</script>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""
# ==================================================================
# СВОДКА ЯВЛЕНИЙ ДЛЯ ПРОИЗВОЛЬНОЙ ТОЧКИ
# ==================================================================
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

<a class="back" href="/analysis">← Анализ</a>
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

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""
