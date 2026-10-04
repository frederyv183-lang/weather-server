# -*- coding: utf-8 -*-
"""Базовые стили, общий JS, вспомогательные функции рендера."""

from core.dictionaries import (
    CODE_TO_TEXT, WEATHER_ICONS, LEGEND_ITEMS, BIBLIOGRAPHY_ITEMS,
)
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




def render_header(active=""):
    """
    Возвращает HTML-шапку с горизонтальным меню.
    active — ключ активного пункта: 'home', 'forecast', 'analysis',
             'theory', 'maps', 'archive', 'about' или '' (нет активного).
    """
    items = [
        ("home",     "/",            "Главная"),
        ("forecast", "/forecast",    "Прогнозы"),
        ("analysis", "/analysis",    "Анализ"),
        ("theory",   "/theory",      "Теория"),
        ("maps",     "/maps",        "Карты"),
        ("archive",  "/archive",     "Архив"),
        ("about",    "/about",       "О проекте"),
    ]

    links = ""
    for key, url, label in items:
        cls = "active" if key == active else ""
        links += f'<a href="{url}" class="nav-link {cls}">{label}</a>'

    return f"""
<header class="topnav">
  <div class="topnav-inner">
    <a href="/" class="brand">
      <span class="brand-icon">≈</span>
      <span class="brand-text">weather-msk</span>
    </a>
    <nav class="nav-links">
      {links}
    </nav>
    <div class="nav-right">
      <button id="theme-btn" onclick="toggleTheme()" title="Сменить тему">🌙</button>
      <button id="season-btn" onclick="cycleSeason()" title="Сезон">🍂</button>
    </div>
  </div>
</header>
<style>
  .topnav {{
    position: sticky;
    top: 0;
    z-index: 9000;
    background: rgba(15, 21, 36, 0.85);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border);
    margin: -20px -20px 20px -20px;
  }}
  [data-theme="light"] .topnav {{
    background: rgba(255, 255, 255, 0.85);
  }}
  .topnav-inner {{
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 20px;
    height: 56px;
    display: flex;
    align-items: center;
    gap: 24px;
  }}
  .brand {{
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: var(--text-0);
    font-weight: 700;
    font-size: 15px;
    letter-spacing: -0.3px;
    flex-shrink: 0;
  }}
  .brand-icon {{
    color: var(--accent);
    font-size: 20px;
    font-weight: 800;
  }}
  .nav-links {{
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    flex: 1;
  }}
  .nav-link {{
    padding: 8px 14px;
    border-radius: 8px;
    text-decoration: none;
    color: var(--text-1);
    font-size: 13px;
    font-weight: 500;
    transition: all 0.15s;
    white-space: nowrap;
  }}
  .nav-link:hover {{
    color: var(--text-0);
    background: rgba(77, 171, 255, 0.08);
  }}
  .nav-link.active {{
    color: var(--text-0);
    background: linear-gradient(135deg, rgba(77, 171, 255, 0.20), rgba(124, 92, 255, 0.20));
    border: 1px solid rgba(77, 171, 255, 0.3);
  }}
  .nav-right {{
    display: flex;
    gap: 6px;
    flex-shrink: 0;
  }}
  .nav-right button {{
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-0);
    width: 34px;
    height: 34px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }}
  .nav-right button:hover {{
    border-color: var(--border-hover);
    background: rgba(77, 171, 255, 0.08);
  }}
  @media (max-width: 900px) {{
    .topnav-inner {{ padding: 0 12px; gap: 12px; }}
    .nav-links {{ overflow-x: auto; }}
    .nav-link {{ padding: 6px 10px; font-size: 12px; }}
  }}
</style>
<script>
  (function(){{
    var b = document.getElementById('theme-btn');
    if (b) b.textContent = (window.__currentTheme === 'light') ? '☀️' : '🌙';
    if (typeof updateSeasonButton === 'function') updateSeasonButton();
  }})();
</script>
"""




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
