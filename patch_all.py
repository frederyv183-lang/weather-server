# -*- coding: utf-8 -*-
"""
Единый патч для weather-server.

Что делает:
  1. scheduler.py       — устойчивая проверка RENDER (job() не запускается на Render).
  2. server.py          — фильтр date_ru (день недели + месяц).
  3. analysis/synoptic.py — функция summarize_day().
  4. server.py          — импорт и использование summarize_day в /forecast/... и /forecast/point.
  5. ui/forecast.py     — блок сводки в TABLE_TEMPLATE.
  6. ui/synoptic.py     — блок сводки в AVIATION_HTML.

Идемпотентен: повторный запуск не ломает файлы (маркеры # [PATCH ...]).
Запуск: python patch_all.py
"""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent


# ============================================================
# УТИЛИТЫ
# ============================================================

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str):
    path.write_text(text, encoding="utf-8")
    print(f"  записан: {path.relative_to(ROOT)}")


def already_patched(text: str, marker: str) -> bool:
    return marker in text


# ============================================================
# 1. scheduler.py — устойчивая проверка RENDER
# ============================================================

def patch_scheduler():
    path = ROOT / "scheduler.py"
    if not path.exists():
        print("  SKIP scheduler.py: файл не найден")
        return
    text = read(path)
    marker = "# [PATCH scheduler.render_check]"
    if already_patched(text, marker):
        print("  SKIP scheduler.py: уже пропатчен")
        return

    # --- 1a. Заменяем _os проверку в init_scheduler ---
    old_block_1 = '''    import os as _os
    if _os.environ.get("RENDER") != "true":
        _scheduler.add_job(
            job,
            "cron",
            hour="*/3",
            minute=20,
            id="update_maps",
            replace_existing=True,
        )'''
    new_block_1 = '''    # [PATCH scheduler.render_check]
    import os as _os
    _render_env = (_os.environ.get("RENDER") or "").strip().lower()
    _is_render = _render_env in ("true", "1", "yes", "on")
    if not _is_render:
        _scheduler.add_job(
            job,
            "cron",
            hour="*/3",
            minute=20,
            id="update_maps",
            replace_existing=True,
        )'''

    if old_block_1 in text:
        text = text.replace(old_block_1, new_block_1)
    else:
        print("  WARN scheduler.py: блок _os не найден (возможно, уже изменён)")

    # --- 1b. Заменяем _os2 проверку в конце init_scheduler ---
    old_block_2 = '''    import os as _os2
    if _os2.environ.get("RENDER") != "true":
        try:
            import threading
            threading.Thread(target=job, daemon=True).start()
            print("[scheduler]     ", flush=True)
        except Exception as e:
            print(f"[scheduler]   : {e}", flush=True)'''
    new_block_2 = '''    # [PATCH scheduler.render_check]
    import os as _os2
    _render_env2 = (_os2.environ.get("RENDER") or "").strip().lower()
    _is_render2 = _render_env2 in ("true", "1", "yes", "on")
    if not _is_render2:
        try:
            import threading
            threading.Thread(target=job, daemon=True).start()
            print("[scheduler] Первая генерация запущена в фоне", flush=True)
        except Exception as e:
            print(f"[scheduler] Ошибка запуска: {e}", flush=True)'''

    if old_block_2 in text:
        text = text.replace(old_block_2, new_block_2)
    else:
        # Пробуем более гибкий вариант: ищем любую строку с RENDER != "true"
        # и заменяем на устойчивую проверку
        pattern = re.compile(
            r'import os as _os2\s*\n\s*if _os2\.environ\.get\("RENDER"\)\s*!=\s*"true":',
            re.MULTILINE,
        )
        if pattern.search(text):
            text = pattern.sub(
                '# [PATCH scheduler.render_check]\n'
                '    import os as _os2\n'
                '    _render_env2 = (_os2.environ.get("RENDER") or "").strip().lower()\n'
                '    _is_render2 = _render_env2 in ("true", "1", "yes", "on")\n'
                '    if not _is_render2:',
                text,
            )
        else:
            print("  WARN scheduler.py: блок _os2 не найден")

    # --- 1c. Заменяем _os3 проверку внутри job() ---
    old_block_3 = '''    import os as _os3
    print("[scheduler]   ...", flush=True)
    try:
        if _os3.environ.get("RENDER") == "true":'''
    new_block_3 = '''    # [PATCH scheduler.render_check]
    import os as _os3
    _render_env3 = (_os3.environ.get("RENDER") or "").strip().lower()
    _is_render3 = _render_env3 in ("true", "1", "yes", "on")
    print("[scheduler] Запуск генерации карт...", flush=True)
    try:
        if _is_render3:'''

    if old_block_3 in text:
        text = text.replace(old_block_3, new_block_3)
    else:
        pattern = re.compile(
            r'import os as _os3\s*\n\s*print\("[^"]*",\s*flush=True\)\s*\n\s*try:\s*\n\s*if _os3\.environ\.get\("RENDER"\)\s*==\s*"true":',
            re.MULTILINE,
        )
        if pattern.search(text):
            text = pattern.sub(
                '# [PATCH scheduler.render_check]\n'
                '    import os as _os3\n'
                '    _render_env3 = (_os3.environ.get("RENDER") or "").strip().lower()\n'
                '    _is_render3 = _render_env3 in ("true", "1", "yes", "on")\n'
                '    print("[scheduler] Запуск генерации карт...", flush=True)\n'
                '    try:\n'
                '        if _is_render3:',
                text,
            )
        else:
            print("  WARN scheduler.py: блок _os3 не найден")

    write(path, text)


