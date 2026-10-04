# -*- coding: utf-8 -*-
"""Хабы: главная, прогноз, анализ, теория, О проекте."""

from ui.styles import (
    BASE_STYLE,
    COMMON_JS,
    render_header,
    render_legend,
)
FORECAST_HUB_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Прогноз — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 16px;
    margin-top: 24px;
  }
  .widget {
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 22px;
    backdrop-filter: blur(14px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    text-decoration: none;
    color: var(--text-0);
    display: flex;
    flex-direction: column;
    min-height: 160px;
  }
  .widget:hover {
    transform: translateY(-3px);
    border-color: var(--border-hover);
    box-shadow: var(--card-shadow);
  }
  .widget::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0; transition: opacity 0.3s;
  }
  .widget:hover::before { opacity: 1; }

  .widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: var(--text-2);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
    font-weight: 600;
  }
  .widget-title {
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 6px;
    color: var(--text-0);
  }
  .widget-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    line-height: 1.1;
    color: var(--accent);
    margin: 6px 0;
  }
  .widget-sub {
    font-size: 12px;
    color: var(--text-2);
    margin-top: auto;
    line-height: 1.5;
  }
  .widget-list {
    list-style: none;
    padding: 0;
    margin: 10px 0 0 0;
    font-size: 13px;
  }
  .widget-list li {
    padding: 6px 0;
    border-bottom: 1px solid rgba(120, 160, 255, 0.06);
    color: var(--text-1);
    display: flex;
    justify-content: space-between;
    gap: 12px;
  }
  .widget-list li:last-child { border-bottom: none; }
  .widget-list li span:last-child {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    color: var(--text-0);
    white-space: nowrap;
  }
  .widget-accent-blue   { --accent: #4dabff; }
  .widget-accent-green  { --accent: #00e5a0; }
  .widget-accent-orange { --accent: #ffb547; }
  .widget-accent-purple { --accent: #a78bfa; }
  .widget-accent-red    { --accent: #ff5470; }
</style>
</head>
<body>

""" + render_header("forecast") + """
<h1>🌍 Прогноз погоды</h1>
<div class="sub">Численные модели · поиск по точке · сравнение · синоптика</div>

<div class="dashboard-grid">

  <!-- GFS -->
  <a class="widget widget-accent-blue" href="/model/gfs">
    <div class="widget-header">
      <span>🌐 Модель GFS</span>
      <span>NOAA · США</span>
    </div>
    <div class="widget-title">Global Forecast System</div>
    <div class="widget-value">~13 км</div>
    <div class="widget-sub">
      Таблица · текст · график · авиация · синоптика
    </div>
  </a>

  <!-- ECMWF -->
  <a class="widget widget-accent-orange" href="/model/ecmwf">
    <div class="widget-header">
      <span>🌐 Модель ECMWF</span>
      <span>Европа</span>
    </div>
    <div class="widget-title">European Centre</div>
    <div class="widget-value">~9–25 км</div>
    <div class="widget-sub">
      Эталонная европейская модель · все виды прогноза
    </div>
  </a>

  <!-- ICON -->
  <a class="widget widget-accent-green" href="/model/icon">
    <div class="widget-header">
      <span>🌐 Модель ICON</span>
      <span>DWD · Германия</span>
    </div>
    <div class="widget-title">Icosahedral Nonhydrostatic</div>
    <div class="widget-value">~11 км</div>
    <div class="widget-sub">
      Немецкая модель · все виды прогноза
    </div>
  </a>

  <!-- Поиск точки -->
  <a class="widget widget-accent-purple" href="/search">
    <div class="widget-header">
      <span>🔍 Поиск точки</span>
      <span>Геокодинг</span>
    </div>
    <div class="widget-title">Прогноз для любой точки</div>
    <ul class="widget-list">
      <li><span>📊 Таблица</span><span>+</span></li>
      <li><span>📝 Текст</span><span>+</span></li>
      <li><span>📈 График</span><span>+</span></li>
      <li><span>✈️ Авиация</span><span>+</span></li>
    </ul>
  </a>

  <!-- График моделей -->
  <a class="widget widget-accent-blue" href="/chart/tushino">
    <div class="widget-header">
      <span>📈 Сравнить модели</span>
      <span>График</span>
    </div>
    <div class="widget-title">GFS vs ECMWF vs ICON</div>
    <div class="widget-value">T · P · V · 🌧</div>
    <div class="widget-sub">
      Температура · давление · ветер · осадки · факт ERA5
    </div>
  </a>

  <!-- Синоптика -->
  <a class="widget widget-accent-red" href="/synoptic/gfs/tushino">
    <div class="widget-header">
      <span>🌡 Синоптика по уровням</span>
      <span>925–300 гПа</span>
    </div>
    <div class="widget-title">Профиль атмосферы</div>
    <ul class="widget-list">
      <li><span>T · θ · RH</span><span>925–300</span></li>
      <li><span>Тропопауза</span><span>2 PVU</span></li>
      <li><span>Струя</span><span>300 гПа</span></li>
      <li><span>LI · K-Index</span><span>+</span></li>
    </ul>
  </a>

  <!-- Карта -->
  <a class="widget widget-accent-green" href="/maps">
    <div class="widget-header">
      <span>🗺 Карта + спутник + радар</span>
      <span>Leaflet</span>
    </div>
    <div class="widget-title">Интерактивная карта</div>
    <div class="widget-sub">
      OSM · спутник · RainViewer · поиск · клик по точке
    </div>
  </a>

</div>

""" + COMMON_JS + render_legend("forecast") + """
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
<style>
  .dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 16px;
    margin-top: 24px;
  }
  .widget {
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 22px;
    backdrop-filter: blur(14px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    text-decoration: none;
    color: var(--text-0);
    display: flex;
    flex-direction: column;
    min-height: 170px;
  }
  .widget:hover {
    transform: translateY(-3px);
    border-color: var(--border-hover);
    box-shadow: var(--card-shadow);
  }
  .widget::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0; transition: opacity 0.3s;
  }
  .widget:hover::before { opacity: 1; }

  .widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: var(--text-2);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
    font-weight: 600;
  }
  .widget-title {
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 8px;
    color: var(--text-0);
  }
  .widget-list {
    list-style: none;
    padding: 0;
    margin: 6px 0 0 0;
    font-size: 13px;
  }
  .widget-list li {
    padding: 6px 0;
    border-bottom: 1px solid rgba(120, 160, 255, 0.06);
    color: var(--text-1);
    display: flex;
    justify-content: space-between;
    gap: 12px;
  }
  .widget-list li:last-child { border-bottom: none; }
  .widget-list li span:last-child {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    color: var(--text-0);
    white-space: nowrap;
  }
  .widget-sub {
    font-size: 12px;
    color: var(--text-2);
    margin-top: auto;
    padding-top: 10px;
    line-height: 1.5;
  }
  .widget-accent-blue   { --accent: #4dabff; }
  .widget-accent-green  { --accent: #00e5a0; }
  .widget-accent-orange { --accent: #ffb547; }
  .widget-accent-purple { --accent: #a78bfa; }
  .widget-accent-red    { --accent: #ff5470; }
</style>
</head>
<body>
""" + render_header("analysis") + """
<h1>📊 Анализ и проверка</h1>
<div class="sub">Сравнение с фактом · статистика · история ошибок · матрицы</div>

<div class="dashboard-grid">

  <!-- Проверка моделей -->
  <a class="widget widget-accent-green" href="/verify/tushino">
    <div class="widget-header">
      <span>✅ Проверка моделей</span>
      <span>MAE · RMSE</span>
    </div>
    <div class="widget-title">Сравнение с фактом</div>
    <ul class="widget-list">
      <li><span>MAE · RMSE · Bias</span><span>°C</span></li>
      <li><span>Корреляция · R²</span><span>+</span></li>
      <li><span>P90 · MAPE</span><span>+</span></li>
    </ul>
  </a>

  <!-- История ошибок -->
  <a class="widget widget-accent-green" href="/verify/tushino/history">
    <div class="widget-header">
      <span>📉 История ошибок</span>
      <span>По дням</span>
    </div>
    <div class="widget-title">Динамика MAE / Bias</div>
    <div class="widget-sub">
      Графики по каждой модели за последние дни
    </div>
  </a>

  <!-- Статистический анализ -->
  <a class="widget widget-accent-purple" href="/analyze/tushino">
    <div class="widget-header">
      <span>📊 Статистический анализ</span>
      <span>Гистограммы</span>
    </div>
    <div class="widget-title">Расширенная статистика</div>
    <ul class="widget-list">
      <li><span>MAPE · P50 · P95</span><span>+</span></li>
      <li><span>Гистограмма ошибок</span><span>+</span></li>
      <li><span>F1 по осадкам</span><span>+</span></li>
    </ul>
  </a>

  <!-- Матрица Хандожко -->
  <a class="widget widget-accent-orange" href="/alt-verify/tushino">
    <div class="widget-header">
      <span>📋 Матрица прогнозов</span>
      <span>Хандожко</span>
    </div>
    <div class="widget-title">Критерии успешности</div>
    <ul class="widget-list">
      <li><span>p, H, τ, v</span><span>+</span></li>
      <li><span>Q, S, F1</span><span>+</span></li>
      <li><span>По каждому явлению</span><span>+</span></li>
    </ul>
  </a>

  <!-- Сравнение матриц -->
  <a class="widget widget-accent-orange" href="/compare-matrices/tushino">
    <div class="widget-header">
      <span>🔀 Сравнить модели</span>
      <span>Матрицы</span>
    </div>
    <div class="widget-title">GFS · ECMWF · ICON</div>
    <div class="widget-sub">
      Для каждого явления — матрица 2×2 · кто лучший?
    </div>
  </a>

  <!-- Сводка явлений -->
  <a class="widget widget-accent-blue" href="/compare/tushino">
    <div class="widget-header">
      <span>📋 Сводка явлений</span>
      <span>Туман · Гроза</span>
    </div>
    <div class="widget-title">Часы с явлениями</div>
    <div class="widget-sub">
      Сколько часов тумана, грозы, осадков — по каждой модели
    </div>
  </a>

</div>

""" + COMMON_JS + render_legend("analysis") + """
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
<style>
  .dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 16px;
    margin-top: 24px;
  }
  .widget {
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 22px;
    backdrop-filter: blur(14px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    text-decoration: none;
    color: var(--text-0);
    display: flex;
    flex-direction: column;
    min-height: 180px;
  }
  .widget:hover {
    transform: translateY(-3px);
    border-color: var(--border-hover);
    box-shadow: var(--card-shadow);
  }
  .widget::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0; transition: opacity 0.3s;
  }
  .widget:hover::before { opacity: 1; }

  .widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: var(--text-2);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
    font-weight: 600;
  }
  .widget-title {
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 8px;
    color: var(--text-0);
  }
  .widget-list {
    list-style: none;
    padding: 0;
    margin: 6px 0 0 0;
    font-size: 13px;
  }
  .widget-list li {
    padding: 7px 0;
    border-bottom: 1px solid rgba(120, 160, 255, 0.06);
    color: var(--text-1);
    display: flex;
    justify-content: space-between;
    gap: 12px;
  }
  .widget-list li:last-child { border-bottom: none; }
  .widget-list li span:last-child {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    color: var(--text-0);
    white-space: nowrap;
  }
  .widget-sub {
    font-size: 12px;
    color: var(--text-2);
    margin-top: 8px;
    line-height: 1.5;
  }
  .widget-accent-blue   { --accent: #4dabff; }
  .widget-accent-green  { --accent: #00e5a0; }
  .widget-accent-orange { --accent: #ffb547; }
  .widget-accent-purple { --accent: #a78bfa; }
  .widget-accent-red    { --accent: #ff5470; }
</style>
</head>
<body>
""" + render_header("theory") + """
<h1>📚 Теория и методы</h1>
<div class="sub">Методы прогноза · матрицы · индексы · учебные примеры</div>

<div class="dashboard-grid">

  <!-- Группа А: Методы прогноза -->
  <a class="widget widget-accent-blue" href="/theory/methods">
    <div class="widget-header">
      <span>🧭 Группа А</span>
      <span>Методы</span>
    </div>
    <div class="widget-title">Методы прогноза</div>
    <ul class="widget-list">
      <li><span>✈️ Авиационные прогнозы</span><span>K, LI, CAPE</span></li>
      <li><span>📐 Изоэнтропический</span><span>θ, PV</span></li>
      <li><span>🌡 Синоптический</span><span>925–300</span></li>
    </ul>
  </a>

  <!-- Группа Б: Матрицы -->
  <a class="widget widget-accent-orange" href="/theory/matrices">
    <div class="widget-header">
      <span>📋 Группа Б</span>
      <span>Матрицы</span>
    </div>
    <div class="widget-title">Матрицы и критерии</div>
    <ul class="widget-list">
      <li><span>Матрица 2×2</span><span>+</span></li>
      <li><span>Критерии Хандожко</span><span>p, H, τ, v</span></li>
      <li><span>Q, S, F1</span><span>+</span></li>
    </ul>
  </a>

  <!-- Группа В: Индексы -->
  <a class="widget widget-accent-purple" href="/theory/indices">
    <div class="widget-header">
      <span>⚡ Группа В</span>
      <span>Индексы</span>
    </div>
    <div class="widget-title">Индексы и явления</div>
    <ul class="widget-list">
      <li><span>LI · K-Index · CAPE</span><span>+</span></li>
      <li><span>ENSO · SSW · PV</span><span>+</span></li>
      <li><span>Складки тропопаузы</span><span>2 PVU</span></li>
    </ul>
  </a>

  <!-- Группа Г: Учебное -->
  <a class="widget widget-accent-green" href="/teaching">
    <div class="widget-header">
      <span>📖 Группа Г</span>
      <span>Учебное</span>
    </div>
    <div class="widget-title">Учебные материалы</div>
    <ul class="widget-list">
      <li><span>📚 Учебные примеры</span><span>+</span></li>
      <li><span>📝 Тесты по блокам</span><span>+</span></li>
      <li><span>📖 Библиография</span><span>+</span></li>
    </ul>
  </a>

</div>

""" + COMMON_JS + """
</body>
</html>
"""




INDEX_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Дашборд — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 16px;
    margin-top: 24px;
  }
  .widget {
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 22px;
    backdrop-filter: blur(14px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    text-decoration: none;
    color: var(--text-0);
    display: flex;
    flex-direction: column;
    min-height: 160px;
  }
  .widget:hover {
    transform: translateY(-3px);
    border-color: var(--border-hover);
    box-shadow: var(--card-shadow);
  }
  .widget::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0; transition: opacity 0.3s;
  }
  .widget:hover::before { opacity: 1; }

  .widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: var(--text-2);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 14px;
    font-weight: 600;
  }
  .widget-header .icon-lg {
    font-size: 18px;
    text-transform: none;
    letter-spacing: 0;
  }
  .widget-title {
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 6px;
    color: var(--text-0);
  }
  .widget-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 32px;
    font-weight: 700;
    line-height: 1.1;
    color: var(--accent);
    margin: 8px 0;
  }
  .widget-value.small {
    font-size: 22px;
  }
  .widget-sub {
    font-size: 12px;
    color: var(--text-2);
    margin-top: auto;
    line-height: 1.5;
  }
  .widget-list {
    list-style: none;
    padding: 0;
    margin: 10px 0 0 0;
    font-size: 13px;
  }
  .widget-list li {
    padding: 6px 0;
    border-bottom: 1px solid rgba(120, 160, 255, 0.06);
    color: var(--text-1);
    display: flex;
    justify-content: space-between;
    gap: 12px;
  }
  .widget-list li:last-child { border-bottom: none; }
  .widget-list li span:last-child {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    color: var(--text-0);
    white-space: nowrap;
  }
  .widget-accent-blue   { --accent: #4dabff; }
  .widget-accent-green  { --accent: #00e5a0; }
  .widget-accent-orange { --accent: #ffb547; }
  .widget-accent-purple { --accent: #a78bfa; }
  .widget-accent-red    { --accent: #ff5470; }
</style>
</head>
<body>
""" + render_header("home") + """
<h1>Дашборд погоды</h1>
<div class="sub">Сводка по моделям, анализ и инструменты · weather-msk</div>

<div class="dashboard-grid">

  <!-- 1. Прогноз -->
  <a class="widget widget-accent-blue" href="/forecast">
    <div class="widget-header">
      <span>🌍 Прогноз погоды</span>
      <span>GFS · ECMWF · ICON</span>
    </div>
    <div class="widget-title">Численные модели</div>
    <div class="widget-sub">
      Таблица · текст · графики · авиация · синоптика
    </div>
  </a>

  <!-- 2. Анализ -->
  <a class="widget widget-accent-green" href="/analysis">
    <div class="widget-header">
      <span>📊 Анализ и проверка</span>
      <span>MAE · RMSE</span>
    </div>
    <div class="widget-title">Верификация моделей</div>
    <div class="widget-sub">
      Сравнение с фактом · статистика · история ошибок · матрицы
    </div>
  </a>

  <!-- 3. Теория -->
  <a class="widget widget-accent-orange" href="/theory">
    <div class="widget-header">
      <span>📚 Теория и методы</span>
      <span>Богаткин · Хандожко</span>
    </div>
    <ul class="widget-list">
      <li><span>✈️ Авиационные прогнозы</span><span>K, LI, CAPE</span></li>
      <li><span>📋 Матрицы сопряжённости</span><span>p, H, τ, v, Q</span></li>
      <li><span>🌡 Синоптика по уровням</span><span>925–300 гПа</span></li>
      <li><span>🌀 Тропопауза и EPV</span><span>2 PVU</span></li>
    </ul>
  </a>

  <!-- 4. Карта -->
  <a class="widget widget-accent-purple" href="/maps">
    <div class="widget-header">
      <span>🗺 Карта погоды</span>
      <span>ICON-EU · GFS</span>
    </div>
    <div class="widget-title">Интерактивные слои</div>
    <div class="widget-sub">
      Температура · давление · ветер · осадки · облачность
    </div>
  </a>

  <!-- 5. Архив -->
  <a class="widget widget-accent-green" href="/archive">
    <div class="widget-header">
      <span>📂 Архив карт</span>
      <span>90 дней</span>
    </div>
    <div class="widget-value small">PNG · ZIP</div>
    <div class="widget-sub">
      Все прогоны ICON-EU и GFS · скачивание
    </div>
  </a>

  <!-- 6. Климат -->
  <a class="widget widget-accent-blue" href="/climate">
    <div class="widget-header">
      <span>🌍 Климатические индексы</span>
      <span>ENSO · SSW · PV</span>
    </div>
    <div class="widget-title">Крупномасштабные процессы</div>
    <div class="widget-sub">
      ONI · стратосферные потепления · полярный вихрь
    </div>
  </a>

  <!-- 7. Библиография -->
  <a class="widget widget-accent-orange" href="/bibliography">
    <div class="widget-header">
      <span>📖 Библиография</span>
      <span>Источники</span>
    </div>
    <ul class="widget-list">
      <li><span>Авиация</span><span>Богаткин</span></li>
      <li><span>Матрицы</span><span>Хандожко</span></li>
      <li><span>Синоптика</span><span>Хромов</span></li>
      <li><span>Климат</span><span>IPCC AR6</span></li>
    </ul>
  </a>

  <!-- 8. О проекте -->
  <a class="widget widget-accent-purple" href="/about">
    <div class="widget-header">
      <span>ℹ️ О проекте</span>
      <span>v1.0</span>
    </div>
    <div class="widget-title">weather-msk</div>
    <div class="widget-sub">
      Источники данных · модели · метрики · API
    </div>
  </a>

</div>

""" + COMMON_JS + """
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
""" + render_header("about") + """
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

""" + COMMON_JS + """
</body>
</html>
"""
