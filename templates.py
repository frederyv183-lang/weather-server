# -*- coding: utf-8 -*-
"""
Шаблоны и стили для server.py.
Только константы и функции рендера, без маршрутов.
"""

import json

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

  body::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: -1;
    pointer-events: none;
    opacity: 0;
    transition: opacity 1.5s ease-in-out;
  }
  body[data-weather="clear"]::after {
    background: radial-gradient(circle at 75% 25%,
      rgba(255, 220, 120, 0.10), transparent 55%);
    opacity: 1;
  }
  body[data-tod="night"][data-weather="clear"]::after {
    background:
      radial-gradient(circle at 75% 20%, rgba(200, 220, 255, 0.12), transparent 45%),
      radial-gradient(circle at 15% 60%, rgba(120, 160, 255, 0.06), transparent 55%),
      radial-gradient(circle at 40% 80%, rgba(160, 120, 255, 0.05), transparent 50%);
    opacity: 1;
  }
  body[data-weather="mostly-clear"]::after {
    background: radial-gradient(circle at 70% 25%,
      rgba(255, 220, 120, 0.08), transparent 50%);
    opacity: 1;
  }
  body[data-weather="partly-cloudy"]::after {
    background:
      radial-gradient(ellipse at 20% 30%, rgba(200, 220, 240, 0.08), transparent 50%),
      radial-gradient(ellipse at 80% 60%, rgba(200, 220, 240, 0.06), transparent 55%);
    opacity: 1;
  }
  body[data-weather="overcast"]::after {
    background: linear-gradient(180deg,
      rgba(120, 130, 150, 0.20), rgba(90, 100, 120, 0.15));
    opacity: 1;
  }
  body[data-weather="rain"]::after,
  body[data-weather="showers"]::after {
    background: linear-gradient(180deg,
      rgba(40, 60, 100, 0.35), rgba(20, 40, 70, 0.25));
    opacity: 1;
  }
  body[data-weather="snow"]::after,
  body[data-weather="snow-showers"]::after {
    background: linear-gradient(180deg,
      rgba(200, 220, 255, 0.20), rgba(150, 180, 220, 0.12));
    opacity: 1;
  }
  body[data-weather="thunder"]::after {
    background: linear-gradient(180deg,
      rgba(30, 20, 60, 0.50), rgba(60, 30, 90, 0.35));
    opacity: 1;
    animation: lightning 8s ease-in-out infinite;
  }
  @keyframes lightning {
    0%, 84%, 100% { filter: brightness(1); }
    85%, 87%        { filter: brightness(2.5) hue-rotate(-10deg); }
    86%, 88%        { filter: brightness(1.2); }
    90%             { filter: brightness(1.8); }
  }
  body[data-weather="fog"]::after {
    background: linear-gradient(180deg,
      rgba(180, 190, 210, 0.30), rgba(140, 150, 170, 0.20));
    opacity: 1;
    animation: fog-drift 30s ease-in-out infinite alternate;
  }
  @keyframes fog-drift {
    from { transform: translateX(-3%) translateY(-1%); }
    to   { transform: translateX(3%) translateY(1%); }
  }

  body[data-bg-mode="static"]::before {
    background: var(--bg-0) !important;
    animation: none !important;
  }
  body[data-bg-mode="static"]::after { display: none !important; }
  body[data-bg-mode="static"] #weather-particles { display: none !important; }
  [data-theme="dark"] body[data-bg-mode="static"]::before {
    background:
      radial-gradient(ellipse at top left, rgba(77, 171, 255, 0.08), transparent 50%),
      radial-gradient(ellipse at bottom right, rgba(124, 92, 255, 0.08), transparent 50%),
      var(--bg-0) !important;
  }

  #weather-particles {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    z-index: -1; pointer-events: none; overflow: hidden;
    opacity: 0; transition: opacity 1.5s ease-in-out;
  }
  #weather-particles.active { opacity: 1; }

  .wp-drop {
    position: absolute; top: -10%; width: 2px; height: 18px;
    background: linear-gradient(180deg, transparent, rgba(160, 200, 255, 0.75));
    border-radius: 1px; animation: wp-fall linear infinite;
  }
  .wp-flake {
    position: absolute; top: -5%; width: 6px; height: 6px;
    background: rgba(220, 235, 255, 0.9); border-radius: 50%;
    box-shadow: 0 0 4px rgba(200, 220, 255, 0.8);
    animation: wp-snowfall linear infinite;
  }
  @keyframes wp-fall {
    from { transform: translateY(-10vh) translateX(0); opacity: 0; }
    10%, 90% { opacity: 1; }
    to { transform: translateY(110vh) translateX(3vw); opacity: 0; }
  }
  @keyframes wp-snowfall {
    from { transform: translateY(-10vh) translateX(0) rotate(0deg); opacity: 0; }
    10%, 90% { opacity: 1; }
    to { transform: translateY(110vh) translateX(-2vw) rotate(180deg); opacity: 0; }
  }
  .wp-star {
    position: absolute; width: 2px; height: 2px;
    background: #fff; border-radius: 50%;
    box-shadow: 0 0 3px rgba(200, 220, 255, 0.9);
    animation: wp-twinkle 3s ease-in-out infinite;
  }
  @keyframes wp-twinkle {
    0%, 100% { opacity: 0.3; transform: scale(0.8); }
    50%      { opacity: 1;   transform: scale(1.2); }
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
  .top-controls > button,
  .top-controls > .bg-menu-wrap > button {
    background: var(--card-bg); border: 1px solid var(--border);
    color: var(--text-0); width: 38px; height: 38px; border-radius: 10px;
    cursor: pointer; font-size: 16px; display: inline-flex;
    align-items: center; justify-content: center;
    transition: all 0.2s; backdrop-filter: blur(10px);
  }
  .top-controls > button:hover,
  .top-controls > .bg-menu-wrap > button:hover {
    border-color: var(--border-hover); box-shadow: var(--card-shadow);
  }

  .bg-menu-wrap { position: relative; }
  .bg-menu {
    position: absolute; top: 46px; left: 0;
    background: var(--card-bg); backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 12px;
    padding: 8px; display: none; flex-direction: column; gap: 2px;
    min-width: 200px; box-shadow: 0 12px 30px -12px rgba(0,0,0,0.5);
    z-index: 10000;
  }
  .bg-menu.open { display: flex; }
  .bg-menu button {
    width: 100%; background: transparent; border: none;
    color: var(--text-0); text-align: left;
    padding: 8px 12px; border-radius: 8px; cursor: pointer;
    font-size: 13px; font-family: 'Inter', sans-serif;
    display: flex; align-items: center; gap: 8px;
  }
  .bg-menu button:hover { background: rgba(120,160,255,0.10); }
  .bg-menu button.active {
    background: rgba(77,171,255,0.18); color: var(--accent); font-weight: 600;
  }
  .bg-menu .divider {
    height: 1px; background: var(--border); margin: 4px 0;
  }

  .current-card {
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 20px;
    padding: 22px 26px; margin-bottom: 22px;
    display: flex; flex-wrap: wrap; gap: 24px; align-items: center;
  }
  .current-card .cur-icon { flex-shrink: 0; }
  .current-card .cur-main { flex: 1 1 220px; }
  .current-card .cur-place {
    font-size: 13px; color: var(--text-2); margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace;
  }
  .current-card .cur-temp {
    font-size: 48px; font-weight: 700; line-height: 1;
    color: var(--text-0); letter-spacing: -1.5px;
  }
  .current-card .cur-feels {
    font-size: 13px; color: var(--text-2); margin-top: 4px;
  }
  .current-card .cur-desc {
    font-size: 15px; color: var(--text-1); margin-top: 8px;
  }
  .current-card .cur-stats {
    display: grid; grid-template-columns: repeat(2, minmax(120px, 1fr));
    gap: 10px 18px; font-size: 13px; color: var(--text-1);
    flex: 1 1 260px;
  }
  .current-card .cur-stats b { color: var(--text-0); font-weight: 600; }
  .current-card .cur-hourly {
    display: flex; gap: 12px; margin-top: 14px;
    overflow-x: auto; padding-bottom: 4px; flex: 1 1 100%;
  }
  .current-card .cur-hourly .h {
    display: flex; flex-direction: column; align-items: center;
    gap: 4px; min-width: 52px; padding: 8px 6px; border-radius: 10px;
    background: rgba(120,160,255,0.06); border: 1px solid var(--border);
  }
  .current-card .cur-hourly .h .t {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px; font-weight: 600;
  }
  .current-card .cur-hourly .h .hh { font-size: 11px; color: var(--text-2); }

  .spark {
    display: inline-block; vertical-align: middle;
    margin-left: 6px; opacity: 0.85;
  }

  @media (max-width: 600px) {
    .current-card { padding: 18px 18px; gap: 16px; }
    .current-card .cur-temp { font-size: 38px; }
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
})();
</script>
"""


def render_top_controls():
    return """
    <div class="top-controls">
      <button id="theme-btn" onclick="toggleTheme()" title="Сменить тему">🌙</button>

      <div class="bg-menu-wrap">
        <button id="bg-btn" onclick="toggleBgMenu()" title="Настройки фона">🎨</button>
        <div class="bg-menu" id="bg-menu">
          <button onclick="setBgMode('static')" id="bg-static">⬜ Обычный фон</button>
          <button onclick="setBgMode('dynamic')" id="bg-dynamic">🌈 Динамический</button>
          <div class="divider"></div>
          <button onclick="setWeather('auto')" id="w-auto">🔄 Авто (по времени)</button>
          <button onclick="setWeather('clear')" id="w-clear">✨ Ясно</button>
          <button onclick="setWeather('rain')" id="w-rain">🌧 Дождь</button>
          <button onclick="setWeather('thunder')" id="w-thunder">🌩 Гроза</button>
          <button onclick="setWeather('fog')" id="w-fog">🌫 Туман</button>
          <button onclick="setWeather('snow')" id="w-snow">❄️ Снег</button>
        </div>
      </div>
    </div>
    <script>
      (function(){
        var b = document.getElementById('theme-btn');
        if (b) b.textContent = (window.__currentTheme === 'light') ? '☀️' : '🌙';

        var bgMode = localStorage.getItem('weather-bg-mode') || 'dynamic';
        var weather = localStorage.getItem('weather-bg-weather') || 'auto';

        window.__bgMode = bgMode;
        window.__bgWeather = weather;
        window.__autoWeather = 'clear';

        function applyBgMode() {
          document.body.setAttribute('data-bg-mode', bgMode);
          var btn = document.getElementById('bg-btn');
          if (btn) btn.textContent = (bgMode === 'dynamic') ? '🎨' : '⬜';
          var s = document.getElementById('bg-static');
          var d = document.getElementById('bg-dynamic');
          if (s) s.classList.toggle('active', bgMode === 'static');
          if (d) d.classList.toggle('active', bgMode === 'dynamic');
        }

        function applyWeather() {
          var realWeather = (weather === 'auto')
            ? (window.__autoWeather || 'clear')
            : weather;
          document.body.setAttribute('data-weather', realWeather);
          ['auto','clear','rain','thunder','fog','snow'].forEach(function(k) {
            var el = document.getElementById('w-' + k);
            if (el) el.classList.toggle('active', weather === k);
          });
          if (typeof window.__rebuildParticles === 'function') {
            window.__rebuildParticles(realWeather);
          }
        }

        window.toggleBgMenu = function() {
          document.getElementById('bg-menu').classList.toggle('open');
        };

        window.setBgMode = function(mode) {
          bgMode = mode;
          localStorage.setItem('weather-bg-mode', mode);
          applyBgMode();
          applyWeather();
          document.getElementById('bg-menu').classList.remove('open');
        };

        window.setWeather = function(w) {
          weather = w;
          localStorage.setItem('weather-bg-weather', w);
          applyWeather();
          document.getElementById('bg-menu').classList.remove('open');
        };

        document.addEventListener('click', function(e) {
          var wrap = document.querySelector('.bg-menu-wrap');
          var menu = document.getElementById('bg-menu');
          if (wrap && menu && !wrap.contains(e.target)) {
            menu.classList.remove('open');
          }
        });

        function updateTod() {
          var h = new Date().getHours();
          var tod;
          if (h >= 5 && h < 8) tod = 'dawn';
          else if (h >= 8 && h < 18) tod = 'day';
          else if (h >= 18 && h < 21) tod = 'dusk';
          else tod = 'night';
          document.body.setAttribute('data-tod', tod);
        }
        updateTod();
        setInterval(updateTod, 60000);

        applyBgMode();
        applyWeather();

        window.__applyAutoWeather = function(code) {
          window.__autoWeather = (code === 0 || code === 1) ? 'clear'
            : (code === 2) ? 'partly-cloudy'
            : (code === 3) ? 'overcast'
            : (code === 45 || code === 48) ? 'fog'
            : (code >= 51 && code <= 67) ? 'rain'
            : (code >= 71 && code <= 77) ? 'snow'
            : (code >= 80 && code <= 82) ? 'rain'
            : (code === 85 || code === 86) ? 'snow'
            : (code >= 95) ? 'thunder'
            : 'clear';
          if (weather === 'auto') applyWeather();
        };
      })();
    </script>
    """


CURRENT_CARD_HTML = """
<div class="current-card fade-in" id="current-card">
  <div class="cur-icon" id="cc-icon">
    <svg viewBox="0 0 64 64" width="72" height="72">
      <circle cx="32" cy="32" r="14" fill="none"
              stroke="var(--border)" stroke-width="2" stroke-dasharray="4 4"/>
    </svg>
  </div>
  <div class="cur-main">
    <div class="cur-place" id="cc-place">Определяем…</div>
    <div class="cur-temp" id="cc-temp">—°</div>
    <div class="cur-feels" id="cc-feels"></div>
    <div class="cur-desc" id="cc-desc"></div>
  </div>
  <div class="cur-stats" id="cc-stats"></div>
  <div class="cur-hourly" id="cc-hourly"></div>