# ============================================================
# 2. server.py — фильтр date_ru
# ============================================================

DATE_RU_NEW = '''@app.template_filter("date_ru")
def date_ru_filter(iso_date):
    """2024-01-15 -> 'Пн, 15 января'."""
    # [PATCH server.date_ru]
    from datetime import datetime

    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря",
    ]
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    try:
        d = datetime.strptime(str(iso_date)[:10], "%Y-%m-%d")
        return f"{weekdays[d.weekday()]}, {d.day} {months[d.month - 1]}"
    except Exception:
        return str(iso_date)'''


def patch_server_date_ru():
    path = ROOT / "server.py"
    if not path.exists():
        print("  SKIP server.py: файл не найден")
        return
    text = read(path)
    marker = "# [PATCH server.date_ru]"
    if already_patched(text, marker):
        print("  SKIP server.py date_ru: уже пропатчен")
        return

    # Ищем старую функцию date_ru_filter
    pattern = re.compile(
        r'@app\.template_filter\("date_ru"\)\s*\n'
        r'def date_ru_filter\(iso_date\):.*?(?=\n@app\.|\napp\.register_blueprint|\Z)',
        re.DOTALL,
    )
    if pattern.search(text):
        text = pattern.sub(DATE_RU_NEW + "\n\n\n", text)
        write(path, text)
    else:
        print("  WARN server.py: date_ru_filter не найден")


# ============================================================
# 3. analysis/synoptic.py — summarize_day
# ============================================================

SUMMARIZE_DAY = '''

# ============================================================
# СВОДКА ЗА СУТКИ
# ============================================================
# [PATCH analysis.synoptic.summarize_day]
def summarize_day(rows):
    """
    Возвращает сводку за сутки:
      {
        "situation": "циклон" | "антициклон" | ...,
        "phenomena": "туман, дождь" | "без существенных явлений",
        "phenomena_list": [...],
      }
    """
    if not rows:
        return {
            "situation": "нет данных",
            "phenomena": "нет данных",
            "phenomena_list": [],
        }

    # --- Обстановка: по среднему давлению ---
    pressures = [r.get("pressure_hpa") for r in rows if r.get("pressure_hpa") is not None]
    if pressures:
        p_avg = sum(pressures) / len(pressures)
        p_min = min(pressures)
        p_max = max(pressures)
        if p_avg < 1005:
            situation = "циклон"
        elif p_avg > 1020:
            situation = "антициклон"
        elif p_max - p_min > 10:
            situation = "гребень/ложбина"
        else:
            situation = "поле пониженного/повышенного давления"
    else:
        situation = "нет данных"

    # --- Явления: по weather_code и осадкам ---
    phenomena = set()
    for r in rows:
        code = r.get("weather_code")
        precip = r.get("precipitation_mm") or 0
        if code in (45, 48):
            phenomena.add("туман")
        if code in (95, 96, 99):
            phenomena.add("гроза")
        if code in (71, 73, 75, 77, 85, 86):
            phenomena.add("снег")
        elif precip > 0.1:
            phenomena.add("дождь")
        wind = r.get("wind_ms")
        if wind is not None and wind >= 12:
            phenomena.add("сильный ветер")

    phenomena_list = sorted(phenomena)
    phenomena_text = ", ".join(phenomena_list) if phenomena_list else "без существенных явлений"

    return {
        "situation": situation,
        "phenomena": phenomena_text,
        "phenomena_list": phenomena_list,
    }
'''