</div>
"""


CURRENT_CARD_JS_TEMPLATE = """
<script>
(function() {
  var ICONS = __WEATHER_ICONS_JSON__;
  var CODE_TO_CLASS = {
    0:'clear',1:'mostly-clear',2:'partly-cloudy',3:'overcast',
    45:'fog',48:'fog',
    51:'rain',53:'rain',55:'rain',
    61:'rain',63:'rain',65:'rain',66:'rain',67:'rain',
    71:'snow',73:'snow',75:'snow',77:'snow',
    80:'showers',81:'showers',82:'showers',
    85:'snow-showers',86:'snow-showers',
    95:'thunder',96:'thunder',99:'thunder'
  };
  var CODE_TO_TEXT = __CODE_TO_TEXT_JSON__;

  function setIcon(code) {
    var cls = CODE_TO_CLASS[code] || 'unknown';
    var svg = ICONS[cls] || ICONS['unknown'];
    document.getElementById('cc-icon').innerHTML = svg;
  }

  function dirText(deg) {
    if (deg === null || deg === undefined) return '—';
    var sectors = ['С','ССВ','СВ','ВСВ','В','ВЮВ','ЮВ','ЮЮВ',
                   'Ю','ЮЮЗ','ЮЗ','ЗЮЗ','З','ЗСЗ','СЗ','ССЗ'];
    var idx = Math.round((deg % 360) / 22.5) % 16;
    return sectors[idx];
  }

  async function loadCurrent(lat, lon, placeName) {
    try {
      var url = 'https://api.open-meteo.com/v1/forecast?latitude=' + lat +
                '&longitude=' + lon +
                '&current=temperature_2m,relative_humidity_2m,apparent_temperature,' +
                'is_day,precipitation,weather_code,cloud_cover,pressure_msl,' +
                'wind_speed_10m,wind_direction_10m,wind_gusts_10m' +
                '&hourly=temperature_2m,weather_code,precipitation_probability' +
                '&forecast_hours=6' +
                '&timezone=Europe/Moscow';
      var resp = await fetch(url);
      var data = await resp.json();
      if (!data.current) return;

      var c = data.current;
      document.getElementById('cc-place').textContent = '📍 ' + placeName;
      document.getElementById('cc-temp').textContent =
        Math.round(c.temperature_2m) + '°';
      document.getElementById('cc-feels').textContent =
        'Ощущается как ' + Math.round(c.apparent_temperature) + '°';
      document.getElementById('cc-desc').textContent =
        CODE_TO_TEXT[c.weather_code] || ('Код: ' + c.weather_code);

      setIcon(c.weather_code);
      if (typeof window.__applyAutoWeather === 'function') {
        window.__applyAutoWeather(c.weather_code);
      }

      var stats = [
        ['💨 Ветер', c.wind_speed_10m.toFixed(1) + ' м/с, ' + dirText(c.wind_direction_10m)],
        ['💧 Осадки', c.precipitation.toFixed(1) + ' мм'],
        ['📊 Давление', Math.round(c.pressure_msl) + ' гПа'],
        ['💦 Влажность', c.relative_humidity_2m + '%'],
      ];
      document.getElementById('cc-stats').innerHTML = stats.map(function(s) {
        return '<div>' + s[0] + ': <b>' + s[1] + '</b></div>';
      }).join('');

      var hours = data.hourly && data.hourly.time ? data.hourly.time.slice(0, 6) : [];
      var temps = data.hourly && data.hourly.temperature_2m
                  ? data.hourly.temperature_2m.slice(0, 6) : [];
      var codes = data.hourly && data.hourly.weather_code
                  ? data.hourly.weather_code.slice(0, 6) : [];
      var html = '';
      for (var i = 0; i < hours.length; i++) {
        var t = hours[i].slice(11, 16);
        var tt = temps[i] !== null && temps[i] !== undefined
                 ? Math.round(temps[i]) + '°' : '—';
        var cc = codes[i];
        var cls = CODE_TO_CLASS[cc] || 'unknown';
        var svg = ICONS[cls] || ICONS['unknown'];
        html += '<div class="h">' + svg.replace('width="48" height="48"',
                  'width="28" height="28"') +
                '<div class="t">' + tt + '</div>' +
                '<div class="hh">' + t + '</div></div>';
      }
      document.getElementById('cc-hourly').innerHTML = html;
    } catch (e) {
      document.getElementById('cc-place').textContent = 'Ошибка загрузки';
    }
  }

  var particleLayer = document.getElementById('weather-particles');
  var currentParticleType = null;

  function clearParticles() {
    if (!particleLayer) return;
    particleLayer.innerHTML = '';
    particleLayer.classList.remove('active');
    currentParticleType = null;
  }

  function buildRain(count) {
    if (!particleLayer) return;
    particleLayer.innerHTML = '';
    for (var i = 0; i < count; i++) {
      var d = document.createElement('div');
      d.className = 'wp-drop';
      d.style.left = Math.random() * 100 + '%';
      d.style.animationDuration = (0.6 + Math.random() * 0.6) + 's';
      d.style.animationDelay = (Math.random() * 2) + 's';
      d.style.height = (12 + Math.random() * 12) + 'px';
      d.style.opacity = 0.5 + Math.random() * 0.5;
      particleLayer.appendChild(d);
    }
    particleLayer.classList.add('active');
    currentParticleType = 'rain';
  }

  function buildSnow(count) {
    if (!particleLayer) return;
    particleLayer.innerHTML = '';
    for (var i = 0; i < count; i++) {
      var f = document.createElement('div');
      f.className = 'wp-flake';
      f.style.left = Math.random() * 100 + '%';
      f.style.animationDuration = (6 + Math.random() * 6) + 's';
      f.style.animationDelay = (Math.random() * 5) + 's';
      var size = 3 + Math.random() * 5;
      f.style.width = size + 'px';
      f.style.height = size + 'px';
      particleLayer.appendChild(f);
    }
    particleLayer.classList.add('active');
    currentParticleType = 'snow';
  }

  function buildStars(count) {
    if (!particleLayer) return;
    particleLayer.innerHTML = '';
    for (var i = 0; i < count; i++) {
      var s = document.createElement('div');
      s.className = 'wp-star';
      s.style.left = Math.random() * 100 + '%';
      s.style.top = Math.random() * 60 + '%';
      s.style.animationDelay = (Math.random() * 3) + 's';
      particleLayer.appendChild(s);
    }
    particleLayer.classList.add('active');
    currentParticleType = 'stars';
  }

  window.__rebuildParticles = function(weather) {
    if (document.body.getAttribute('data-bg-mode') === 'static') {
      clearParticles();
      return;
    }
    var tod = document.body.getAttribute('data-tod');
    if (weather === 'rain' || weather === 'thunder') {
      buildRain(weather === 'thunder' ? 120 : 80);
    } else if (weather === 'snow') {
      buildSnow(60);
    } else if (tod === 'night' && weather === 'clear') {
      buildStars(50);
    } else {
      clearParticles();
    }
  };

  var params = new URLSearchParams(window.location.search);
  var qLat = params.get('lat');
  var qLon = params.get('lon');
  var qName = params.get('name');

  if (qLat && qLon) {
    loadCurrent(parseFloat(qLat), parseFloat(qLon), qName || (qLat + ', ' + qLon));
  } else if ('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(
      function(pos) {
        loadCurrent(pos.coords.latitude, pos.coords.longitude, 'Ваше местоположение');
      },
      function() {
        loadCurrent(__DEFAULT_LAT__, __DEFAULT_LON__, __DEFAULT_NAME__);
      },
      { enableHighAccuracy: false, timeout: 6000, maximumAge: 600000 }
    );
  } else {
    loadCurrent(__DEFAULT_LAT__, __DEFAULT_LON__, __DEFAULT_NAME__);
  }
})();
</script>
"""


def build_current_card_js():
    return (CURRENT_CARD_JS_TEMPLATE
            .replace("__WEATHER_ICONS_JSON__", json.dumps(WEATHER_ICONS, ensure_ascii=False))
            .replace("__CODE_TO_TEXT_JSON__", json.dumps(CODE_TO_TEXT, ensure_ascii=False))
            .replace("__DEFAULT_LAT__", str(DEFAULT_LOCATION["lat"]))
            .replace("__DEFAULT_LON__", str(DEFAULT_LOCATION["lon"]))
            .replace("__DEFAULT_NAME__", json.dumps(DEFAULT_LOCATION["name"], ensure_ascii=False)))


VIEW_TABS = """
<div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;">
  <a href="/forecast/{{ model }}/{{ station_key }}"
     style="padding:9px 16px;border-radius:10px;text-decoration:none;font-size:13px;font-weight:500;
            {% if view == 'table' %}background:linear-gradient(135deg,#4dabff,#7c5cff);color:#fff;box-shadow:0 4px 20px -4px rgba(77,171,255,0.5);{% else %}background:rgba(120,160,255,0.08);color:var(--text-1);border:1px solid var(--border);{% endif %}">
     📋 Таблица</a>
  <a href="/text/{{ model }}/{{ station_key }}"
     style="padding:9px 16px;border-radius:10px;text-decoration:none;font-size:13px;font-weight:500;
            {% if view == 'text' %}background:linear-gradient(135deg,#4dabff,#7c5cff);color:#fff;box-shadow:0 4px 20px -4px rgba(77,171,255,0.5);{% else %}background:rgba(120,160,255,0.08);color:var(--text-1);border:1px solid var(--border);{% endif %}">
     📰 Текст</a>
  <a href="/chart/{{ station_key }}"
     style="padding:9px 16px;border-radius:10px;text-decoration:none;font-size:13px;font-weight:500;
            background:rgba(120,160,255,0.08);color:var(--text-1);border:1px solid var(--border);">
     📈 График</a>
  <a href="/verify/{{ station_key }}"
     style="padding:9px 16px;border-radius:10px;text-decoration:none;font-size:13px;font-weight:500;
            background:rgba(0,229,160,0.08);color:#00e5a0;border:1px solid rgba(0,229,160,0.2);">
     ✅ Проверка</a>
  <a href="/analyze/{{ station_key }}"
     style="padding:9px 16px;border-radius:10px;text-decoration:none;font-size:13px;font-weight:500;
            background:rgba(124,92,255,0.10);color:#a78bfa;border:1px solid rgba(124,92,255,0.25);">
     📊 Анализ</a>
  <a href="/aviation/{{ model }}/{{ station_key }}"
     style="padding:9px 16px;border-radius:10px;text-decoration:none;font-size:13px;font-weight:500;
            background:rgba(255,181,71,0.10);color:#ffb547;border:1px solid rgba(255,181,71,0.25);">
     ✈️ Авиация</a>
  <a href="/alt-verify/{{ station_key }}"
     style="padding:9px 16px;border-radius:10px;text-decoration:none;font-size:13px;font-weight:500;
            background:rgba(0,229,160,0.10);color:#00e5a0;border:1px solid rgba(0,229,160,0.25);">
     📋 Матрица</a>
  <a href="/compare-matrices/{{ station_key }}"
     style="padding:9px 16px;border-radius:10px;text-decoration:none;font-size:13px;font-weight:500;
            background:rgba(255,181,71,0.15);color:#ffb547;border:1px solid rgba(255,181,71,0.3);">
     🔀 Сравнить модели</a>
</div>
"""


# ============================================================
# HTML-ШАБЛОНЫ
# ============================================================

INDEX_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Прогноз погоды — weather-msk</title>
""" + BASE_STYLE + """
</head>
<body>

<div id="weather-particles"></div>

""" + CURRENT_CARD_HTML + """

<h1>Прогноз погоды</h1>
<div class="sub">Выберите модель прогноза</div>

{% for key, m in models.items() %}
  <a class="card fade-in" href="/model/{{ key }}" style="animation-delay: {{ loop.index * 0.05 }}s">
    <span class="icon">🌍</span><b>{{ m.name }}</b>
    <div class="desc">{{ m.desc }}</div>
  </a>
{% endfor %}

<a class="card fade-in" href="/search" style="animation-delay: 0.2s;background:rgba(124,92,255,0.10);">
  <span class="icon">🔍</span><b>Поиск прогноза для любой точки</b>
  <div class="desc">Город, координаты, индекс — с таблицей, текстом и графиком</div>
</a>

<a class="card fade-in" href="/verify/tushino" style="animation-delay: 0.22s;background:rgba(0,229,160,0.08);">
  <span class="icon">✅</span><b>Проверка моделей</b>
  <div class="desc">Сравнение с фактом (станция / ERA5) — MAE, RMSE, Bias</div>
</a>

<a class="card fade-in" href="/chart/tushino" style="animation-delay: 0.25s">
  <span class="icon">📈</span><b>Сравнить модели на графике</b>
  <div class="desc">Температура, θ, ветер, осадки, давление</div>
</a>

<a class="card fade-in" href="/analyze/tushino" style="animation-delay: 0.27s;background:rgba(124,92,255,0.10);">
  <span class="icon">📊</span><b>Статистический анализ</b>
  <div class="desc">Корреляция, R², MAPE, гистограмма ошибок, F1 по осадкам</div>
</a>

<a class="card fade-in" href="/aviation/gfs/tushino" style="animation-delay: 0.28s;background:rgba(255,181,71,0.10);">
  <span class="icon">✈️</span><b>Авиационные прогнозы</b>
  <div class="desc">Методы Богаткина: Вайтинг (K), LI, CAPE, туман по Кирюхину</div>
</a>

<a class="card fade-in" href="/alt-verify/tushino" style="animation-delay: 0.29s;background:rgba(0,229,160,0.10);">
  <span class="icon">📋</span><b>Матрица альтернативных прогнозов</b>
  <div class="desc">Критерии Хандожко: p, H, Q, v, τ, A — метод / инерц. / случайный / климатология</div>
</a>

<a class="card fade-in" href="/compare-matrices/tushino" style="animation-delay: 0.30s;background:rgba(255,181,71,0.15);">
  <span class="icon">🔀</span><b>Сравнить модели по матрицам</b>
  <div class="desc">GFS vs ECMWF vs ICON — p, H, Q, v, τ, A, S Хайдке</div>
</a>

<a class="card fade-in" href="/teaching" style="animation-delay: 0.32s;background:rgba(0,229,160,0.08);">
  <span class="icon">📚</span><b>Учебные примеры</b>
  <div class="desc">Разборы из учебника Дробжевой и Волобуевой (заморозки, ветер, пожары)</div>
</a>

<a class="card fade-in" href="/noaa" style="animation-delay: 0.33s;background:rgba(0,229,160,0.06);">
  <span class="icon">🗄</span><b>NOAA — исторические данные</b>
  <div class="desc">Наблюдения со станций NOAA NCEI (для Москвы — до 2022)</div>
</a>

<a class="card fade-in" href="/map" style="animation-delay: 0.34s">
  <span class="icon">🗺</span><b>Карта + спутник + радар</b>
  <div class="desc">OSM · Meteosat · RainViewer · поиск · клик</div>
</a>

<a class="card fade-in" href="/about" style="animation-delay: 0.35s;background:rgba(120,160,255,0.05);">
  <span class="icon">ℹ️</span><b>О проекте</b>
  <div class="desc">Источники данных, модели, метрики, как это работает</div>
</a>

""" + COMMON_JS + render_top_controls() + build_current_card_js() + """

</body>
</html>
"""


ABOUT_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>О проекте — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 22px 26px; margin-bottom: 16px; }
  .card h2 { font-size: 17px; margin: 0 0 14px 0;
             color: var(--accent); font-weight: 600; }
  .card p, .card li { color: var(--text-1); font-size: 14px;
                      line-height: 1.75; margin: 6px 0; }
  .card b { color: var(--text-0); }
  .card code { font-family: 'JetBrains Mono', monospace;
    background: rgba(120,160,255,0.08);
    padding: 2px 6px; border-radius: 5px; font-size: 12.5px;
    color: var(--accent); }
  .card ul { padding-left: 20px; margin: 6px 0; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
          gap: 14px; margin-top: 12px; }
  .grid .item { padding: 14px 16px; border-radius: 12px;
    background: rgba(120,160,255,0.05); border: 1px solid var(--border); }
  .grid .item b { display: block; margin-bottom: 4px; font-size: 13.5px; }
  .grid .item span { color: var(--text-2); font-size: 12.5px; line-height: 1.6; }
</style>
</head>
<body>
<a class="back" href="/">← На главную</a>
<h1>О проекте</h1>
<div class="sub">Источники данных, модели, метрики, принципы работы</div>

<div class="card fade-in">
  <h2>🌍 Что это</h2>
  <p><b>weather-msk</b> — учебно-исследовательский проект: сравнение прогнозов
  нескольких численных моделей атмосферы между собой и с фактическими данными.</p>
</div>

<div class="card fade-in">
  <h2>📡 Источники данных</h2>
  <div class="grid">
    <div class="item"><b>Прогноз: Open-Meteo</b>
      <span>GFS, ECMWF, ICON. Бесплатный API без ключа.</span></div>
    <div class="item"><b>Факт: Meteostat</b>
      <span>Прямые почасовые измерения с ближайшей метеостанции.</span></div>
    <div class="item"><b>Факт-фолбэк: ERA5</b>
      <span>Реанализ ECMWF, ~31 км. С weather_code и wind_speed_10m.</span></div>
    <div class="item"><b>История: NOAA NCEI</b>
      <span>Суточные наблюдения TMAX/TMIN/PRCP (для Москвы — до 2022).</span></div>
  </div>
</div>

<div class="card fade-in">
  <h2>📋 Матрица альтернативных прогнозов</h2>
  <p>По методу Л.А. Хандожко (учебник Дробжевой, Волобуевой, 2016):</p>
  <ul>
    <li><b>n11</b> — оправдавшиеся прогнозы наличия</li>
    <li><b>n12</b> — ошибки-пропуски</li>
    <li><b>n21</b> — ошибки-страховки</li>
    <li><b>n22</b> — оправдавшиеся прогнозы отсутствия</li>
  </ul>
  <p style="margin-top:12px">Критерии: <b>p</b> (оправдываемость), <b>H</b> (надёжность),
  <b>Q</b> (точность), <b>v</b> (информационное отношение),
  <b>τ</b> (Гудмэн–Крускал), <b>A</b> (сходство), <b>S</b> (Хайдке).</p>
</div>

<div class="card fade-in">
  <h2>✈️ Авиационные методы (по Богаткину)</h2>
  <p><b>Метод Вайтинга:</b> <code>K = 2·T850 − T500 − D850 − D700</code></p>
  <p><b>LI</b> и <b>CAPE</b> — современные индексы неустойчивости.</p>
  <p><b>Туман (по Кирюхину):</b> T−Td ≤ 2°C, ветер 0.5–3 м/с, облачность &lt;30%, ночь, RH ≥ 90%.</p>
</div>

<p style="text-align:center;color:var(--text-2);font-size:12px;margin-top:24px;">
  Проект носит образовательный характер.
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
<title>{{ model_name }} — выбор станции</title>
""" + BASE_STYLE + """
</head>
<body>
<a class="back" href="/">← Выбор модели</a>
<h1>{{ model_name }}</h1>
<div class="sub">Выберите станцию</div>

{% for key, s in stations.items() %}
  <a class="card fade-in" href="/forecast/{{ model }}/{{ key }}" style="animation-delay: {{ loop.index * 0.05 }}s">
    <span class="icon">📍</span><b>{{ s.name }}</b>
    <div class="coords">{{ s.lat }}, {{ s.lon }}</div>
  </a>
{% endfor %}

<a class="card fade-in" href="/chart/{{ first_station }}" style="animation-delay: 0.15s">
  <span class="icon">📈</span><b>Сравнить модели на графике</b>
</a>

<a class="card fade-in" href="/verify/{{ first_station }}" style="animation-delay: 0.2s;background:rgba(0,229,160,0.08);">
  <span class="icon">✅</span><b>Проверка моделей</b>
</a>

<a class="card fade-in" href="/alt-verify/{{ first_station }}" style="animation-delay: 0.22s;background:rgba(0,229,160,0.10);">
  <span class="icon">📋</span><b>Матрица альтернативных прогнозов</b>
</a>

<a class="card fade-in" href="/compare-matrices/{{ first_station }}" style="animation-delay: 0.24s;background:rgba(255,181,71,0.10);">
  <span class="icon">🔀</span><b>Сравнить модели по матрицам</b>
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
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 14px 16px; margin-bottom: 16px; overflow-x: auto; }
  .day-header { font-size: 15px; font-weight: 700; color: var(--accent);
    margin: 0 0 10px 0; padding-bottom: 8px;
    border-bottom: 1px solid var(--border); letter-spacing: 0.5px; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; min-width: 640px; }
  th, td { padding: 8px 6px; text-align: center;
           border-bottom: 1px solid rgba(120, 160, 255, 0.06); }
  th { background: rgba(120, 160, 255, 0.06); color: var(--text-1);
       font-weight: 600; font-size: 11px;
       text-transform: uppercase; letter-spacing: 0.5px; }
  td { color: var(--text-0); font-family: 'JetBrains Mono', monospace; }
  td:first-child { font-family: 'Inter', sans-serif; font-weight: 600; color: var(--accent); }
  td.icon-cell { padding: 2px 4px; }
  td.icon-cell svg { width: 30px; height: 30px; vertical-align: middle; }
  tr.clear td { background: rgba(77,171,255,0.06); }
  tr.mostly-clear td { background: rgba(77,171,255,0.04); }
  tr.partly-cloudy td { background: rgba(120,160,255,0.04); }
  tr.overcast td { background: rgba(120,160,255,0.08); }
  tr.fog td { background: rgba(255,181,71,0.10); }
  tr.rain td { background: rgba(77,171,255,0.10); }
  tr.snow td { background: rgba(180,220,255,0.08); }
  tr.showers td { background: rgba(77,171,255,0.14); }
  tr.snow-showers td { background: rgba(180,220,255,0.12); }
  tr.thunder td { background: rgba(124,92,255,0.14); }
  .updated { color: var(--text-2); font-size: 11px; text-align: center;
             margin-top: 16px; font-family: 'JetBrains Mono', monospace; }
  .add-place { display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 14px; border-radius: 10px; margin-bottom: 14px;
    background: rgba(124,92,255,0.10); color: var(--text-0);
    border: 1px solid rgba(124,92,255,0.25); cursor: pointer;
    font-size: 13px; font-weight: 500; font-family: 'Inter', sans-serif; }
  .add-place:hover { background: rgba(124,92,255,0.20); }
</style>
</head>
<body>

<a class="back" href="/model/{{ model }}">← Выбор станции</a>
<h1>{{ station }}</h1>
<div class="sub">
  Модель: <b style="color:var(--accent)">{{ model_name }}</b> ·
  {{ lat }}, {{ lon }} · прогноз на {{ days }} дня
</div>

<script id="place-data" type="application/json">
{"name": {{ station|tojson }}, "lat": {{ lat }}, "lon": {{ lon }}, "model": {{ model|tojson }}}
</script>
<button class="add-place" onclick="addCurrentPlace()">⭐ В «Мои места»</button>

{% if synoptic %}
<div class="card fade-in">
  <div class="day-header">🌀 Синоптический анализ</div>
  {% for ev in synoptic[:10] %}
    <span class="synoptic-badge synoptic-{{ ev.type }}">{{ ev.time[5:16].replace('T', ' ') }} — {{ ev.text }}</span>
  {% endfor %}
</div>
{% endif %}

""" + VIEW_TABS + """

{% for day, rows in by_day.items() %}
<div class="card fade-in">
  <div class="day-header">{{ day }}</div>
  <table>
    <tr>
      <th>Час</th><th></th><th>T°, C</th><th>θ, K</th><th>Ветер, м/с</th><th>Напр.</th>
      <th>Давл., гПа</th><th>Влаж., %</th><th>Осад., мм</th><th>Явление</th>
      <th>K</th><th>⛈</th><th>🌫</th>
    </tr>
    {% for h in rows %}
    <tr class="{{ h.css_class }}">
      <td>{{ h.time[11:16] }}</td>
      <td class="icon-cell">{{ h.icon_svg|safe }}</td>
      <td>{{ h.temp_c }}{{ h.temp_spark|safe }}</td>
      <td>{{ h.theta_k if h.theta_k else '—' }}</td>
      <td>{{ h.wind_ms }}</td>
      <td>{{ h.wind_dir_text }}</td>
      <td>{{ h.pressure_hpa|int if h.pressure_hpa is not none else '—' }}{{ h.press_spark|safe }}</td>
      <td>{{ h.humidity|int if h.humidity is not none else '—' }}</td>
      <td>{{ h.precipitation_mm }}</td>
      <td>{{ h.code_text }}</td>
      <td>{{ h.av_thunder.k if h.av_thunder.k is not none else '—' }}</td>
      <td>{{ h.av_thunder.combined_prob }}%</td>
      <td>{{ h.av_fog.probability }}%</td>
    </tr>
    {% endfor %}
  </table>
</div>
{% endfor %}

<div class="updated">Обновлено: {{ updated }}</div>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


TEXT_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ station }} — текстовый прогноз</title>
""" + BASE_STYLE + """
<style>
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 24px 28px; margin-bottom: 16px; }
  pre { white-space: pre-wrap; word-wrap: break-word;
    font-family: 'Inter', sans-serif; font-size: 15px;
    line-height: 1.8; margin: 0; color: var(--text-0); }
  .add-place { display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 14px; border-radius: 10px; margin-bottom: 14px;
    background: rgba(124,92,255,0.10); color: var(--text-0);
    border: 1px solid rgba(124,92,255,0.25); cursor: pointer;
    font-size: 13px; font-weight: 500; font-family: 'Inter', sans-serif; }
  .add-place:hover { background: rgba(124,92,255,0.20); }
</style>
</head>
<body>

<a class="back" href="/model/{{ model }}">← Назад</a>
<h1>{{ station }}</h1>
<div class="sub">
  Модель: <b style="color:var(--accent)">{{ model_name }}</b> ·
  текстовый прогноз на {{ days }} дня
</div>

<script id="place-data" type="application/json">
{"name": {{ station|tojson }}, "lat": {{ lat }}, "lon": {{ lon }}, "model": {{ model|tojson }}}
</script>
<button class="add-place" onclick="addCurrentPlace()">⭐ В «Мои места»</button>

""" + VIEW_TABS + """

{% if synoptic %}
<div class="card fade-in">
  <h2 style="font-size:16px;color:var(--accent);margin:0 0 12px 0;">🌀 Синоптический анализ</h2>
  {% for ev in synoptic[:10] %}
    <span class="synoptic-badge synoptic-{{ ev.type }}">{{ ev.time[5:16].replace('T', ' ') }} — {{ ev.text }}</span>
  {% endfor %}
</div>
{% endif %}

<div class="card fade-in">
  <pre>{{ text }}</pre>
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
<title>Поиск прогноза</title>
""" + BASE_STYLE + """
<style>
  .search-box { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 12px 14px; margin-bottom: 12px; display: flex; gap: 10px; }
  .search-box input { flex: 1; padding: 12px 16px;
    background: rgba(10, 14, 26, 0.5);
    border: 1px solid var(--border); border-radius: 10px;
    font-size: 14px; outline: none; color: var(--text-0);
    font-family: 'Inter', sans-serif; }
  [data-theme="light"] .search-box input { background: #fff; }
  .search-box input:focus { border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(77,171,255,0.15); }
  .search-box button { padding: 12px 22px; border: none; border-radius: 10px;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff; cursor: pointer; font-size: 14px; font-weight: 600; }
  .model-picker { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 12px 14px; margin-bottom: 16px;
    display: flex; align-items: center; gap: 12px; }
  .model-picker label { color: var(--text-1); font-size: 13px; }
  .model-picker select { padding: 10px 14px;
    background: rgba(10, 14, 26, 0.6);
    border: 1px solid var(--border); border-radius: 10px;
    color: var(--text-0); font-size: 14px; outline: none; }
  [data-theme="light"] .model-picker select { background: #fff; }
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 16px; margin-bottom: 16px; }
  #my-places { background: linear-gradient(135deg, rgba(124,92,255,0.08), rgba(15,21,36,0.5));
    backdrop-filter: blur(14px);
    border: 1px solid rgba(124,92,255,0.20);
    border-radius: 14px; padding: 14px 16px; margin-bottom: 16px; }
  #my-places h3 { margin: 0 0 10px 0; font-size: 13px;
                  color: var(--text-1); font-weight: 600; }
  .place-list { display: flex; flex-wrap: wrap; gap: 8px; }
  .place-item { display: inline-flex; align-items: center; gap: 8px;
    padding: 8px 12px; border-radius: 10px;
    background: rgba(120,160,255,0.06);
    border: 1px solid var(--border);
    text-decoration: none; color: var(--text-0);
    font-size: 13px; }
  .place-item:hover { border-color: var(--border-hover); }
  .place-item .rm { cursor: pointer; color: #ff5470; font-weight: 700;
                    padding: 0 4px; }
</style>
</head>
<body>
<a class="back" href="/">← На главную</a>
<h1>Поиск прогноза</h1>
<div class="sub">Введите город, координаты или почтовый индекс</div>

<div id="my-places" style="display:none">
  <h3>⭐ Мои места</h3>
  <div class="place-list" id="place-list"></div>
</div>

<div class="search-box">
  <input type="text" id="q" placeholder="Москва, 55.41 37.90, 190000..."
         onkeydown="if(event.key==='Enter') doSearch()">
  <button onclick="doSearch()">🔍 Найти</button>
</div>

<div class="model-picker">
  <label>Модель:</label>
  <select id="model">
    {% for key, m in models.items() %}
      <option value="{{ key }}">{{ m.name }}</option>
    {% endfor %}
  </select>
</div>

<div id="results"></div>

""" + COMMON_JS + render_top_controls() + """

<script>
  function renderMyPlaces() {
    const list = window.MyPlaces.list();
    const block = document.getElementById('my-places');
    const cont = document.getElementById('place-list');
    if (!list.length) { block.style.display = 'none'; return; }
    block.style.display = 'block';
    cont.innerHTML = list.map(p => {
      const url = '/forecast/point?lat=' + p.lat + '&lon=' + p.lon +
                  '&name=' + encodeURIComponent(p.name) +
                  '&model=' + (p.model || 'gfs') + '&view=table';
      return '<a class="place-item" href="' + url + '">📍 ' + p.name +
             '<span class="rm" onclick="event.preventDefault(); removePlace(' +
             p.lat + ',' + p.lon + ')">✕</span></a>';
    }).join('');
  }
  renderMyPlaces();

  async function doSearch() {
    const q = document.getElementById('q').value.trim();
    if (!q) return;
    const model = document.getElementById('model').value;
    const results = document.getElementById('results');
    results.innerHTML = '<div style="color:var(--accent);padding:20px;">⏳ Поиск...</div>';

    const coordMatch = q.match(/^(-?\\d+\\.?\\d*)[\\s,]+(-?\\d+\\.?\\d*)$/);
    if (coordMatch) {
      const lat = parseFloat(coordMatch[1]);
      const lon = parseFloat(coordMatch[2]);
      if (lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
        window.location.href = '/forecast/point?lat=' + lat + '&lon=' + lon +
          '&name=' + encodeURIComponent(lat + ', ' + lon) + '&model=' + model + '&view=table';
        return;
      }
    }

    try {
      const url = '/api/geocode?q=' + encodeURIComponent(q);
      const resp = await fetch(url);
      const data = await resp.json();

      if (!data.results || data.results.length === 0) {
        results.innerHTML = '<div style="color:var(--text-2);padding:20px;">Ничего не найдено.</div>';
        return;
      }

      let html = '<div class="card"><h2 style="font-size:14px;color:var(--text-1);margin-bottom:10px;">Найдено:</h2>';
      data.results.forEach(p => {
        const label = [p.name, p.admin1, p.country].filter(Boolean).join(', ');
        const url = '/forecast/point?lat=' + p.latitude + '&lon=' + p.longitude +
                    '&name=' + encodeURIComponent(label) + '&model=' + model + '&view=table';
        html += '<a href="' + url + '" style="display:block;padding:12px 16px;margin:6px 0;background:rgba(120,160,255,0.06);border:1px solid var(--border);border-radius:10px;text-decoration:none;color:var(--text-0);">' +
          '📍 <b>' + p.name + '</b> <span style="color:var(--text-2);font-size:12px;">' + label + '</span>' +
          '<div style="color:var(--text-2);font-size:11px;font-family:\\'JetBrains Mono\\',monospace;margin-top:4px;">' + p.latitude + ', ' + p.longitude + '</div>' +
        '</a>';
      });
      html += '</div>';
      results.innerHTML = html;
    } catch (err) {
      results.innerHTML = '<div style="color:#ff5470;padding:20px;">Ошибка: ' + err.message + '</div>';
    }
  }