def patch_synoptic():
    path = ROOT / "analysis" / "synoptic.py"
    if not path.exists():
        print("  SKIP analysis/synoptic.py: файл не найден")
        return
    text = read(path)
    marker = "# [PATCH analysis.synoptic.summarize_day]"
    if already_patched(text, marker):
        print("  SKIP analysis/synoptic.py: уже пропатчен")
        return
    text = text.rstrip() + "\n" + SUMMARIZE_DAY
    write(path, text)


# ============================================================
# 4. server.py — использовать summarize_day в маршрутах
# ============================================================

def patch_server_use_summary():
    path = ROOT / "server.py"
    if not path.exists():
        print("  SKIP server.py: файл не найден")
        return
    text = read(path)
    marker = "# [PATCH server.use_summary]"
    if already_patched(text, marker):
        print("  SKIP server.py use_summary: уже пропатчен")
        return

    # --- 4a. Добавляем импорт summarize_day ---
    old_import = "from analysis.synoptic import analyze_synoptic"
    new_import = "from analysis.synoptic import analyze_synoptic  # [PATCH server.use_summary]\ntry:\n    from analysis.synoptic import summarize_day\nexcept ImportError:\n    summarize_day = None"
    if old_import in text and "summarize_day" not in text:
        text = text.replace(old_import, new_import, 1)

    # --- 4b. Заменяем блок формирования days_list в /forecast/<model>/<station> ---
    old_block_1 = '''    days_list = []
    for day, rows in by_day.items():
        days_list.append({
            "date": day,
            "rows": rows,
            "events": [ev for ev in events if ev["time"][:10] == day],
        })'''
    new_block_1 = '''    days_list = []
    for day, rows in by_day.items():
        summary = summarize_day(rows) if summarize_day else {}
        days_list.append({
            "date": day,
            "rows": rows,
            "events": [ev for ev in events if ev["time"][:10] == day],
            "summary": summary,
        })  # [PATCH server.use_summary]'''

    if old_block_1 in text:
        text = text.replace(old_block_1, new_block_1)

    # --- 4c. Заменяем блок формирования days_list в /forecast/point ---
    old_block_2 = '''    days_list = []
    for day, rows in by_day.items():
        days_list.append({
            "date": day,
            "rows": rows,
            "events": [ev for ev in events if ev["time"][:10] == day],
        })'''
    # тот же самый блок, что и 4b — replace уже сработал, повторно не нужно

    write(path, text)


# ============================================================
# 5. ui/forecast.py — блок сводки в TABLE_TEMPLATE
# ============================================================

def patch_ui_forecast():
    path = ROOT / "ui" / "forecast.py"
    if not path.exists():
        print("  SKIP ui/forecast.py: файл не найден")
        return
    text = read(path)
    marker = "<!-- [PATCH ui.forecast.day_summary] -->"
    if already_patched(text, marker):
        print("  SKIP ui/forecast.py: уже пропатчен")
        return

    # --- 5a. Добавляем CSS в TABLE_TEMPLATE ---
    css_old = '''  .error-box {
    background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    border-radius: 12px; padding: 16px; color: #ff5470;
    margin: 16px 0;
  }

  @media (max-width: 900px) {'''
    css_new = '''  .error-box {
    background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    border-radius: 12px; padding: 16px; color: #ff5470;
    margin: 16px 0;
  }

  /* [PATCH ui.forecast.day_summary] */
  .day-summary {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin: 8px 0 12px 0;
    padding: 10px 14px;
    background: rgba(77, 171, 255, 0.06);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    font-size: 13px;
    color: var(--text-1);
  }
  .day-summary .situation {
    font-weight: 700;
    color: var(--accent);
  }
  .day-summary .phenomena {
    color: var(--text-0);
  }

  @media (max-width: 900px) {'''
    if css_old in text:
        text = text.replace(css_old, css_new)

    # --- 5b. Добавляем блок сводки в разметку ---
    html_old = '''  <div class="day-header">
    <div class="day-title">📅 {{ day.date | date_ru }}</div>
    <div class="day-events">
      {% for ev in day.events[:6] %}
        <span class="event-badge synoptic-{{ ev.type }}">{{ ev.text }}</span>
      {% endfor %}
    </div>
  </div>

  <div style="overflow-x:auto;">'''
    html_new = '''  <div class="day-header">
    <div class="day-title">📅 {{ day.date | date_ru }}</div>
    <div class="day-events">
      {% for ev in day.events[:6] %}
        <span class="event-badge synoptic-{{ ev.type }}">{{ ev.text }}</span>
      {% endfor %}
    </div>
  </div>

  <!-- [PATCH ui.forecast.day_summary] -->
  {% if day.summary %}
  <div class="day-summary">
    <span class="situation">🌍 {{ day.summary.situation }}</span>
    <span class="phenomena">{{ day.summary.phenomena }}</span>
  </div>
  {% endif %}

  <div style="overflow-x:auto;">'''
    if html_old in text:
        text = text.replace(html_old, html_new)

    write(path, text)