</script>
</body>
</html>
"""


POINT_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Прогноз — {{ point_name }}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
""" + BASE_STYLE + """
<style>
  .point-info { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 14px 18px; margin-bottom: 16px;
    font-family: 'JetBrains Mono', monospace; font-size: 13px;
    color: var(--text-1); }
  .point-info b { color: var(--accent); }
  .tabs { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
  .tabs a { padding: 9px 16px; border-radius: 10px; text-decoration: none;
    font-size: 13px; font-weight: 500; transition: all 0.2s;
    font-family: 'Inter', sans-serif; }
  .tabs a.active { background: linear-gradient(135deg, #4dabff, #7c5cff); color: #fff;
    box-shadow: 0 4px 20px -4px rgba(77,171,255,0.5); }
  .tabs a.inactive { background: rgba(120,160,255,0.08); color: var(--text-1);
    border: 1px solid var(--border); }
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 20px; margin-bottom: 16px; overflow-x: auto; }
  .card h2 { font-size: 16px; margin: 0 0 14px 0;
             color: var(--accent); font-weight: 600; }
  canvas { max-height: 400px; }
  .chart-tabs { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
  .chart-tabs button { padding: 9px 16px; border-radius: 10px;
    background: rgba(120, 160, 255, 0.08); color: var(--text-1);
    border: 1px solid var(--border); cursor: pointer;
    font-size: 13px; font-weight: 500; font-family: 'Inter', sans-serif; }
  .chart-tabs button.active { background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff; border-color: transparent; }
  .chart-comment { margin-top: 14px; font-size: 12px; color: var(--text-1);
    line-height: 1.6; padding: 12px 16px;
    background: rgba(77,171,255,0.04);
    border-left: 3px solid var(--accent); border-radius: 6px; }
  pre { white-space: pre-wrap; word-wrap: break-word;
    font-family: 'Inter', sans-serif; font-size: 15px;
    line-height: 1.8; margin: 0; color: var(--text-0); }
  table { width: 100%; border-collapse: collapse; font-size: 12px; min-width: 640px; }
  th, td { padding: 8px 6px; text-align: center;
           border-bottom: 1px solid rgba(120, 160, 255, 0.06); }
  th { background: rgba(120, 160, 255, 0.06); color: var(--text-1);
       font-weight: 600; font-size: 11px;
       text-transform: uppercase; letter-spacing: 0.5px; }
  td { color: var(--text-0); font-family: 'JetBrains Mono', monospace; }
  td:first-child { font-family: 'Inter', sans-serif; font-weight: 600; color: var(--accent); }
  td.icon-cell { padding: 2px 4px; }
  td.icon-cell svg { width: 30px; height: 30px; vertical-align: middle; }
  tr.clear td { background: rgba(77,171,255,0.06); }
  tr.mostly-clear td { background: rgba(77,171,255,0.04); }
  tr.partly-cloudy td { background: rgba(120,160,255,0.04); }
  tr.overcast td { background: rgba(120,160,255,0.08); }
  tr.fog td { background: rgba(255,181,71,0.10); }
  tr.rain td { background: rgba(77,171,255,0.10); }
  tr.snow td { background: rgba(180,220,255,0.08); }
  tr.showers td { background: rgba(77,171,255,0.14); }
  tr.snow-showers td { background: rgba(180,220,255,0.12); }
  tr.thunder td { background: rgba(124,92,255,0.14); }
  .add-place { display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 14px; border-radius: 10px; margin-bottom: 14px;
    background: rgba(124,92,255,0.10); color: var(--text-0);
    border: 1px solid rgba(124,92,255,0.25); cursor: pointer;
    font-size: 13px; font-weight: 500; font-family: 'Inter', sans-serif; }
  .add-place:hover { background: rgba(124,92,255,0.20); }
</style>
</head>
<body>

<a class="back" href="/search">← Новый поиск</a>
<h1>{{ point_name }}</h1>
<div class="point-info">
  📍 <b>{{ lat }}, {{ lon }}</b> · модель: <b>{{ model_name }}</b>
</div>

<script id="place-data" type="application/json">
{"name": {{ point_name|tojson }}, "lat": {{ lat }}, "lon": {{ lon }}, "model": {{ model|tojson }}}
</script>
<button class="add-place" onclick="addCurrentPlace()">⭐ В «Мои места»</button>

{% if synoptic %}
<div class="card">
  <h2>🌀 Синоптический анализ</h2>
  {% for ev in synoptic[:10] %}
    <span class="synoptic-badge synoptic-{{ ev.type }}">{{ ev.time[5:16].replace('T', ' ') }} — {{ ev.text }}</span>
  {% endfor %}
</div>
{% endif %}

<div class="tabs">
  <a href="/forecast/point?lat={{ lat }}&lon={{ lon }}&name={{ point_name }}&model={{ model }}&view=table"
     class="{% if view == 'table' %}active{% else %}inactive{% endif %}">📋 Таблица</a>
  <a href="/forecast/point?lat={{ lat }}&lon={{ lon }}&name={{ point_name }}&model={{ model }}&view=text"
     class="{% if view == 'text' %}active{% else %}inactive{% endif %}">📰 Текст</a>
  <a href="/forecast/point?lat={{ lat }}&lon={{ lon }}&name={{ point_name }}&model={{ model }}&view=chart"
     class="{% if view == 'chart' %}active{% else %}inactive{% endif %}">📈 График</a>
  <a href="/alt-verify?lat={{ lat }}&lon={{ lon }}&name={{ point_name }}"
     class="inactive">📋 Матрица</a>
</div>

{% if view == 'table' %}
  {% for day, rows in by_day.items() %}
  <div class="card fade-in">
    <h2>{{ day }}</h2>
    <table>
      <tr>
        <th>Час</th><th></th><th>T°, C</th><th>θ, K</th><th>Ветер, м/с</th><th>Напр.</th>
        <th>Давл., гПа</th><th>Влаж., %</th><th>Осад., мм</th><th>Явление</th>
        <th>K</th><th>⛈</th><th>🌫</th>
      </tr>
      {% for h in rows %}
      <tr class="{{ h.css_class }}">
        <td>{{ h.time[11:16] }}</td>
        <td class="icon-cell">{{ h.icon_svg|safe }}</td>
        <td>{{ h.temp_c }}{{ h.temp_spark|safe }}</td>
        <td>{{ h.theta_k if h.theta_k else '—' }}</td>
        <td>{{ h.wind_ms }}</td>
        <td>{{ h.wind_dir_text }}</td>
        <td>{{ h.pressure_hpa|int if h.pressure_hpa is not none else '—' }}{{ h.press_spark|safe }}</td>
        <td>{{ h.humidity|int if h.humidity is not none else '—' }}</td>
        <td>{{ h.precipitation_mm }}</td>
        <td>{{ h.code_text }}</td>
        <td>{{ h.av_thunder.k if h.av_thunder.k is not none else '—' }}</td>
        <td>{{ h.av_thunder.combined_prob }}%</td>
        <td>{{ h.av_fog.probability }}%</td>
      </tr>
      {% endfor %}
    </table>
  </div>
  {% endfor %}
{% endif %}

{% if view == 'text' %}
  <div class="card fade-in">
    <pre>{{ text }}</pre>
  </div>
{% endif %}

{% if view == 'chart' %}
  <div class="chart-tabs">
    <button class="active" onclick="showMetric('temp', this)">🌡 Температура</button>
    <button onclick="showMetric('theta', this)">🌀 θ</button>
    <button onclick="showMetric('wind', this)">💨 Ветер</button>
    <button onclick="showMetric('precip', this)">💧 Осадки</button>
    <button onclick="showMetric('pressure', this)">📊 Давление</button>
  </div>
  <div class="card fade-in">
    <h2 id="chart-title">Температура, °C</h2>
    <canvas id="chart"></canvas>
    <div class="chart-comment" id="chart-comment"></div>
  </div>
  <script>
    const LABELS = {{ labels_json | safe }};
    const DATA = {{ data_json | safe }};
    const METRICS = {
      temp:     { title: "Температура, °C", comment: "💡 Ход температуры по часам." },
      theta:    { title: "Потенциальная температура, K", comment: "💡 Резкий рост θ указывает на складки." },
      wind:     { title: "Ветер, м/с", comment: "💡 Следите за усилением ветра — признак фронта." },
      precip:   { title: "Осадки, мм", comment: "💡 Осадки дискретны — важны периоды." },
      pressure: { title: "Давление, гПа", comment: "💡 Падение давления = циклон и фронт." },
    };
    Chart.defaults.color = "#a8b4d0";
    Chart.defaults.borderColor = "rgba(120,160,255,0.1)";
    Chart.defaults.font.family = "'Inter', sans-serif";
    let chart = null;
    function renderChart(metricKey) {
      const m = METRICS[metricKey];
      document.getElementById("chart-title").textContent = m.title;
      document.getElementById("chart-comment").textContent = m.comment;
      if (chart) chart.destroy();
      const ctx = document.getElementById("chart").getContext("2d");
      chart = new Chart(ctx, {
        type: "line",
        data: {
          labels: LABELS,
          datasets: [{
            label: m.title, data: DATA[metricKey],
            borderColor: metricKey === "theta" ? "#ff5470" : "#4dabff",
            backgroundColor: metricKey === "theta" ? "rgba(255,84,112,0.15)" : "rgba(77,171,255,0.15)",
            borderWidth: 2.5, tension: 0.4,
            pointRadius: 0, pointHoverRadius: 5, spanGaps: true,
          }]
        },
        options: {
          responsive: true,
          interaction: { mode: "index", intersect: false },
          plugins: {
            legend: { display: false },
            tooltip: { mode: "index", intersect: false,
                       backgroundColor: "rgba(15,21,36,0.95)",
                       borderColor: "rgba(120,160,255,0.3)",
                       borderWidth: 1, padding: 12,
                       titleColor: "#e8eefc", bodyColor: "#a8b4d0" },
          },
          scales: {
            x: { grid: { color: "rgba(120,160,255,0.06)" },
                 ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 12 } },
            y: { grid: { color: "rgba(120,160,255,0.06)" }, beginAtZero: false },
          },
        },
      });
    }
    function showMetric(key, btn) {
      document.querySelectorAll(".chart-tabs button").forEach(b => b.classList.remove("active"));
      if (btn) btn.classList.add("active");
      renderChart(key);
    }
    renderChart("temp");
  </script>
{% endif %}

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


VERIFY_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Проверка моделей — {{ station_name }}</title>
""" + BASE_STYLE + """
<style>
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 20px; margin-bottom: 16px; }
  .date-picker { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 14px 18px; margin-bottom: 16px;
    display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
  .date-picker label { color: var(--text-1); font-size: 13px; font-weight: 500; }
  .date-picker input[type=date] { padding: 10px 14px;
    background: rgba(10, 14, 26, 0.6);
    border: 1px solid var(--border); border-radius: 10px;
    color: var(--text-0); font-family: 'JetBrains Mono', monospace;
    font-size: 14px; outline: none; }
  [data-theme="light"] .date-picker input[type=date] { background: #fff; }
  .date-picker button { padding: 10px 22px; border: none; border-radius: 10px;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff; cursor: pointer; font-size: 14px; font-weight: 600; }
  .date-picker a.btn-history { padding: 10px 22px; border-radius: 10px;
    background: rgba(0,229,160,0.10); color: #00e5a0;
    border: 1px solid rgba(0,229,160,0.3); text-decoration: none;
    font-size: 14px; font-weight: 600; }
  .date-picker a.btn-analyze { padding: 10px 22px; border-radius: 10px;
    background: rgba(124,92,255,0.10); color: #a78bfa;
    border: 1px solid rgba(124,92,255,0.3); text-decoration: none;
    font-size: 14px; font-weight: 600; }
  .date-badge { display: inline-block; padding: 6px 14px; border-radius: 8px;
    background: rgba(0,229,160,0.1); color: #00e5a0;
    font-family: 'JetBrains Mono', monospace; font-size: 13px;
    border: 1px solid rgba(0,229,160,0.25); margin-bottom: 16px; }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  th, td { padding: 14px 12px; text-align: center;
           border-bottom: 1px solid rgba(120,160,255,0.08); }
  th { color: var(--text-1); font-weight: 600; font-size: 11px;
       text-transform: uppercase; letter-spacing: 0.5px;
       background: rgba(120,160,255,0.04); }
  td { font-family: 'JetBrains Mono', monospace; color: var(--text-0); }
  td:first-child { font-family: 'Inter', sans-serif;
                   font-weight: 600; color: var(--accent); text-align: left; }
  .best { color: #00e5a0 !important; font-weight: 700; }
  .src-station { color: #00e5a0; }
  .src-era5 { color: #ffb547; }
  .hint { color: var(--text-2); font-size: 12px; margin-top: 12px;
          padding: 10px 14px; background: rgba(0,229,160,0.04);
          border-left: 3px solid #00e5a0; border-radius: 6px;
          line-height: 1.7; }
  .loading { color: var(--accent); font-size: 13px; text-align: center;
             padding: 20px; font-family: 'JetBrains Mono', monospace; }
</style>
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>Проверка моделей</h1>
<div class="sub">Сравнение прогноза (за сутки) с фактом (станция / ERA5)</div>

<div class="date-picker">
  <label>📅 Дата:</label>
  <input type="date" id="target-date-input"
         value="{{ default_date }}" min="{{ min_date }}">
  <button onclick="loadVerification()">Показать</button>
  <a class="btn-history" href="/verify/{{ station_key }}/history">📉 История за {{ history_days }} дней</a>
  <a class="btn-analyze" href="/analyze/{{ station_key }}">📊 Расширенный анализ</a>
</div>

<div class="date-badge" id="target-date">Загрузка...</div>
<div class="card" id="result-card">
  <div class="loading">⏳ Считаем ошибки...</div>
</div>

<div class="hint">
  <b>MAE</b> — средняя абсолютная ошибка.<br>
  <b>Bias</b> — систематическое смещение (прогноз − факт).<br>
  <b>RMSE</b> — среднеквадратичная ошибка.<br>
  <b>Источник факта:</b> <span class="src-station">станция</span> или <span class="src-era5">ERA5</span>.<br>
  <b>Данные доступны с {{ min_date }}.</b>
</div>

<script>
  const STATION = "{{ station_key }}";
  const DEFAULT_DATE = "{{ default_date }}";

  async function loadVerification() {
    const dateInput = document.getElementById('target-date-input');
    const date = dateInput ? dateInput.value : DEFAULT_DATE;
    const url = '/api/verify/' + STATION + '?date=' + date;
    document.getElementById('result-card').innerHTML =
      '<div class="loading">⏳ Считаем ошибки...</div>';

    try {
      const resp = await fetch(url);
      const data = await resp.json();
      document.getElementById('target-date').textContent = '📅 ' + data.date;

      if (data.results && data.results.length > 0) {
        renderTable(data.results);
      } else {
        document.getElementById('result-card').innerHTML =
          '<div class="loading">Нет данных для проверки.</div>';
      }
    } catch (err) {
      document.getElementById('result-card').innerHTML =
        '<div class="loading">Ошибка: ' + err.message + '</div>';
    }
  }

  function srcClass(source) {
    if (!source) return '';
    if (source.indexOf('станция') === 0) return 'src-station';
    return 'src-era5';
  }

  function renderTable(results) {
    const valid = results.filter(r => r.temp_mae !== undefined);
    const bestMae = valid.length ? Math.min(...valid.map(r => r.temp_mae)) : null;

    let html = '<table><tr>' +
      '<th>Модель</th><th>Источник факта</th><th>T° MAE</th><th>T° RMSE</th><th>T° Bias</th>' +
      '<th>Осад. MAE</th><th>Осад. RMSE</th><th>Часов</th></tr>';

    results.forEach(r => {
      if (r.error) {
        html += '<tr><td>' + (r.name || r.model) + '</td>' +
                '<td colspan="7" style="color:var(--text-2)">' + r.error + '</td></tr>';
        return;
      }
      const isBest = bestMae !== null && r.temp_mae === bestMae;
      html += '<tr>' +
        '<td>' + (r.name || r.model) + '</td>' +
        '<td class="' + srcClass(r.source) + '" style="font-size:11px">' + (r.source || '—') + '</td>' +
        '<td class="' + (isBest ? 'best' : '') + '">' + r.temp_mae + '</td>' +
        '<td>' + r.temp_rmse + '</td>' +
        '<td>' + (r.temp_bias > 0 ? '+' : '') + r.temp_bias + '</td>' +
        '<td>' + (r.prec_mae !== null && r.prec_mae !== undefined ? r.prec_mae : '—') + '</td>' +
        '<td>' + (r.prec_rmse !== null && r.prec_rmse !== undefined ? r.prec_rmse : '—') + '</td>' +
        '<td>' + r.hours + '</td>' +
      '</tr>';
    });

    html += '</table>';
    document.getElementById('result-card').innerHTML = html;
  }

  loadVerification();
</script>

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
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
""" + BASE_STYLE + """
<style>
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 20px; margin-bottom: 16px; }
  .card h2 { font-size: 16px; margin: 0 0 14px 0;
             color: var(--accent); font-weight: 600; }
  canvas { max-height: 420px; }
  .model-legend { display: flex; gap: 16px; flex-wrap: wrap;
                  margin-bottom: 12px; font-size: 12px; }
  .model-legend span { display: inline-flex; align-items: center; gap: 6px;
                       color: var(--text-1); }
  .model-legend i { width: 12px; height: 3px; border-radius: 2px;
                    display: inline-block; }
  .loading { color: var(--accent); font-size: 13px; text-align: center;
             padding: 20px; font-family: 'JetBrains Mono', monospace; }
  .info { color: var(--text-2); font-size: 12px;
          padding: 10px 14px; background: rgba(77,171,255,0.05);
          border-left: 3px solid var(--accent); border-radius: 6px;
          margin-bottom: 14px; line-height: 1.7; }
</style>
</head>
<body>

<a class="back" href="/verify/{{ station_key }}">← К проверке</a>
<h1>История ошибок</h1>
<div class="sub">{{ station_name }} · последние {{ history_days }} дней</div>

<div class="info">
  💡 График показывает, как менялась ошибка прогноза (за сутки) во времени.
</div>

<div class="card fade-in">
  <h2>MAE температуры, °C</h2>
  <div class="model-legend" id="legend"></div>
  <canvas id="chart-mae"></canvas>
</div>

<div class="card fade-in">
  <h2>Bias температуры, °C</h2>
  <canvas id="chart-bias"></canvas>
</div>

<script>
  const STATION = "{{ station_key }}";
  const HISTORY_DAYS = {{ history_days }};
  const COLORS = { gfs: "#4dabff", ecmwf: "#00e5a0", icon: "#ffb547" };

  async function load() {
    try {
      const resp = await fetch('/api/verify/' + STATION + '/history?days=' + HISTORY_DAYS);
      const data = await resp.json();
      if (data.error) throw new Error(data.error);
      render(data);
    } catch (e) {
      document.getElementById('chart-mae').outerHTML =
        '<div class="loading">Ошибка: ' + e.message + '</div>';
    }
  }

  function render(data) {
    const dates = data.days.map(d => d.date);
    const sources = data.days.map(d => {
      const first = Object.keys(d.models)[0];
      const f = d.models[first];
      return f && f.source ? f.source : '—';
    });

    let legend = '';
    Object.keys(data.models).forEach(function(k) {
      legend += '<span><i style="background:' + (COLORS[k] || '#4dabff') + '"></i>' +
                data.models[k] + '</span>';
    });
    document.getElementById('legend').innerHTML = legend;

    const maeDatasets = Object.keys(data.models).map(function(k) {
      return { label: data.models[k], data: data.series[k].mae,
        borderColor: COLORS[k] || '#4dabff', backgroundColor: 'transparent',
        borderWidth: 2.5, tension: 0.35,
        pointRadius: 4, pointHoverRadius: 6, spanGaps: true };
    });

    new Chart(document.getElementById('chart-mae'), {
      type: 'line',
      data: { labels: dates, datasets: maeDatasets },
      options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(15,21,36,0.95)',
            borderColor: 'rgba(120,160,255,0.3)',
            borderWidth: 1, padding: 12,
            callbacks: {
              afterBody: function(items) {
                return 'Источник факта: ' + sources[items[0].dataIndex];
              }
            }
          }
        },
        scales: {
          x: { grid: { color: 'rgba(120,160,255,0.06)' } },
          y: { grid: { color: 'rgba(120,160,255,0.06)' }, beginAtZero: true },
        },
      },
    });

    const biasDatasets = Object.keys(data.models).map(function(k) {
      return { label: data.models[k], data: data.series[k].bias,
        borderColor: COLORS[k] || '#4dabff', backgroundColor: 'transparent',
        borderWidth: 2.5, tension: 0.35,
        pointRadius: 4, pointHoverRadius: 6, spanGaps: true };
    });

    new Chart(document.getElementById('chart-bias'), {
      type: 'line',
      data: { labels: dates, datasets: biasDatasets },
      options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(15,21,36,0.95)',
            borderColor: 'rgba(120,160,255,0.3)',
            borderWidth: 1, padding: 12,
          }
        },
        scales: {
          x: { grid: { color: 'rgba(120,160,255,0.06)' } },
          y: { grid: { color: 'rgba(120,160,255,0.06)' } },
        },
      },
    });
  }

  load();
</script>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


ANALYZE_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Статистический анализ — {{ station_name }}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
""" + BASE_STYLE + """
<style>
  .controls { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 14px 18px; margin-bottom: 16px;
    display: flex; flex-wrap: wrap; gap: 14px; align-items: center; }
  .controls label { color: var(--text-1); font-size: 13px; font-weight: 500; }
  .controls select {
    padding: 10px 14px;
    background: rgba(10, 14, 26, 0.6);
    border: 1px solid var(--border); border-radius: 10px;
    color: var(--text-0); font-size: 14px; outline: none;
    font-family: 'Inter', sans-serif;
  }
  [data-theme="light"] .controls select { background: #fff; }
  .controls button {
    padding: 10px 22px; border: none; border-radius: 10px;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff; cursor: pointer; font-size: 14px; font-weight: 600;
  }
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 20px; margin-bottom: 16px; }
  .card h2 { font-size: 16px; margin: 0 0 14px 0;
             color: var(--accent); font-weight: 600; }
  .metrics-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 14px;
  }
  .metric { padding: 14px 16px; border-radius: 12px;
    background: rgba(120,160,255,0.06);
    border: 1px solid var(--border); }
  .metric .label { font-size: 11px; color: var(--text-2);
                   text-transform: uppercase; letter-spacing: 0.5px;
                   font-weight: 600; }
  .metric .value { font-size: 22px; font-weight: 700;
                   color: var(--text-0); margin-top: 6px;
                   font-family: 'JetBrains Mono', monospace; }
  .metric .hint  { font-size: 11px; color: var(--text-2); margin-top: 4px; }
  .metric.good .value { color: #00e5a0; }
  .metric.bad  .value { color: #ff5470; }
  canvas { max-height: 380px; }
  .loading { color: var(--accent); font-size: 13px; text-align: center;
             padding: 20px; font-family: 'JetBrains Mono', monospace; }
  .err { color: #ff5470; padding: 20px; text-align: center; }
</style>
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>Статистический анализ</h1>
<div class="sub">{{ station_name }} · расширенные метрики прогноза vs факта</div>

<div class="controls">
  <label>Модель:</label>
  <select id="model-select">
    {% for k, m in models.items() %}
      <option value="{{ k }}">{{ m.name }}</option>
    {% endfor %}
  </select>
  <label>Период:</label>
  <select id="days-select">
    <option value="7">7 дней</option>
    <option value="14" selected>14 дней</option>
    <option value="30">30 дней</option>
  </select>
  <button onclick="loadAnalysis()">📊 Анализировать</button>
</div>

<div id="result">
  <div class="loading">Выберите параметры и нажмите «Анализировать»…</div>
</div>

<script>
  const STATION = "{{ station_key }}";

  async function loadAnalysis() {
    const model = document.getElementById('model-select').value;
    const days = document.getElementById('days-select').value;
    const result = document.getElementById('result');
    result.innerHTML = '<div class="loading">⏳ Считаем метрики…</div>';

    try {
      const url = '/api/analyze/' + STATION + '?model=' + model + '&days=' + days;
      const resp = await fetch(url);
      const data = await resp.json();
      if (data.error) {
        result.innerHTML = '<div class="err">' + data.error + '</div>';
        return;
      }
      render(data);
    } catch (e) {
      result.innerHTML = '<div class="err">Ошибка: ' + e.message + '</div>';
    }
  }

  function fmt(v, suffix) {
    if (v === null || v === undefined) return '—';
    return v + (suffix || '');
  }

  function metricClass(value, good, bad) {
    if (value === null || value === undefined) return '';
    if (good !== undefined && value <= good) return 'good';
    if (bad !== undefined && value >= bad) return 'bad';
    return '';
  }

  function render(data) {
    const t = data.temp;
    const p = data.precip;

    let html = '';
    html += '<div class="card fade-in">';
    html += '<h2>🌡 Температура — ' + data.model_name + '</h2>';
    html += '<div style="color:var(--text-2);font-size:12px;margin-bottom:14px;">'
          + 'Часов: <b style="color:var(--text-0)">' + data.hours_total + '</b></div>';
    html += '<div class="metrics-grid">';
    html += '<div class="metric ' + metricClass(t.mae, 1.0, 2.5) + '">'
          + '<div class="label">MAE</div>'
          + '<div class="value">' + fmt(t.mae, '°C') + '</div></div>';
    html += '<div class="metric ' + metricClass(t.rmse, 1.5, 3.0) + '">'
          + '<div class="label">RMSE</div>'
          + '<div class="value">' + fmt(t.rmse, '°C') + '</div></div>';
    html += '<div class="metric">'
          + '<div class="label">Bias</div>'
          + '<div class="value">' + fmt(t.bias, '°C') + '</div></div>';
    html += '<div class="metric">'
          + '<div class="label">Корреляция</div>'
          + '<div class="value">' + fmt(t.corr) + '</div></div>';
    html += '<div class="metric">'
          + '<div class="label">R²</div>'
          + '<div class="value">' + fmt(t.r2) + '</div></div>';
    html += '<div class="metric">'
          + '<div class="label">MAPE</div>'
          + '<div class="value">' + fmt(t.mape, '%') + '</div></div>';
    html += '</div>';
    html += '<div class="metrics-grid" style="margin-top:14px;">';
    html += '<div class="metric"><div class="label">P50</div>'
          + '<div class="value">' + fmt(t.p50, '°C') + '</div></div>';
    html += '<div class="metric"><div class="label">P90</div>'
          + '<div class="value">' + fmt(t.p90, '°C') + '</div></div>';
    html += '<div class="metric"><div class="label">P95</div>'
          + '<div class="value">' + fmt(t.p95, '°C') + '</div></div>';
    html += '</div></div>';

    html += '<div class="card fade-in"><h2>🔵 Прогноз vs факт</h2>'
          + '<canvas id="scatter"></canvas></div>';
    html += '<div class="card fade-in"><h2>📊 Распределение ошибок</h2>'
          + '<canvas id="histogram"></canvas></div>';

    html += '<div class="card fade-in">';
    html += '<h2>💧 Осадки — совпадение явлений</h2>';
    html += '<div class="metrics-grid">';
    html += '<div class="metric"><div class="label">Факт, часов</div>'
          + '<div class="value">' + p.fact_hours + '</div></div>';
    html += '<div class="metric"><div class="label">Прогноз, часов</div>'
          + '<div class="value">' + p.fcst_hours + '</div></div>';
    html += '<div class="metric good"><div class="label">Совпало</div>'
          + '<div class="value">' + p.hits + '</div></div>';
    html += '<div class="metric bad"><div class="label">Пропуск</div>'
          + '<div class="value">' + p.misses + '</div></div>';
    html += '<div class="metric bad"><div class="label">Ложных</div>'
          + '<div class="value">' + p.false_alarms + '</div></div>';
    html += '</div>';
    html += '<div class="metrics-grid" style="margin-top:14px;">';
    html += '<div class="metric"><div class="label">Hit rate</div>'
          + '<div class="value">' + fmt(p.hit_rate) + '</div></div>';
    html += '<div class="metric"><div class="label">Precision</div>'
          + '<div class="value">' + fmt(p.precision) + '</div></div>';
    html += '<div class="metric"><div class="label">F1-score</div>'
          + '<div class="value">' + fmt(p.f1) + '</div></div>';
    html += '</div></div>';

    document.getElementById('result').innerHTML = html;

    new Chart(document.getElementById('scatter').getContext('2d'), {
      type: 'scatter',
      data: {
        datasets: [{
          label: 'прогноз vs факт',
          data: data.scatter,
          backgroundColor: 'rgba(77,171,255,0.6)',
          borderColor: '#4dabff',
          pointRadius: 3, pointHoverRadius: 5,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { title: { display: true, text: 'факт, °C', color: '#a8b4d0' },
               grid: { color: 'rgba(120,160,255,0.06)' } },
          y: { title: { display: true, text: 'прогноз, °C', color: '#a8b4d0' },
               grid: { color: 'rgba(120,160,255,0.06)' } },
        }
      }
    });

    new Chart(document.getElementById('histogram').getContext('2d'), {
      type: 'bar',
      data: {
        labels: data.histogram.map(b => b.x + ''),
        datasets: [{
          data: data.histogram.map(b => b.count),
          backgroundColor: data.histogram.map(b =>
            b.x < 0 ? 'rgba(77,171,255,0.6)' : 'rgba(255,181,71,0.6)'),
          borderColor: data.histogram.map(b =>
            b.x < 0 ? '#4dabff' : '#ffb547'),
          borderWidth: 1.5,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { title: { display: true, text: 'ошибка, °C', color: '#a8b4d0' } },
          y: { title: { display: true, text: 'часов', color: '#a8b4d0' },
               beginAtZero: true },
        }
      }
    });
  }

  loadAnalysis();
</script>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


AVIATION_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Авиационные прогнозы — {{ station_name }}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
""" + BASE_STYLE + """
<style>
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 20px; margin-bottom: 16px; overflow-x: auto; }
  .card h2 { font-size: 16px; margin: 0 0 14px 0;
             color: var(--accent); font-weight: 600; }
  .controls { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 14px 18px; margin-bottom: 16px;
    display: flex; flex-wrap: wrap; gap: 14px; align-items: center; }
  .controls label { color: var(--text-1); font-size: 13px; }
  .controls select { padding: 10px 14px;
    background: rgba(10, 14, 26, 0.6); border: 1px solid var(--border);
    border-radius: 10px; color: var(--text-0); font-size: 14px; outline: none; }
  [data-theme="light"] .controls select { background: #fff; }
  .controls button { padding: 10px 22px; border: none; border-radius: 10px;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff; cursor: pointer; font-size: 14px; font-weight: 600; }
  table { width: 100%; border-collapse: collapse; font-size: 12px;
          min-width: 900px; }
  th, td { padding: 8px 6px; text-align: center;
           border-bottom: 1px solid rgba(120, 160, 255, 0.06); }
  th { background: rgba(120, 160, 255, 0.06); color: var(--text-1);
       font-weight: 600; font-size: 11px;
       text-transform: uppercase; letter-spacing: 0.5px; }
  td { color: var(--text-0); font-family: 'JetBrains Mono', monospace; }
  td:first-child { font-family: 'Inter', sans-serif; font-weight: 600;
                   color: var(--accent); }
  tr.risk-none   td { background: rgba(120, 160, 255, 0.02); }
  tr.risk-weak   td { background: rgba(77, 171, 255, 0.06); }
  tr.risk-mod    td { background: rgba(255, 181, 71, 0.10); }
  tr.risk-strong td { background: rgba(255, 84, 112, 0.12); }
  tr.risk-vstrong td { background: rgba(255, 84, 112, 0.20); }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 5px;
           font-size: 10px; font-weight: 700; }
  .badge-none   { background: rgba(120,160,255,0.10); color: var(--text-2); }
  .badge-weak   { background: rgba(77,171,255,0.15); color: #4dabff; }
  .badge-mod    { background: rgba(255,181,71,0.15); color: #ffb547; }
  .badge-strong { background: rgba(255,84,112,0.15); color: #ff5470; }
  .badge-vstrong{ background: rgba(255,84,112,0.30); color: #ff5470; }
  .legend { font-size: 12px; color: var(--text-2); line-height: 1.8;
            padding: 12px 16px; background: rgba(77,171,255,0.04);
            border-left: 3px solid var(--accent); border-radius: 6px;
            margin-top: 12px; }
  .legend code { font-family: 'JetBrains Mono', monospace;
                 background: rgba(120,160,255,0.08);
                 padding: 2px 6px; border-radius: 4px;
                 color: var(--accent); font-size: 11px; }
  canvas { max-height: 380px; }
  .loading { color: var(--accent); text-align: center; padding: 20px;
             font-family: 'JetBrains Mono', monospace; font-size: 13px; }
  .err { color: #ff5470; padding: 20px; text-align: center; }
</style>
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>Авиационные прогнозы</h1>
<div class="sub">
  {{ station_name }} · методы по Богаткину: Вайтинг, LI, CAPE, Кирюхин
</div>

<div class="controls">
  <label>Модель:</label>
  <select id="model-select">
    {% for k, m in models.items() %}
      <option value="{{ k }}">{{ m.name }}</option>
    {% endfor %}
  </select>
  <button onclick="loadAviation()">🧭 Рассчитать</button>
</div>

<div id="result">
  <div class="loading">Загрузка…</div>
</div>

<script>
  const STATION = "{{ station_key }}";

  async function loadAviation() {
    const model = document.getElementById('model-select').value;
    const result = document.getElementById('result');
    result.innerHTML = '<div class="loading">⏳ Считаем…</div>';

    try {
      const url = '/api/aviation/' + model + '/' + STATION;
      const resp = await fetch(url);
      const data = await resp.json();
      if (data.error) {
        result.innerHTML = '<div class="err">' + data.error + '</div>';
        return;
      }
      render(data);
    } catch (e) {
      result.innerHTML = '<div class="err">Ошибка: ' + e.message + '</div>';
    }
  }

  function badge(level, text) {
    const safeLevel = (level || 'none').replace(/\\s+/g, '-');
    return '<span class="badge badge-' + safeLevel + '">' + (text || '—') + '</span>';
  }

  function rowClass(prob) {
    if (prob === null || prob === undefined) return 'risk-none';
    if (prob < 20) return 'risk-none';
    if (prob < 40) return 'risk-weak';
    if (prob < 60) return 'risk-mod';
    if (prob < 80) return 'risk-strong';
    return 'risk-vstrong';
  }

  function render(data) {
    let html = '';

    html += '<div class="card fade-in"><h2>📅 Сводка по дням</h2>';
    html += '<table><tr><th>День</th><th>Часы с грозой</th>'
          + '<th>Часы с туманом</th><th>Макс. K</th>'
          + '<th>Мин. LI</th><th>Макс. CAPE</th></tr>';
    data.days_summary.forEach(d => {
      html += '<tr>'
        + '<td>' + d.date + '</td>'
        + '<td>' + (d.thunder_count || '—') + '</td>'
        + '<td>' + (d.fog_count || '—') + '</td>'
        + '<td>' + (d.max_k !== null ? d.max_k : '—') + '</td>'
        + '<td>' + (d.min_li !== null ? d.min_li : '—') + '</td>'
        + '<td>' + (d.max_cape !== null ? d.max_cape : '—') + '</td>'
      + '</tr>';
    });
    html += '</table></div>';

    html += '<div class="card fade-in"><h2>📈 Эволюция индексов</h2>'
          + '<canvas id="chart-idx"></canvas></div>';

    html += '<div class="card fade-in"><h2>🧭 Часовые значения</h2>';
    html += '<table><tr>'
          + '<th>Час</th><th>T850</th><th>Td850</th>'
          + '<th>T700</th><th>Td700</th><th>T500</th>'
          + '<th>K</th><th>LI</th><th>CAPE</th>'
          + '<th>Гроза</th><th>%</th>'
          + '<th>Туман</th><th>%</th>'
          + '</tr>';

    data.hours.forEach(h => {
      const t = h.av_thunder || {};
      const f = h.av_fog || {};
      const prob = t.combined_prob || 0;
      html += '<tr class="' + rowClass(prob) + '">'
        + '<td>' + h.time + '</td>'
        + '<td>' + (h.t850 !== null && h.t850 !== undefined ? h.t850 : '—') + '</td>'
        + '<td>' + (h.td850 !== null && h.td850 !== undefined ? h.td850 : '—') + '</td>'
        + '<td>' + (h.t700 !== null && h.t700 !== undefined ? h.t700 : '—') + '</td>'
        + '<td>' + (h.td700 !== null && h.td700 !== undefined ? h.td700 : '—') + '</td>'
        + '<td>' + (h.t500 !== null && h.t500 !== undefined ? h.t500 : '—') + '</td>'
        + '<td>' + (t.k !== null && t.k !== undefined ? t.k : '—') + '</td>'
        + '<td>' + (t.li !== null && t.li !== undefined ? t.li : '—') + '</td>'
        + '<td>' + (t.cape !== null && t.cape !== undefined ? t.cape : '—') + '</td>'
        + '<td>' + badge(t.combined_level, t.combined_level) + '</td>'
        + '<td>' + (t.combined_prob || '—') + '</td>'
        + '<td>' + badge(f.level, f.level) + '</td>'
        + '<td>' + (f.probability || '—') + '</td>'
      + '</tr>';
    });
    html += '</table>';

    html += '<div class="legend">'
      + '<b>Метод Вайтинга:</b> <code>K = 2·T850 − T500 − D850 − D700</code><br>'
      + '<b>LI</b> — lifted index<br>'
      + '<b>CAPE</b> — доступная энергия конвекции (Дж/кг)<br>'
      + '<b>Сводная вероятность грозы</b> — LI×0.4 + CAPE×0.35 + K×0.25<br>'
      + '<b>Туман:</b> T−Td ≤ 2°C, ветер 0.5–3 м/с, облачность < 30%, 0–9 МСК, RH ≥ 90%'
      + '</div></div>';

    document.getElementById('result').innerHTML = html;

    new Chart(document.getElementById('chart-idx').getContext('2d'), {
      type: 'line',
      data: {
        labels: data.hours.map(h => h.time),
        datasets: [
          { label: 'K (Вайтинг)',
            data: data.hours.map(h => h.av_thunder && h.av_thunder.k),
            borderColor: '#ffb547', backgroundColor: 'transparent',
            borderWidth: 2.5, tension: 0.4, pointRadius: 0, spanGaps: true },
          { label: 'CAPE / 50',
            data: data.hours.map(h => h.av_thunder && h.av_thunder.cape !== null
              ? Math.round(h.av_thunder.cape / 50) : null),
            borderColor: '#4dabff', backgroundColor: 'transparent',
            borderWidth: 2.5, tension: 0.4, pointRadius: 0, spanGaps: true },
          { label: 'LI (инвертированный)',
            data: data.hours.map(h => h.av_thunder && h.av_thunder.li !== null
              ? -h.av_thunder.li : null),
            borderColor: '#00e5a0', backgroundColor: 'transparent',
            borderWidth: 2.5, tension: 0.4, pointRadius: 0, spanGaps: true },
        ]
      },
      options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { labels: { color: '#a8b4d0' } },
          tooltip: { backgroundColor: 'rgba(15,21,36,0.95)',
                     borderColor: 'rgba(120,160,255,0.3)',
                     borderWidth: 1, padding: 12 },
        },
        scales: {
          x: { grid: { color: 'rgba(120,160,255,0.06)' },
               ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 12 } },
          y: { grid: { color: 'rgba(120,160,255,0.06)' } },
        },
      },
    });
  }

  loadAviation();
</script>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ============================================================
# МАТРИЦА АЛЬТЕРНАТИВНЫХ ПРОГНОЗОВ
# ============================================================
ALT_VERIFY_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Матрица прогнозов — {{ title }}</title>
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
""" + BASE_STYLE + """
<style>
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 20px; margin-bottom: 16px; overflow-x: auto; }
  .card h2 { font-size: 16px; margin: 0 0 14px 0;
             color: var(--accent); font-weight: 600; }
  .controls { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 14px 18px; margin-bottom: 16px;
    display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
  .controls label { color: var(--text-1); font-size: 13px; font-weight: 500; }
  .controls select, .controls input[type=date] {
    padding: 10px 14px;
    background: rgba(10, 14, 26, 0.6);
    border: 1px solid var(--border); border-radius: 10px;
    color: var(--text-0); font-size: 14px; outline: none;
    font-family: 'Inter', sans-serif;
  }
  [data-theme="light"] .controls select,
  [data-theme="light"] .controls input[type=date] { background: #fff; }
  .controls button {
    padding: 10px 22px; border: none; border-radius: 10px;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff; cursor: pointer; font-size: 14px; font-weight: 600;
  }
  .station-info {
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 14px 18px; margin-bottom: 16px;
    font-size: 13px; line-height: 1.7;
    display: flex; flex-wrap: wrap; align-items: center;
    justify-content: space-between; gap: 14px;
  }
  .station-info .src-body { flex: 1 1 auto; }
  .station-info .src-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
  .station-info .src-detail { color: var(--text-2); font-size: 12px; }
  .station-info .src-good { color: #00e5a0; }
  .station-info .src-warn { color: #ffb547; }
  .station-info button {
    padding: 8px 16px; border-radius: 8px; cursor: pointer;
    background: rgba(0,229,160,0.10); color: #00e5a0;
    border: 1px solid rgba(0,229,160,0.3);
    font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 500;
    transition: all 0.2s;
  }
  .station-info button:hover { background: rgba(0,229,160,0.20); }
  .station-info button:disabled {
    opacity: 0.5; cursor: not-allowed; background: rgba(120,160,255,0.06);
    color: var(--text-2); border-color: var(--border);
  }
  .matrix { display: grid; grid-template-columns: 90px 1fr 1fr 70px;
            gap: 1px; background: var(--border);
            border: 1px solid var(--border); border-radius: 12px;
            overflow: hidden; margin-bottom: 14px; max-width: 540px; }
  .matrix div { background: var(--bg-1); padding: 12px 10px;
                text-align: center; font-family: 'JetBrains Mono', monospace;
                font-size: 14px; }
  .matrix .hdr { background: rgba(120,160,255,0.08);
                 color: var(--text-1); font-weight: 700;
                 font-size: 11px; font-family: 'Inter', sans-serif;
                 text-transform: uppercase; letter-spacing: 0.5px; }
  .matrix .hit  { background: rgba(0,229,160,0.15); color: #00e5a0;
                  font-weight: 700; }
  .matrix .miss { background: rgba(255,181,71,0.15); color: #ffb547;
                  font-weight: 700; }
  .matrix .false { background: rgba(255,84,112,0.15); color: #ff5470;
                   font-weight: 700; }
  .metrics-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
    gap: 10px; margin-top: 12px;
  }
  .metric { padding: 10px 12px; border-radius: 10px;
    background: rgba(120,160,255,0.06);
    border: 1px solid var(--border); }
  .metric .label { font-size: 11px; color: var(--text-2);
                   text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
  .metric .value { font-size: 18px; font-weight: 700;
                   color: var(--text-0); margin-top: 6px;
                   font-family: 'JetBrains Mono', monospace; }
  .metric.good .value { color: #00e5a0; }
  .metric.bad .value { color: #ff5470; }
  table.cmp { width: 100%; border-collapse: collapse; font-size: 13px; }
  table.cmp th, table.cmp td { padding: 10px 12px; text-align: center;
    border-bottom: 1px solid var(--border); }
  table.cmp th { background: rgba(120,160,255,0.06);
    color: var(--text-1); font-weight: 600; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.5px; }
  table.cmp td:first-child { text-align: left; font-weight: 600;
    color: var(--accent); font-family: 'Inter', sans-serif; }
  table.cmp td { font-family: 'JetBrains Mono', monospace; }
  .formula { font-size: 12px; color: var(--text-2); line-height: 1.8;
    padding: 12px 16px; background: rgba(77,171,255,0.04);
    border-left: 3px solid var(--accent); border-radius: 6px;
    margin-top: 12px; font-family: 'JetBrains Mono', monospace; }
  .loading { color: var(--accent); text-align: center; padding: 20px;
             font-family: 'JetBrains Mono', monospace; font-size: 13px; }
  .err { color: #ff5470; padding: 20px; text-align: center; }
</style>
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>Матрица альтернативных прогнозов</h1>
<div class="sub">{{ title }} · критерии успешности по Хандожко</div>

<div class="controls">
  <label>Модель:</label>
  <select id="model-select">
    {% for k, m in models.items() %}
      <option value="{{ k }}">{{ m.name }}</option>
    {% endfor %}
  </select>
  <label>Явление:</label>
  <select id="phenomenon-select">
    {% for k, p in phenomena.items() %}
      <option value="{{ k }}" {% if k == phenomenon %}selected{% endif %}>
        {{ p.name }} ({{ p.unit }})
      </option>
    {% endfor %}
  </select>
  <label>С:</label>
  <input type="date" id="start-date" value="{{ start_date }}">
  <label>По:</label>
  <input type="date" id="end-date" value="{{ end_date }}">
  <button onclick="loadMatrix()">📊 Рассчитать</button>
  <button onclick="downloadPNG()" id="png-btn" style="display:none;
          background: rgba(124,92,255,0.10); color: #a78bfa;
          border: 1px solid rgba(124,92,255,0.3);">
    📸 Скачать PNG
  </button>
</div>

<div id="station-info" class="station-info" style="display:none;"></div>

<div id="result">
  <div class="loading">Выберите параметры и нажмите «Рассчитать»…</div>
</div>

<script>
  const STATION = "{{ station_key }}";
  const LAT = {{ lat }};
  const LON = {{ lon }};

  let forceStation = false;

  async function loadMatrix() {
    const phenomenon = document.getElementById('phenomenon-select').value;
    const model = document.getElementById('model-select').value;
    const start = document.getElementById('start-date').value;
    const end = document.getElementById('end-date').value;
    const result = document.getElementById('result');

    if (!start || !end) {
      result.innerHTML = '<div class="err">Укажите даты</div>';
      return;
    }
    if (start > end) {
      result.innerHTML = '<div class="err">Дата начала позже даты конца</div>';
      return;
    }

    result.innerHTML = '<div class="loading">⏳ Считаем матрицы…</div>';

    try {
      const url = '/api/alt-verify?lat=' + LAT + '&lon=' + LON +
                  '&phenomenon=' + phenomenon +
                  '&model=' + model +
                  '&start=' + start + '&end=' + end +
                  '&force_station=' + (forceStation ? '1' : '0');
      const resp = await fetch(url);
      const data = await resp.json();
      if (data.error) {
        result.innerHTML = '<div class="err">' + data.error + '</div>';
        return;
      }
      renderStationInfo(data);
      render(data);
    } catch (e) {
      result.innerHTML = '<div class="err">Ошибка: ' + e.message + '</div>';
    }
  }

  function renderStationInfo(data) {
    const box = document.getElementById('station-info');
    if (!data.station) { box.style.display = 'none'; return; }

    const s = data.station;
    const src = data.sources_used || {};
    const era5Count = src['ERA5'] || 0;
    const stationCount = Object.keys(src)
      .filter(k => k !== 'ERA5')
      .reduce((acc, k) => acc + src[k], 0);

    let icon, statusClass, statusText, detail;
    if (s.available) {
      icon = '🟢';
      statusClass = 'src-good';
      statusText = 'Источник факта: станция «' + (s.name || '—') + '»';
      detail = 'Расстояние: ' + (s.distance_km !== null ? s.distance_km + ' км' : '—') +
               ' · Использовано: ' + stationCount + ' из ' + (stationCount + era5Count) + ' дней';
    } else {
      icon = '🟡';
      statusClass = 'src-warn';
      statusText = 'Источник факта: ERA5 (реанализ)';
      detail = 'Причина: ' + (s.reason || 'станция недоступна') +
               ' · Использовано: ' + era5Count + ' дней';
    }

    let html = '<div class="src-body">' +
      '<div class="src-title ' + statusClass + '">' + icon + ' ' + statusText + '</div>' +
      '<div class="src-detail">' + detail + '</div>' +
    '</div>';

    if (!s.available && s.meteostat_available && s.distance_km !== null) {
      html += '<button onclick="tryForceStation()">🔍 Попробовать станцию всё равно</button>';
    } else if (!s.available && !s.meteostat_available) {
      html += '<button disabled>Meteostat не установлен на сервере</button>';
    } else if (forceStation && s.available) {
      html += '<button onclick="resetForceStation()">↩️ Вернуться к авто-выбору</button>';
    }

    box.innerHTML = html;
    box.style.display = 'flex';
  }

  function tryForceStation() {
    forceStation = true;
    loadMatrix();
  }

  function resetForceStation() {
    forceStation = false;
    loadMatrix();
  }

  function fmt(v) {
    if (v === null || v === undefined) return '—';
    return v.toFixed(3);
  }

  function pct(v) {
    if (v === null || v === undefined) return '—';
    return (v * 100).toFixed(1) + '%';
  }

  function classFor(v, good, bad) {
    if (v === null || v === undefined) return '';
    if (good !== undefined && v >= good) return 'good';
    if (bad !== undefined && v <= bad) return 'bad';
    return '';
  }

  function matrixBlock(title, color, mm) {
    const mc = mm.contingency;
    return '<div class="card fade-in">'
      + '<h2 style="color:' + color + '">' + title + '</h2>'
      + '<div class="matrix">'
      + '<div class="hdr"></div>'
      + '<div class="hdr">П</div>'
      + '<div class="hdr">П̄</div>'
      + '<div class="hdr">Σ</div>'
      + '<div class="hdr">Ф</div>'
      + '<div class="hit">' + mc.n11 + '</div>'
      + '<div class="miss">' + mc.n12 + '</div>'
      + '<div>' + mc.n10 + '</div>'
      + '<div class="hdr">Ф̄</div>'
      + '<div class="false">' + mc.n21 + '</div>'
      + '<div class="hit">' + mc.n22 + '</div>'
      + '<div>' + mc.n20 + '</div>'
      + '<div class="hdr">Σ</div>'
      + '<div>' + mc.n01 + '</div>'
      + '<div>' + mc.n02 + '</div>'
      + '<div>' + mc.N + '</div>'
      + '</div>'
      + '<div class="metrics-grid">'
      + '<div class="metric ' + classFor(mm.p, 0.9, 0.7) + '">'
      + '<div class="label">p</div>'
      + '<div class="value">' + pct(mm.p) + '</div></div>'
      + '<div class="metric ' + classFor(mm.H, 0.8, 0.5) + '">'
      + '<div class="label">H</div>'
      + '<div class="value">' + fmt(mm.H) + '</div></div>'
      + '<div class="metric ' + classFor(mm.Q, 0.8, 0.5) + '">'
      + '<div class="label">Q</div>'
      + '<div class="value">' + fmt(mm.Q) + '</div></div>'
      + '<div class="metric"><div class="label">v</div>'
      + '<div class="value">' + fmt(mm.v) + '</div></div>'
      + '<div class="metric"><div class="label">τ</div>'
      + '<div class="value">' + fmt(mm.tau) + '</div></div>'
      + '<div class="metric"><div class="label">A</div>'
      + '<div class="value">' + fmt(mm.A) + '</div></div>'
      + '</div>'
      + '</div>';
  }

  function render(data) {
    const m = data.methodical;
    const inp = data.inertial;
    const rnd = data.random;
    const clim = data.climatological;

    let html = '';

    html += '<div class="card fade-in">';
    html += '<h2>📋 Параметры расчёта</h2>';
    html += '<div style="color:var(--text-1);font-size:13px;line-height:1.9;">'
          + 'Явление: <b>' + data.phenomenon_name + '</b><br>'
          + 'Модель: <b>' + data.model_name + '</b><br>'
          + 'Период: <b>' + data.start + ' … ' + data.end + '</b> '
          + '(' + data.dates_used + ' дней, ' + data.hours_total + ' часов)'
          + '</div>';
    html += '</div>';

    html += matrixBlock('📘 Методический прогноз (' + data.model_name + ')', '#00e5a0', m);
    if (inp) html += matrixBlock('⚙️ Инерционный прогноз (персистентность)', '#ffb547', inp);
    if (rnd) html += matrixBlock('🎲 Случайный прогноз (мат. ожидание)', '#a78bfa', rnd);
    if (clim) {
      html += matrixBlock(
        '📗 Климатологический прогноз (норма за ' +
        (data.climate_years || 5) + ' лет)',
        '#4dabff', clim
      );
    }

    html += '<div class="card fade-in">';
    html += '<h2>📊 Сводная таблица критериев</h2>';
    html += '<table class="cmp"><tr>'
          + '<th>Критерий</th>'
          + '<th>Методический</th>'
          + '<th>Инерционный</th>'
          + '<th>Случайный</th>'
          + '<th>Климатологический</th>'
          + '<th>Δ (метод − инерц.)</th>'
          + '</tr>';

    const rows = [
      ['p (оправдываемость)', m.p, inp ? inp.p : null, rnd ? rnd.p : null, clim ? clim.p : null, 'pct'],
      ['H (надёжность)', m.H, inp ? inp.H : null, rnd ? rnd.H : null, clim ? clim.H : null, 'raw'],
      ['Q (точность)', m.Q, inp ? inp.Q : null, rnd ? rnd.Q : null, clim ? clim.Q : null, 'raw'],
      ['v (информ. отношение)', m.v, inp ? inp.v : null, rnd ? rnd.v : null, clim ? clim.v : null, 'raw'],
      ['τ (Гудмэн–Крускал)', m.tau, inp ? inp.tau : null, rnd ? rnd.tau : null, clim ? clim.tau : null, 'raw'],
      ['A (сходство)', m.A, inp ? inp.A : null, rnd ? rnd.A : null, clim ? clim.A : null, 'raw'],
    ];
    rows.forEach(function(row) {
      const name = row[0], v1 = row[1], v2 = row[2], v3 = row[3],
            v4 = row[4], fmtType = row[5];
      const f = fmtType === 'pct' ? pct : fmt;
      const diff = (v1 !== null && v1 !== undefined &&
                    v2 !== null && v2 !== undefined) ? (v1 - v2) : null;
      const diffStr = diff !== null
        ? (diff > 0 ? '+' : '') + diff.toFixed(3)
        : '—';
      const isBetter = diff !== null && diff > 0;
      html += '<tr>'
            + '<td>' + name + '</td>'
            + '<td>' + f(v1) + '</td>'
            + '<td>' + f(v2) + '</td>'
            + '<td>' + f(v3) + '</td>'
            + '<td>' + f(v4) + '</td>'
            + '<td style="color:' + (isBetter ? '#00e5a0' : 'inherit') + '">'
            + diffStr + '</td>'
            + '</tr>';
    });
    if (data.S_haidke !== null && data.S_haidke !== undefined) {
      html += '<tr><td>S Хайдке (метод vs инерц.)</td>'
            + '<td colspan="5" style="color:#00e5a0;font-weight:700">'
            + data.S_haidke.toFixed(3) + '</td></tr>';
    }
    html += '</table>';

    html += '<div class="formula">'
          + '<b>Методический</b> — прогноз выбранной модели за сутки до события.<br>'
          + '<b>Инерционный</b> — прогноз на час t = факт в час t−1.<br>'
          + '<b>Случайный</b> — математическое ожидание независимого прогноза.<br>'
          + '<b>Климатологический</b> — 5-летняя норма для этого дня года.<br>'
          + '<b>S Хайдке</b> — если > 0, методический прогноз лучше инерционного.'
          + '</div>';
    html += '</div>';

    document.getElementById('result').innerHTML = html;
    document.getElementById('png-btn').style.display = 'inline-block';
  }

  function downloadPNG() {
    const result = document.getElementById('result');
    const btn = document.getElementById('png-btn');
    const orig = btn.textContent;
    btn.textContent = '⏳ Готовим...';
    btn.disabled = true;

    html2canvas(result, {
      backgroundColor: '#0a0e1a',
      scale: 2,
      logging: false,
    }).then(function(canvas) {
      const link = document.createElement('a');
      const phenomenon = document.getElementById('phenomenon-select').value;
      const start = document.getElementById('start-date').value;
      const end = document.getElementById('end-date').value;
      link.download = 'matrix_' + (STATION || 'point') + '_' + phenomenon + '_' +
                      start + '_' + end + '.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
      btn.textContent = orig;
      btn.disabled = false;
    }).catch(function(err) {
      alert('Ошибка экспорта: ' + err.message);
      btn.textContent = orig;
      btn.disabled = false;
    });
  }

  setTimeout(loadMatrix, 200);
</script>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ============================================================
# СРАВНЕНИЕ МОДЕЛЕЙ ПО МАТРИЦАМ
# ============================================================
COMPARE_MATRICES_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Сравнение моделей — {{ station_name }}</title>
""" + BASE_STYLE + """
<style>
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 20px; margin-bottom: 16px; overflow-x: auto; }
  .card h2 { font-size: 16px; margin: 0 0 14px 0;
             color: var(--accent); font-weight: 600; }
  .controls { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 14px 18px; margin-bottom: 16px;
    display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
  .controls label { color: var(--text-1); font-size: 13px; font-weight: 500; }
  .controls select, .controls input[type=date] {
    padding: 10px 14px;
    background: rgba(10, 14, 26, 0.6);
    border: 1px solid var(--border); border-radius: 10px;
    color: var(--text-0); font-size: 14px; outline: none;
    font-family: 'Inter', sans-serif;
  }
  [data-theme="light"] .controls select,
  [data-theme="light"] .controls input[type=date] { background: #fff; }
  .controls button {
    padding: 10px 22px; border: none; border-radius: 10px;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff; cursor: pointer; font-size: 14px; font-weight: 600;
  }
  .matrix { display: grid; grid-template-columns: 90px 1fr 1fr 70px;
            gap: 1px; background: var(--border);
            border: 1px solid var(--border); border-radius: 12px;
            overflow: hidden; margin-bottom: 14px; max-width: 540px; }
  .matrix div { background: var(--bg-1); padding: 12px 10px;
                text-align: center; font-family: 'JetBrains Mono', monospace;
                font-size: 14px; }
  .matrix .hdr { background: rgba(120,160,255,0.08);
                 color: var(--text-1); font-weight: 700;
                 font-size: 11px; font-family: 'Inter', sans-serif;
                 text-transform: uppercase; letter-spacing: 0.5px; }
  .matrix .hit  { background: rgba(0,229,160,0.15); color: #00e5a0;
                  font-weight: 700; }
  .matrix .miss { background: rgba(255,181,71,0.15); color: #ffb547;
                  font-weight: 700; }
  .matrix .false { background: rgba(255,84,112,0.15); color: #ff5470;
                   font-weight: 700; }
  .metrics-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
    gap: 10px; margin-top: 12px;
  }
  .metric { padding: 10px 12px; border-radius: 10px;
    background: rgba(120,160,255,0.06);
    border: 1px solid var(--border); }
  .metric .label { font-size: 11px; color: var(--text-2);
                   text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
  .metric .value { font-size: 18px; font-weight: 700;
                   color: var(--text-0); margin-top: 6px;
                   font-family: 'JetBrains Mono', monospace; }
  table.cmp { width: 100%; border-collapse: collapse; font-size: 13px; }
  table.cmp th, table.cmp td { padding: 10px 12px; text-align: center;
    border-bottom: 1px solid var(--border); }
  table.cmp th { background: rgba(120,160,255,0.06);
    color: var(--text-1); font-weight: 600; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.5px; }
  table.cmp td:first-child { text-align: left; font-weight: 600;
    color: var(--accent); font-family: 'Inter', sans-serif; }
  table.cmp td { font-family: 'JetBrains Mono', monospace; }
  table.cmp td.best { color: #00e5a0; font-weight: 700; }
  .loading { color: var(--accent); text-align: center; padding: 20px;
             font-family: 'JetBrains Mono', monospace; font-size: 13px; }
  .err { color: #ff5470; padding: 20px; text-align: center; }
</style>
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>Сравнение моделей по матрицам</h1>
<div class="sub">{{ station_name }} · критерии успешности по Хандожко</div>

<div class="controls">
  <label>Явление:</label>
  <select id="phenomenon-select">
    {% for k, p in phenomena.items() %}
      <option value="{{ k }}" {% if k == phenomenon %}selected{% endif %}>
        {{ p.name }} ({{ p.unit }})
      </option>
    {% endfor %}
  </select>
  <label>С:</label>
  <input type="date" id="start-date" value="{{ start_date }}">
  <label>По:</label>
  <input type="date" id="end-date" value="{{ end_date }}">
  <button onclick="loadComparison()">📊 Сравнить</button>
</div>

<div id="result">
  <div class="loading">Выберите параметры и нажмите «Сравнить»…</div>
</div>

<script>
  const STATION = "{{ station_key }}";
  const LAT = {{ lat }};
  const LON = {{ lon }};

  async function loadComparison() {
    const phenomenon = document.getElementById('phenomenon-select').value;
    const start = document.getElementById('start-date').value;
    const end = document.getElementById('end-date').value;
    const result = document.getElementById('result');

    if (!start || !end) {
      result.innerHTML = '<div class="err">Укажите даты</div>';
      return;
    }
    if (start > end) {
      result.innerHTML = '<div class="err">Дата начала позже даты конца</div>';
      return;
    }

    result.innerHTML = '<div class="loading">⏳ Считаем матрицы для всех моделей…</div>';

    try {
      const url = '/api/compare-matrices?lat=' + LAT + '&lon=' + LON +
                  '&phenomenon=' + phenomenon +
                  '&start=' + start + '&end=' + end;
      const resp = await fetch(url);
      const data = await resp.json();
      if (data.error) {
        result.innerHTML = '<div class="err">' + data.error + '</div>';
        return;
      }
      render(data);
    } catch (e) {
      result.innerHTML = '<div class="err">Ошибка: ' + e.message + '</div>';
    }
  }

  function fmt(v) {
    if (v === null || v === undefined) return '—';
    return v.toFixed(3);
  }

  function pct(v) {
    if (v === null || v === undefined) return '—';
    return (v * 100).toFixed(1) + '%';
  }

  function matrixBlock(title, color, mm) {
    const mc = mm.contingency;
    return '<div class="card fade-in">'
      + '<h2 style="color:' + color + '">' + title + '</h2>'
      + '<div class="matrix">'
      + '<div class="hdr"></div>'
      + '<div class="hdr">П</div>'
      + '<div class="hdr">П̄</div>'
      + '<div class="hdr">Σ</div>'
      + '<div class="hdr">Ф</div>'
      + '<div class="hit">' + mc.n11 + '</div>'
      + '<div class="miss">' + mc.n12 + '</div>'
      + '<div>' + mc.n10 + '</div>'
      + '<div class="hdr">Ф̄</div>'
      + '<div class="false">' + mc.n21 + '</div>'
      + '<div class="hit">' + mc.n22 + '</div>'
      + '<div>' + mc.n20 + '</div>'
      + '<div class="hdr">Σ</div>'
      + '<div>' + mc.n01 + '</div>'
      + '<div>' + mc.n02 + '</div>'
      + '<div>' + mc.N + '</div>'
      + '</div>'
      + '<div class="metrics-grid">'
      + '<div class="metric"><div class="label">p</div>'
      + '<div class="value">' + pct(mm.p) + '</div></div>'
      + '<div class="metric"><div class="label">H</div>'
      + '<div class="value">' + fmt(mm.H) + '</div></div>'
      + '<div class="metric"><div class="label">Q</div>'
      + '<div class="value">' + fmt(mm.Q) + '</div></div>'
      + '<div class="metric"><div class="label">v</div>'
      + '<div class="value">' + fmt(mm.v) + '</div></div>'
      + '<div class="metric"><div class="label">τ</div>'
      + '<div class="value">' + fmt(mm.tau) + '</div></div>'
      + '<div class="metric"><div class="label">A</div>'
      + '<div class="value">' + fmt(mm.A) + '</div></div>'
      + '</div>'
      + '</div>';
  }

  function render(data) {
    let html = '';

    html += '<div class="card fade-in">';
    html += '<h2>📋 Параметры</h2>';
    html += '<div style="color:var(--text-1);font-size:13px;line-height:1.9;">'
          + 'Явление: <b>' + data.phenomenon_name + '</b><br>'
          + 'Период: <b>' + data.start + ' … ' + data.end + '</b> '
          + '(' + data.dates_used + ' дней, ' + data.hours_total + ' часов)'
          + '</div>';
    html += '</div>';

    html += '<div class="card fade-in">';
    html += '<h2>📊 Сводка критериев по моделям</h2>';
    html += '<table class="cmp"><tr>'
          + '<th>Модель</th>'
          + '<th>p</th><th>H</th><th>Q</th><th>v</th><th>τ</th><th>A</th>'
          + '<th>S Хайдке</th>'
          + '</tr>';

    const modelsData = data.models;
    const keys = Object.keys(modelsData);
    const bestByKey = {};
    ['p', 'H', 'Q', 'v', 'tau', 'A'].forEach(function(k) {
      let best = null;
      keys.forEach(function(mk) {
        const v = modelsData[mk][k];
        if (v !== null && v !== undefined && (best === null || v > best)) {
          best = v;
        }
      });
      bestByKey[k] = best;
    });

    keys.forEach(function(mk) {
      const mm = modelsData[mk];
      const row = [
        ['p', mm.p, pct],
        ['H', mm.H, fmt],
        ['Q', mm.Q, fmt],
        ['v', mm.v, fmt],
        ['tau', mm.tau, fmt],
        ['A', mm.A, fmt],
      ];
      html += '<tr><td>' + mm.name + '</td>';
      row.forEach(function(cell) {
        const key = cell[0], val = cell[1], f = cell[2];
        const isBest = val !== null && val !== undefined &&
                       bestByKey[key] !== null &&
                       Math.abs(val - bestByKey[key]) < 1e-9;
        html += '<td class="' + (isBest ? 'best' : '') + '">' + f(val) + '</td>';
      });
      html += '<td>' + (mm.S_haidke !== null && mm.S_haidke !== undefined
                        ? mm.S_haidke.toFixed(3) : '—') + '</td>';
      html += '</tr>';
    });

    html += '</table>';
    html += '</div>';

    const colors = { gfs: '#4dabff', ecmwf: '#00e5a0', icon: '#ffb547' };
    keys.forEach(function(mk) {
      const mm = modelsData[mk];
      const color = colors[mk] || '#4dabff';
      html += matrixBlock('📘 ' + mm.name, color, mm);
    });

    document.getElementById('result').innerHTML = html;
  }

  setTimeout(loadComparison, 200);
</script>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ============================================================
# УЧЕБНЫЕ ПРИМЕРЫ
# ============================================================
TEACHING_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Учебные примеры — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 22px 26px; margin-bottom: 16px; }
  .card h2 { font-size: 17px; margin: 0 0 14px 0;
             color: var(--accent); font-weight: 600; }
  .card h3 { font-size: 14px; margin: 18px 0 8px 0;
             color: var(--text-0); font-weight: 600; }
  .card p, .card li { color: var(--text-1); font-size: 14px;
                      line-height: 1.75; margin: 6px 0; }
  .card b { color: var(--text-0); }
  .card code { font-family: 'JetBrains Mono', monospace;
    background: rgba(120,160,255,0.08);
    padding: 2px 6px; border-radius: 5px; font-size: 12.5px;
    color: var(--accent); }
  .card ul { padding-left: 20px; margin: 6px 0; }
  .example-btn {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 12px 20px; border-radius: 12px; margin: 6px 6px 6px 0;
    background: linear-gradient(135deg, rgba(77,171,255,0.10), rgba(124,92,255,0.10));
    border: 1px solid rgba(77,171,255,0.25); color: var(--text-0);
    text-decoration: none; font-size: 14px; font-weight: 500;
    font-family: 'Inter', sans-serif; transition: all 0.2s;
  }
  .example-btn:hover {
    background: linear-gradient(135deg, rgba(77,171,255,0.20), rgba(124,92,255,0.20));
    border-color: var(--border-hover); transform: translateY(-2px);
  }
  .formula-box {
    background: rgba(77,171,255,0.05);
    border-left: 3px solid var(--accent);
    border-radius: 8px; padding: 12px 16px; margin: 12px 0;
    font-family: 'JetBrains Mono', monospace; font-size: 13px;
    color: var(--text-1); line-height: 1.9;
  }
  .num {
    display: inline-block; width: 26px; height: 26px;
    border-radius: 50%; text-align: center; line-height: 26px;
    background: rgba(77,171,255,0.15); color: var(--accent);
    font-weight: 700; font-size: 13px; margin-right: 8px;
  }
</style>
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>Учебные примеры</h1>
<div class="sub">
  По учебнику: Дробжева Я.В., Волобуева О.В.
  «Метеорологические прогнозы и их экономическая полезность» (СПб, 2016)
</div>

<div class="card fade-in">
  <h2>📚 О чём этот раздел</h2>
  <p>Здесь собраны разборы примеров из глав 3–5 учебника. Для каждого примера
  можно открыть интерактивную страницу <code>/alt-verify</code> с предустановленными
  параметрами и посмотреть, как работает метод Л.А. Хандожко на реальных данных.</p>
</div>

<div class="card fade-in">
  <h2>🌡 Пример 1. Заморозки в сельском хозяйстве</h2>
  <p><b>Глава 3.</b> Сельхозпредприятие «Дмитриевский», Республика Башкортостан,
  метеостанция Уфа-Дема, 1999–2003 гг., сельхозкультура — капуста.</p>

  <h3>Ключевые элементы матрицы потерь</h3>
  <div class="formula-box">
    s₁₁ = C — затраты на защиту (дымление, дождевание)<br>
    s₁₂ = L — прямые потери при пропуске заморозка<br>
    s₂₁ = C — напрасные затраты (прогноз был, явления не было)<br>
    s₂₂ = 0 — потерь нет
  </div>

  <h3>Формулы прямых потерь</h3>
  <div class="formula-box">
    s₁₂ = 2·H·k̄·S̄ + S<sub>y</sub><br>
    где H — затраты на рассаду и посадку,<br>
    k̄ — средняя степень повреждения,<br>
    S<sub>y</sub> — недобор урожая (~5%)
  </div>

  <h3>Результат из учебника (капуста, 1999–2003)</h3>
  <p>Экономический эффект от методических прогнозов заморозков:
  <b>от 90 до 443 тыс. руб. за сезон</b>. Оптимальная стратегия — ориентация
  на оперативные прогнозы.</p>

  <p style="margin-top:16px">Посмотреть на реальных данных (интерактив):</p>
  <a class="example-btn" href="/alt-verify/tushino">
    🔍 Заморозок · Тушино
  </a>
  <a class="example-btn" href="/alt-verify?lat=54.7388&lon=55.9721&name=Уфа">
    🔍 Заморозок · Уфа
  </a>
</div>

<div class="card fade-in">
  <h2>💨 Пример 2. Скорость ветра для морского порта</h2>
  <p><b>Глава 4.</b> Мурманский морской порт, октябрь–март 2004–2008 гг.</p>

  <h3>Матрица потерь</h3>
  <div class="formula-box">
    s₁₁ = 1,7 млн руб. — затраты на защиту (простой судов, кранов)<br>
    s₁₂ = 4,6 млн руб. — прямые потери (повреждения судов, оборудования)<br>
    εs₁₂ ≈ 1,2 млн руб. — непредотвращённые потери<br>
    s₂₁ = 0,85 млн руб. — напрасные затраты
  </div>

  <h3>Результат из учебника</h3>
  <p>Экономический эффект за период 2004–2008 (октябрь–март):
  <b>168 млн руб.</b> На 1 рубль затрат — 153–280 руб. сбережённых средств.</p>

  <p style="margin-top:16px">Посмотреть на реальных данных:</p>
  <a class="example-btn" href="/alt-verify?lat=68.9585&lon=33.0827&name=Мурманск">
    🔍 Сильный ветер · Мурманск
  </a>
</div>

<div class="card fade-in">
  <h2>🔥 Пример 3. Пожароопасность в лесном хозяйстве</h2>
  <p><b>Глава 5.</b> Республика Адыгея, май–август 2001–2005 гг.</p>

  <h3>Матрица потерь</h3>
  <div class="formula-box">
    s₁₁ = 68,3 тыс. руб. — экстренная организация тушения<br>
    s₁₂ = 1766,2 тыс. руб. — прямые потери при пожаре (t = 12 ч)<br>
    ε = 0,16 — коэффициент непредотвращённых потерь<br>
    s₂₁ = 28,1 тыс. руб. — напрасные затраты
  </div>

  <h3>Формула площади пожара</h3>
  <div class="formula-box">
    S₃ = 1,0 · t<sup>1,25</sup> — для 3-го класса пожарной опасности<br>
    при t = 12 ч → S₃ ≈ 22,3 га
  </div>

  <h3>Результат из учебника</h3>
  <p>Экономический эффект за 5 лет: <b>26 млн руб.</b>
  На 1 рубль затрат — 47 руб. сбережённых природных богатств.</p>

  <p style="margin-top:16px">Посмотреть на реальных данных:</p>
  <a class="example-btn" href="/alt-verify?lat=44.6098&lon=40.1006&name=Майкоп">
    🔍 Сильная жара · Майкоп
  </a>
</div>

<div class="card fade-in">
  <h2>📊 Как читать результаты</h2>
  <ul>
    <li><span class="num">1</span> <b>p</b> — общая оправдываемость: доля всех
      правильных ответов (и «да», и «нет»)</li>
    <li><span class="num">2</span> <b>H</b> — надёжность: доля обнаруженных явлений
      от всех фактических</li>
    <li><span class="num">3</span> <b>Q</b> — точность (Обухова): доля оправдавшихся
      прогнозов наличия</li>
    <li><span class="num">4</span> <b>v</b> — информационное отношение: какая часть
      климатологической неопределённости устраняется</li>
    <li><span class="num">5</span> <b>τ</b> — мера Гудмэна–Крускала: наиболее полная
      мера различия качества</li>
    <li><span class="num">6</span> <b>S</b> — критерий Хайдке: если &gt; 0,
      методический прогноз лучше инерционного</li>
  </ul>
</div>

<div class="card fade-in">
  <h2>🎓 Для преподавателей</h2>
  <p>Все примеры можно использовать на практических занятиях по курсам
  «Экономическая метеорология» и «Метеорологическое обеспечение хозяйственной
  деятельности». Студент может:</p>
  <ul>
    <li>Открыть интерактивную страницу <code>/alt-verify</code> с любой точкой</li>
    <li>Выбрать явление, модель и период</li>
    <li>Получить сразу 4 матрицы (методическую, инерционную, случайную,
      климатологическую) и критерии успешности</li>
    <li>Скачать результат в PNG для отчёта</li>
  </ul>
</div>

<p style="text-align:center;color:var(--text-2);font-size:12px;margin-top:24px;">
  Проект носит образовательный характер.
</p>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ============================================================
# ГРАФИК СРАВНЕНИЯ
# ============================================================
CHART_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Сравнение моделей — {{ station_name }}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
""" + BASE_STYLE + """
<style>
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 20px; margin-bottom: 16px; }
  .card h2 { font-size: 16px; margin: 0 0 14px 0;
             color: var(--accent); font-weight: 600; }
  canvas { max-height: 420px; }
  .chart-tabs { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
  .chart-tabs button { padding: 9px 16px; border-radius: 10px;
    background: rgba(120, 160, 255, 0.08); color: var(--text-1);
    border: 1px solid var(--border); cursor: pointer;
    font-size: 13px; font-weight: 500; font-family: 'Inter', sans-serif; }
  .chart-tabs button.active { background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff; border-color: transparent; }
  .chart-comment { margin-top: 14px; font-size: 12px; color: var(--text-1);
    line-height: 1.6; padding: 12px 16px;
    background: rgba(77,171,255,0.04);
    border-left: 3px solid var(--accent); border-radius: 6px; }
  .model-legend { display: flex; gap: 16px; flex-wrap: wrap;
                  margin-bottom: 12px; font-size: 12px; }
  .model-legend span { display: inline-flex; align-items: center; gap: 6px;
                       color: var(--text-1); }
  .model-legend i { width: 12px; height: 3px; border-radius: 2px;
                    display: inline-block; }
</style>
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>Сравнение моделей</h1>
<div class="sub">
  {{ station_name }} · {{ lat }}, {{ lon }} · прогноз на {{ days }} дня
</div>

<div class="chart-tabs">
  <button class="active" onclick="showMetric('temp', this)">🌡 Температура</button>
  <button onclick="showMetric('theta', this)">🌀 θ</button>
  <button onclick="showMetric('wind', this)">💨 Ветер</button>
  <button onclick="showMetric('precip', this)">💧 Осадки</button>
  <button onclick="showMetric('pressure', this)">📊 Давление</button>
</div>

<div class="card fade-in">
  <h2 id="chart-title">Температура, °C</h2>
  <div class="model-legend" id="model-legend"></div>
  <canvas id="chart"></canvas>
  <div class="chart-comment" id="chart-comment"></div>
</div>

<script>
  const LABELS = {{ labels_json | safe }};
  const SERIES = {{ series_json | safe }};
  const COLORS = { gfs: "#4dabff", ecmwf: "#00e5a0", icon: "#ffb547" };
  const METRICS = {
    temp:     { title: "Температура, °C",
                comment: "💡 Сравнение хода температуры по трём моделям." },
    theta:    { title: "Потенциальная температура, K",
                comment: "💡 Резкие скачки θ — признак фронта." },
    wind:     { title: "Ветер, м/с",
                comment: "💡 Усиление ветра обычно совпадает с фронтом." },
    precip:   { title: "Осадки, мм",
                comment: "💡 Модели по-разному «видят» локальные ливни." },
    pressure: { title: "Давление, гПа",
                comment: "💡 Глубокий минимум = циклон." },
  };

  Chart.defaults.color = "#a8b4d0";
  Chart.defaults.borderColor = "rgba(120,160,255,0.1)";
  Chart.defaults.font.family = "'Inter', sans-serif";

  let chart = null;

  function renderChart(metricKey) {
    const m = METRICS[metricKey];
    document.getElementById("chart-title").textContent = m.title;
    document.getElementById("chart-comment").textContent = m.comment;

    const datasets = Object.keys(SERIES).map(function(modelKey) {
      const s = SERIES[modelKey];
      return { label: s.name, data: s[metricKey],
        borderColor: COLORS[modelKey] || "#4dabff",
        backgroundColor: "transparent",
        borderWidth: 2.5, tension: 0.4,
        pointRadius: 0, pointHoverRadius: 5, spanGaps: true };
    });

    let legend = "";
    Object.keys(SERIES).forEach(function(modelKey) {
      legend += '<span><i style="background:' + (COLORS[modelKey] || "#4dabff") + '"></i>' +
                SERIES[modelKey].name + '</span>';
    });
    document.getElementById("model-legend").innerHTML = legend;

    if (chart) chart.destroy();
    const ctx = document.getElementById("chart").getContext("2d");
    chart = new Chart(ctx, {
      type: "line",
      data: { labels: LABELS, datasets: datasets },
      options: {
        responsive: true,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: { mode: "index", intersect: false,
                     backgroundColor: "rgba(15,21,36,0.95)",
                     borderColor: "rgba(120,160,255,0.3)",
                     borderWidth: 1, padding: 12 },
        },
        scales: {
          x: { grid: { color: "rgba(120,160,255,0.06)" },
               ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 12 } },
          y: { grid: { color: "rgba(120,160,255,0.06)" }, beginAtZero: false },
        },
      },
    });
  }

  function showMetric(key, btn) {
    document.querySelectorAll(".chart-tabs button").forEach(b => b.classList.remove("active"));
    if (btn) btn.classList.add("active");
    renderChart(key);
  }

  renderChart("temp");
</script>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ============================================================
# СРАВНЕНИЕ ЯВЛЕНИЙ
# ============================================================
COMPARE_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Сравнение моделей — {{ station_name }}</title>
""" + BASE_STYLE + """
<style>
  table { width: 100%; border-collapse: collapse; font-size: 14px;
          background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
          backdrop-filter: blur(14px);
          border-radius: 16px; overflow: hidden; border: 1px solid var(--border); }
  th, td { padding: 14px; text-align: center; border-bottom: 1px solid var(--border); }
  th { background: rgba(120, 160, 255, 0.08); color: var(--text-1);
       font-weight: 600; font-size: 12px;
       text-transform: uppercase; letter-spacing: 0.5px; }
  td { font-family: 'JetBrains Mono', monospace; }
  td:first-child { font-family: 'Inter', sans-serif;
                   font-weight: 600; color: var(--accent); text-align: left; }
  tr.fog td { background: rgba(255, 181, 71, 0.10); }
  tr.thunder td { background: rgba(124, 92, 255, 0.14); }
  tr.rain td { background: rgba(77, 171, 255, 0.10); }
</style>
</head>
<body>
<a class="back" href="/model/{{ first_model }}">← Назад</a>
<h1>Сравнение моделей</h1>
<div class="sub">Прогноз для «{{ station_name }}» · на {{ days }} дня</div>

<table class="fade-in">
  <tr>
    <th>Модель</th><th>🌫 Туман, ч</th><th>⛈ Гроза, ч</th><th>💧 Осадки, ч</th>
  </tr>
  {% for r in rows %}
  <tr class="{% if r.fog > 0 %}fog{% elif r.thunder > 0 %}thunder{% elif r.precip > 0 %}rain{% endif %}">
    <td>{{ r.name }}</td><td>{{ r.fog }}</td>
    <td>{{ r.thunder }}</td><td>{{ r.precip }}</td>
  </tr>
  {% endfor %}
</table>
<p style="text-align:center;color:var(--text-2);font-size:11px;margin-top:16px;font-family:'JetBrains Mono',monospace;">
  Обновлено: {{ updated }}
</p>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ============================================================
# КАРТА
# ============================================================
MAP_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Карта</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
""" + BASE_STYLE + """
<style>
  #map { height: 75vh; min-height: 480px; border-radius: 16px;
         border: 1px solid var(--border);
         box-shadow: 0 20px 60px -20px rgba(0,0,0,0.6); overflow: hidden; }
  .search-box { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 12px 14px; margin-bottom: 12px; display: flex; gap: 10px; }
  .search-box input { flex: 1; padding: 12px 16px;
    background: rgba(10, 14, 26, 0.5);
    border: 1px solid var(--border); border-radius: 10px;
    font-size: 14px; outline: none; color: var(--text-0);
    font-family: 'Inter', sans-serif; }
  [data-theme="light"] .search-box input { background: #fff; }
  .search-box button { padding: 12px 22px; border: none; border-radius: 10px;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff; cursor: pointer; font-size: 14px; font-weight: 600; }
  .layer-controls { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 10px 14px; margin-bottom: 12px;
    display: flex; flex-wrap: wrap; gap: 14px; align-items: center; }
  .layer-controls label { color: var(--text-1); font-size: 13px;
    display: flex; align-items: center; gap: 6px; cursor: pointer; }
  .hint { color: var(--text-2); font-size: 12px; margin-bottom: 10px;
          padding: 8px 12px; background: rgba(77,171,255,0.05);
          border-left: 3px solid var(--accent); border-radius: 6px; }
  .leaflet-popup-content-wrapper {
    background: #fff !important; color: #222 !important; border-radius: 12px !important; }
  .leaflet-popup-tip { background: #fff !important; }
</style>
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>Карта</h1>
<div class="sub">OSM + спутник Meteosat + радар RainViewer</div>

<div class="layer-controls">
  <label><input type="checkbox" id="sat-toggle" onchange="toggleSatellite()"> 🛰 Спутник Meteosat</label>
  <label><input type="checkbox" id="radar-toggle" onchange="toggleRadar()"> 🌧 Радар осадков</label>
</div>

<div class="hint">💡 Клик по карте — прогноз для точки.</div>

<div class="search-box">
  <input type="text" id="search-input"
         placeholder="Город, координаты или почтовый индекс..."
         onkeydown="if(event.key==='Enter') doSearch()">
  <button onclick="doSearch()">🔍 Найти</button>
</div>

<div id="map"></div>

<script>
  const map = L.map('map').setView([55.75, 37.62], 7);
  L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors, HOT', maxZoom: 19,
  }).addTo(map);

  let satelliteLayer = null;
  function toggleSatellite() {
    const on = document.getElementById('sat-toggle').checked;
    if (on && !satelliteLayer) {
      satelliteLayer = L.tileLayer.wms("https://view.eumetsat.int/geoserver/wms", {
        layers: 'mtg_fd:rgb_geocolour', format: 'image/png',
        transparent: true, opacity: 0.6,
        attribution: '© EUMETSAT', version: '1.3.0',
      }).addTo(map);
    } else if (!on && satelliteLayer) {
      map.removeLayer(satelliteLayer); satelliteLayer = null;
    }
  }

  let radarLayer = null;
  async function toggleRadar() {
    const on = document.getElementById('radar-toggle').checked;
    if (on && !radarLayer) {
      try {
        const resp = await fetch('https://api.rainviewer.com/public/weather-maps.json');
        const data = await resp.json();
        const past = data.radar && data.radar.past ? data.radar.past : [];
        if (!past.length) return;
        const latest = past[past.length - 1];
        const url = data.host + latest.path + '/256/{z}/{x}/{y}/2/1_1.png';
        radarLayer = L.tileLayer(url, { opacity: 0.65,
          attribution: '© RainViewer', maxZoom: 12 }).addTo(map);
      } catch (e) {
        alert('Не удалось загрузить радар.');
        document.getElementById('radar-toggle').checked = false;
      }
    } else if (!on && radarLayer) {
      map.removeLayer(radarLayer); radarLayer = null;
    }
  }

  map.on('click', async function(e) {
    const lat = e.latlng.lat.toFixed(4);
    const lon = e.latlng.lng.toFixed(4);
    const popup = L.popup().setLatLng(e.latlng).setContent('Загрузка...').openOn(map);
    try {
      const url = 'https://api.open-meteo.com/v1/forecast?latitude=' + lat + '&longitude=' + lon +
        '&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,pressure_msl,precipitation,weather_code&timezone=Europe/Moscow';
      const resp = await fetch(url);
      const data = await resp.json();
      if (data.current) {
        const c = data.current;
        const desc = {{ code_to_text_json | safe }};
        popup.setContent(
          '<div style="font-family:Inter,sans-serif;font-size:13px;min-width:240px;color:#222;">' +
            '<b style="color:#0369a1">' + lat + ', ' + lon + '</b>' +
            '<hr style="border:none;border-top:1px solid #ddd;margin:8px 0;">' +
            '🌡 <b style="font-size:16px">' + c.temperature_2m.toFixed(1) + '°C</b><br>' +
            '💨 ' + c.wind_speed_10m.toFixed(1) + ' м/с<br>' +
            '💧 ' + c.precipitation.toFixed(1) + ' мм<br>' +
            '📊 ' + Math.round(c.pressure_msl) + ' гПа<br>' +
            '<i style="color:#666">' + (desc[c.weather_code] || '—') + '</i><br>' +
            '<a href="/forecast/point?lat=' + lat + '&lon=' + lon +
              '&name=' + encodeURIComponent(lat + ', ' + lon) + '&model=gfs&view=table" ' +
              'style="color:#0369a1;font-weight:600;">📋 Прогноз →</a>' +
          '</div>'
        );
      }
    } catch (err) { popup.setContent('Ошибка.'); }
  });

  async function doSearch() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) return;
    const btn = document.querySelector('.search-box button');
    const orig = btn.textContent;
    btn.textContent = '⏳'; btn.disabled = true;
    try {
      const coordMatch = query.match(/^(-?\\d+\\.?\\d*)[\\s,]+(-?\\d+\\.?\\d*)$/);
      if (coordMatch) {
        const lat = parseFloat(coordMatch[1]);
        const lon = parseFloat(coordMatch[2]);
        if (lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
          map.flyTo([lat, lon], 10); return;
        }
      }
      const url = 'https://geocoding-api.open-meteo.com/v1/search?name=' +
                  encodeURIComponent(query) + '&count=1&language=ru&format=json';
      const resp = await fetch(url);
      const data = await resp.json();
      if (data.results && data.results.length > 0) {
        map.flyTo([data.results[0].latitude, data.results[0].longitude], 10);
      } else { alert('Ничего не найдено: ' + query); }
    } catch (err) { alert('Ошибка поиска.'); }
    finally { btn.textContent = orig; btn.disabled = false; }
  }

  const STATIONS = {{ stations_json | safe }};
  Object.keys(STATIONS).forEach(function(key) {
    const s = STATIONS[key];
    L.circleMarker([s.lat, s.lon], {
      radius: 6, color: '#0369a1', fillColor: '#7c5cff',
      fillOpacity: 0.9, weight: 2,
    }).addTo(map).bindPopup('<b>' + s.name + '</b><br>' + s.lat + ', ' + s.lon);
  });
</script>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""


# ============================================================
# NOAA — исторические данные
# ============================================================
NOAA_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NOAA — исторические данные</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
""" + BASE_STYLE + """
<style>
  .card { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 20px; margin-bottom: 16px; }
  .card h2 { font-size: 16px; margin: 0 0 14px 0;
             color: var(--accent); font-weight: 600; }
  .controls { background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 14px 18px; margin-bottom: 16px;
    display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
  .controls label { color: var(--text-1); font-size: 13px; font-weight: 500; }
  .controls input, .controls select {
    padding: 10px 14px;
    background: rgba(10, 14, 26, 0.6);
    border: 1px solid var(--border); border-radius: 10px;
    color: var(--text-0); font-size: 14px; outline: none;
    font-family: 'Inter', sans-serif;
  }
  [data-theme="light"] .controls input,
  [data-theme="light"] .controls select { background: #fff; }
  .controls button {
    padding: 10px 22px; border: none; border-radius: 10px;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff; cursor: pointer; font-size: 14px; font-weight: 600;
  }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th, td { padding: 10px 12px; text-align: center;
           border-bottom: 1px solid var(--border); }
  th { background: rgba(120,160,255,0.06); color: var(--text-1);
       font-weight: 600; font-size: 11px; text-transform: uppercase; }
  td { font-family: 'JetBrains Mono', monospace; }
  td:first-child { font-family: 'Inter', sans-serif; font-weight: 600;
                   color: var(--accent); }
  .station-row { cursor: pointer; }
  .station-row:hover { background: rgba(120,160,255,0.06); }
  .station-row.selected { background: rgba(77,171,255,0.15); }
  canvas { max-height: 380px; }
  .loading { color: var(--accent); text-align: center; padding: 20px;
             font-family: 'JetBrains Mono', monospace; font-size: 13px; }
  .err { color: #ff5470; padding: 20px; text-align: center; }
  .hint { color: var(--text-2); font-size: 12px;
          padding: 10px 14px; background: rgba(77,171,255,0.05);
          border-left: 3px solid var(--accent); border-radius: 6px;
          margin-bottom: 14px; line-height: 1.7; }
</style>
</head>
<body>

<a class="back" href="/">← На главную</a>
<h1>NOAA — исторические данные</h1>
<div class="sub">Наблюдения со станций NOAA NCEI (для Москвы — до 2022-01-15)</div>

<div class="controls">
  <label>Широта:</label>
  <input type="number" id="lat" value="55.85" step="0.01" style="width:100px">
  <label>Долгота:</label>
  <input type="number" id="lon" value="37.44" step="0.01" style="width:100px">
  <label>Радиус, км:</label>
  <input type="number" id="radius" value="100" style="width:80px">
  <button onclick="findStations()">🔍 Найти станции</button>
</div>

<div id="stations-block" style="display:none">
  <div class="card">
    <h2>📡 Найденные станции</h2>
    <div id="stations-list"></div>
  </div>

  <div class="controls">
    <label>Период с:</label>
    <input type="date" id="start-date" value="2021-06-01">
    <label>по:</label>
    <input type="date" id="end-date" value="2021-06-30">
    <button onclick="loadData()">📊 Показать данные</button>
    <button onclick="downloadPNG()" id="png-btn" style="display:none;
            background: rgba(124,92,255,0.10); color: #a78bfa;
            border: 1px solid rgba(124,92,255,0.3);">
      📸 Скачать PNG
    </button>
  </div>
</div>

<div id="result">
  <div class="hint">
    💡 Укажите координаты и нажмите «Найти станции». Затем выберите станцию и период.<br>
    Для Москвы данные доступны до <b>2022-01-15</b>.
  </div>
</div>

<script>
  let selectedStation = null;

  async function findStations() {
    const lat = document.getElementById('lat').value;
    const lon = document.getElementById('lon').value;
    const radius = document.getElementById('radius').value;
    const list = document.getElementById('stations-list');
    list.innerHTML = '<div class="loading">⏳ Поиск…</div>';
    document.getElementById('stations-block').style.display = 'block';

    try {
      const url = '/api/noaa/nearby?lat=' + lat + '&lon=' + lon + '&radius=' + radius;
      const resp = await fetch(url);
      const data = await resp.json();
      if (!data.stations || !data.stations.length) {
        list.innerHTML = '<div class="err">Станции не найдены</div>';
        return;
      }
      let html = '<table><tr><th>Станция</th><th>ID</th><th>Расст., км</th>'
               + '<th>Данные с</th><th>Данные по</th></tr>';
      data.stations.forEach(s => {
        html += '<tr class="station-row" onclick="selectStation(this, \\'' + s.id + '\\')">'
              + '<td>' + (s.name || '—') + '</td>'
              + '<td style="font-size:11px">' + s.id + '</td>'
              + '<td>' + (s.distance_km ? s.distance_km.toFixed(1) : '—') + '</td>'
              + '<td>' + (s.mindate || '—') + '</td>'
              + '<td>' + (s.maxdate || '—') + '</td>'
              + '</tr>';
      });
      html += '</table>';
      list.innerHTML = html;
    } catch (e) {
      list.innerHTML = '<div class="err">Ошибка: ' + e.message + '</div>';
    }
  }

  function selectStation(row, stationId) {
    document.querySelectorAll('.station-row').forEach(r => r.classList.remove('selected'));
    row.classList.add('selected');
    selectedStation = stationId;
  }

  async function loadData() {
    if (!selectedStation) {
      alert('Сначала выберите станцию');
      return;
    }
    const start = document.getElementById('start-date').value;
    const end = document.getElementById('end-date').value;
    const result = document.getElementById('result');
    result.innerHTML = '<div class="loading">⏳ Загрузка данных…</div>';

    try {
      const lat = document.getElementById('lat').value;
      const lon = document.getElementById('lon').value;
      const url = '/api/noaa/historical?lat=' + lat + '&lon=' + lon
                + '&start=' + start + '&end=' + end;
      const resp = await fetch(url);
      const data = await resp.json();
      if (data.error) {
        result.innerHTML = '<div class="err">' + data.error + '</div>';
        return;
      }
      render(data);
    } catch (e) {
      result.innerHTML = '<div class="err">Ошибка: ' + e.message + '</div>';
    }
  }

  function render(data) {
    const station = data.station || {};
    const records = (data.data && data.data.results) ? data.data.results : [];

    const byDate = {};
    records.forEach(r => {
      const d = r.date.slice(0, 10);
      if (!byDate[d]) byDate[d] = {};
      byDate[d][r.datatype] = r.value;
    });
    const dates = Object.keys(byDate).sort();

    let html = '<div class="card"><h2>📊 ' + (station.name || 'Станция') + '</h2>';
    html += '<div style="color:var(--text-2);font-size:12px;margin-bottom:12px;">'
          + 'ID: ' + (station.id || '—')
          + ' · Расст.: ' + (station.distance_km ? station.distance_km.toFixed(1) + ' км' : '—')
          + ' · Период: ' + data.period.start + ' … ' + data.period.end
          + '</div>';

    if (!dates.length) {
      html += '<div class="err">Нет данных за этот период</div></div>';
      document.getElementById('result').innerHTML = html;
      return;
    }

    html += '<table><tr><th>Дата</th><th>TMAX, °C</th><th>TMIN, °C</th>'
          + '<th>Средняя, °C</th><th>Осадки, мм</th></tr>';
    dates.forEach(d => {
      const day = byDate[d];
      const tmax = day.TMAX !== undefined ? day.TMAX : null;
      const tmin = day.TMIN !== undefined ? day.TMIN : null;
      const tavg = (tmax !== null && tmin !== null) ? ((tmax + tmin) / 2).toFixed(1) : '—';
      const prcp = day.PRCP !== undefined ? day.PRCP : '—';
      html += '<tr>'
            + '<td>' + d + '</td>'
            + '<td>' + (tmax !== null ? tmax : '—') + '</td>'
            + '<td>' + (tmin !== null ? tmin : '—') + '</td>'
            + '<td>' + tavg + '</td>'
            + '<td>' + prcp + '</td>'
            + '</tr>';
    });
    html += '</table></div>';

    html += '<div class="card"><h2>📈 Динамика</h2>'
          + '<canvas id="noaa-chart"></canvas></div>';

    document.getElementById('result').innerHTML = html;
    document.getElementById('png-btn').style.display = 'inline-block';

    const tmaxArr = dates.map(d => byDate[d].TMAX !== undefined ? byDate[d].TMAX : null);
    const tminArr = dates.map(d => byDate[d].TMIN !== undefined ? byDate[d].TMIN : null);
    const prcpArr = dates.map(d => byDate[d].PRCP !== undefined ? byDate[d].PRCP : null);

    new Chart(document.getElementById('noaa-chart').getContext('2d'), {
      type: 'line',
      data: {
        labels: dates,
        datasets: [
          { label: 'TMAX', data: tmaxArr, borderColor: '#ff5470',
            backgroundColor: 'transparent', borderWidth: 2.5,
            tension: 0.3, pointRadius: 4, spanGaps: true },
          { label: 'TMIN', data: tminArr, borderColor: '#4dabff',
            backgroundColor: 'transparent', borderWidth: 2.5,
            tension: 0.3, pointRadius: 4, spanGaps: true },
          { label: 'Осадки, мм', data: prcpArr, borderColor: '#00e5a0',
            backgroundColor: 'rgba(0,229,160,0.15)', borderWidth: 2,
            type: 'bar', yAxisID: 'y1', spanGaps: true },
        ]
      },
      options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { labels: { color: '#a8b4d0' } } },
        scales: {
          x: { grid: { color: 'rgba(120,160,255,0.06)' } },
          y: { grid: { color: 'rgba(120,160,255,0.06)' },
               title: { display: true, text: '°C', color: '#a8b4d0' } },
          y1: { position: 'right', beginAtZero: true,
                grid: { drawOnChartArea: false },
                title: { display: true, text: 'мм', color: '#a8b4d0' } },
        },
      },
    });
  }

  function downloadPNG() {
    const result = document.getElementById('result');
    const btn = document.getElementById('png-btn');
    const orig = btn.textContent;
    btn.textContent = '⏳ Готовим...';
    btn.disabled = true;

    html2canvas(result, { backgroundColor: '#0a0e1a', scale: 2, logging: false })
      .then(canvas => {
        const link = document.createElement('a');
        link.download = 'noaa_data.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
        btn.textContent = orig;
        btn.disabled = false;
      })
      .catch(err => {
        alert('Ошибка экспорта: ' + err.message);
        btn.textContent = orig;
        btn.disabled = false;
      });
  }
</script>

""" + COMMON_JS + render_top_controls() + """
</body>
</html>
"""