# ============================================================
# 6. ui/synoptic.py — блок сводки в AVIATION_HTML
# ============================================================

def patch_ui_synoptic():
    path = ROOT / "ui" / "synoptic.py"
    if not path.exists():
        print("  SKIP ui/synoptic.py: файл не найден")
        return
    text = read(path)
    marker = "<!-- [PATCH ui.synoptic.day_summary] -->"
    if already_patched(text, marker):
        print("  SKIP ui/synoptic.py: уже пропатчен")
        return

    # --- 6a. CSS ---
    css_old = '''  .error-box {
    background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    border-radius: 12px; padding: 16px; color: #ff5470;
    margin: 16px 0;
  }
</style>
</head>
<body>

""" + render_header("forecast") + """
<h1>✈️ Авиационные прогнозы</h1>'''
    css_new = '''  .error-box {
    background: rgba(255,84,112,0.12);
    border: 1px solid rgba(255,84,112,0.4);
    border-radius: 12px; padding: 16px; color: #ff5470;
    margin: 16px 0;
  }

  /* [PATCH ui.synoptic.day_summary] */
  .day-summary {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin: 8px 0 12px 0;
    padding: 10px 14px;
    background: rgba(77, 171, 255, 0.06);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    font-size: 13px;
    color: var(--text-1);
  }
  .day-summary .situation {
    font-weight: 700;
    color: var(--accent);
  }
  .day-summary .phenomena {
    color: var(--text-0);
  }
</style>
</head>
<body>

""" + render_header("forecast") + """
<h1>✈️ Авиационные прогнозы</h1>'''
    if css_old in text:
        text = text.replace(css_old, css_new)

    # --- 6b. HTML ---
    html_old = '''<div class="day-block fade-in">
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
        <th>K</th>'''
    html_new = '''<div class="day-block fade-in">
  <div class="day-header">
    <div class="day-title">📅 {{ day.date | date_ru }}</div>
  </div>

  <!-- [PATCH ui.synoptic.day_summary] -->
  {% if day.summary %}
  <div class="day-summary">
    <span class="situation">🌍 {{ day.summary.situation }}</span>
    <span class="phenomena">{{ day.summary.phenomena }}</span>
  </div>
  {% endif %}

  <div style="overflow-x:auto;">
  <table class="hour-table">
    <thead>
      <tr>
        <th>Час</th>
        <th>Иконка</th>
        <th>T, °C</th>
        <th>Td, °C</th>
        <th>K</th>'''
    if html_old in text:
        text = text.replace(html_old, html_new)

    write(path, text)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("Единый патч weather-server")
    print("=" * 60)

    print("\n[1/6] scheduler.py — устойчивая проверка RENDER")
    patch_scheduler()

    print("\n[2/6] server.py — фильтр date_ru")
    patch_server_date_ru()

    print("\n[3/6] analysis/synoptic.py — summarize_day")
    patch_synoptic()

    print("\n[4/6] server.py — использование summarize_day")
    patch_server_use_summary()

    print("\n[5/6] ui/forecast.py — блок сводки в TABLE_TEMPLATE")
    patch_ui_forecast()

    print("\n[6/6] ui/synoptic.py — блок сводки в AVIATION_HTML")
    patch_ui_synoptic()

    print("\n" + "=" * 60)
    print("Готово. Проверьте синтаксис:")
    print("  python -c \"import ast; ast.parse(open('scheduler.py', encoding='utf-8').read()); print('scheduler OK')\"")
    print("  python -c \"import ast; ast.parse(open('server.py', encoding='utf-8').read()); print('server OK')\"")
    print("  python -c \"import ast; ast.parse(open('analysis/synoptic.py', encoding='utf-8').read()); print('synoptic OK')\"")
    print("  python -c \"import ast; ast.parse(open('ui/forecast.py', encoding='utf-8').read()); print('ui/forecast OK')\"")
    print("  python -c \"import ast; ast.parse(open('ui/synoptic.py', encoding='utf-8').read()); print('ui/synoptic OK')\"")
    print("=" * 60)


if __name__ == "__main__":
    main()