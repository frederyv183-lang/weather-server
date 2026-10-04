# -*- coding: utf-8 -*-
"""
Одной командой добавляет раздел «Синоптические карты» в проект weather-server.

Что делает:
  1. Бэкап затрагиваемых файлов в .backup_synoptic/
  2. Создаёт synoptic_maps/ (config.py, generator.py, routes.py, __init__.py)
  3. Создаёт ui/synoptic_maps.py
  4. Патчит ui/__init__.py (добавляет реэкспорт)
  5. Патчит ui/styles.py (добавляет пункт в render_header)
  6. Патчит server.py (регистрирует blueprint)
  7. Патчит scheduler.py (добавляет задачу)
  8. Патчит Dockerfile (ставит libeccodes0)
  9. Проверяет синтаксис и импорт

Запуск:
    python add_synoptic_maps.py

Откат:
    удалить synoptic_maps/, ui/synoptic_maps.py
    восстановить файлы из .backup_synoptic/
"""

import io
import os
import re
import shutil
import sys
from pathlib import Path

# ----------------------------------------------------------------
# UTF-8 вывод в Windows
# ----------------------------------------------------------------
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8",
                                  errors="replace")


ROOT = Path.cwd()
BACKUP_DIR = ROOT / ".backup_synoptic"


# ================================================================
# УТИЛИТЫ
# ================================================================
def backup(path: Path) -> None:
    """Копирует файл в .backup_synoptic/ с сохранением структуры."""
    if not path.exists():
        return
    rel = path.relative_to(ROOT)
    dst = BACKUP_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)
    print(f"  ← бэкап: {rel}")


def write_file(path: Path, content: str) -> None:
    """Пишет файл, создавая папки."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  ✓ {path.relative_to(ROOT)}  ({len(content)} симв.)")


def patch_file(path: Path, patches: list) -> bool:
    """
    Патчит файл: список (pattern, replacement, описание).
    Возвращает True, если все патчи применены.
    """
    if not path.exists():
        print(f"  ✗ {path.relative_to(ROOT)}: не существует")
        return False

    backup(path)
    text = path.read_text(encoding="utf-8")
    original = text

    for pattern, replacement, desc in patches:
        new_text, n = re.subn(pattern, replacement, text, count=1)
        if n == 0:
            print(f"  ⚠ паттерн не найден: {desc}")
        else:
            text = new_text
            print(f"  ✓ применён патч: {desc}")

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def check_syntax(path: Path) -> bool:
    """Проверяет синтаксис Python-файла."""
    try:
        src = path.read_text(encoding="utf-8")
        compile(src, str(path), "exec")
        print(f"  ✓ {path.relative_to(ROOT)}: синтаксис OK")
        return True
    except SyntaxError as e:
        print(f"  ✗ {path.relative_to(ROOT)}: SyntaxError: {e}")
        return False


# ================================================================
# ШАБЛОНЫ ФАЙЛОВ
# ================================================================

CONFIG_PY = '''# -*- coding: utf-8 -*-
"""Конфигурация раздела «Синоптические карты»."""

# Уровни абсолютной топографии (гПа) и типичные диапазоны высот (м)
AT_LEVELS = {
    850: {"name": "АТ-850", "range": (1000, 1700), "step": 20},
    700: {"name": "АТ-700", "range": (2500, 3300), "step": 40},
    500: {"name": "АТ-500", "range": (4800, 6000), "step": 40},
    300: {"name": "АТ-300", "range": (8000, 9800), "step": 80},
    200: {"name": "АТ-200", "range": (10500, 12500), "step": 100},
    100: {"name": "АТ-100", "range": (15000, 16800), "step": 100},
}

# Регионы: (lon_min, lon_max, lat_min, lat_max)
REGIONS = {
    "world":    {"name": "Весь мир",            "bbox": (-180, 180, -90, 90)},
    "nh":       {"name": "Северное полушарие",  "bbox": (-180, 180, 0, 90)},
    "europe":   {"name": "Европа",              "bbox": (-25, 60, 30, 75)},
    "etr":      {"name": "ЕТР",                 "bbox": (20, 60, 40, 70)},
    "atlantic": {"name": "Северная Атлантика",  "bbox": (-70, 20, 30, 70)},
    "asia":     {"name": "Азия",                "bbox": (60, 150, 10, 70)},
}

# Модели
MODELS = {
    "gfs": {"name": "GFS (США)", "herbie_model": "gfs"},
}

# Шаги прогноза (часы)
STEPS = [0, 12, 24, 48, 72]

# Дополнительные слои (пока не реализованы, для расширения)
OVERLAY_LAYERS = {
    "t_850":  {"name": "Температура 850 гПа", "variable": "temperature_850hPa"},
    "t_500":  {"name": "Температура 500 гПа", "variable": "temperature_500hPa"},
    "wind":   {"name": "Ветер 500 гПа",       "variable": "wind_speed_500hPa"},
    "rh_700": {"name": "Влажность 700 гПа",   "variable": "relative_humidity_700hPa"},
}
'''


GENERATOR_PY = '''# -*- coding: utf-8 -*-
"""
Генерация глобальных карт абсолютной топографии (АТ) через NOAA GFS.

Использует herbie-data для скачивания GRIB-файлов GFS и Cartopy
для отрисовки изогипс на карте Robinson.
"""

import os
import traceback
from datetime import datetime, timedelta, timezone

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from synoptic_maps.config import AT_LEVELS, REGIONS


OUTPUT_DIR = "static/synoptic_maps"
ARCHIVE_DIR = os.path.join(OUTPUT_DIR, "archive")


def get_latest_gfs_run():
    """Ближайший доступный прогон GFS (задержка ~5 часов)."""
    now = datetime.now(timezone.utc) - timedelta(hours=5)
    hour = (now.hour // 6) * 6
    return now.replace(hour=hour, minute=0, second=0, microsecond=0)


def read_gh_field(run, level_hpa, step_h, region_bbox):
    """
    Читает поле HGT (geopotential height) из GFS GRIB.
    Возвращает (lons, lats, gh_2d).
    """
    from herbie import Herbie

    H = Herbie(
        run.strftime("%Y-%m-%d %H:%M"),
        model="gfs",
        product="pgrb2.0p25",
        fxx=step_h,
    )

    # Скачиваем только HGT на нужном уровне (маленький сабсет)
    ds = H.xarray(f"HGT:{level_hpa} mb")
    if isinstance(ds, list):
        ds = ds[0]

    var = list(ds.data_vars)[0]
    lats = ds.latitude.values
    lons = ds.longitude.values

    # Приводим долготы к -180..180
    if lons.max() > 180:
        lons = np.where(lons > 180, lons - 360, lons)
        order = np.argsort(lons)
        lons = lons[order]
        ds = ds.isel(longitude=order)

    if lats[0] > lats[-1]:
        lats = lats[::-1]
        ds = ds.isel(latitude=slice(None, None, -1))

    lon_min, lon_max, lat_min, lat_max = region_bbox
    mask_lon = (lons >= lon_min) & (lons <= lon_max)
    mask_lat = (lats >= lat_min) & (lats <= lat_max)

    lons_c = lons[mask_lon]
    lats_c = lats[mask_lat]
    gh_2d = ds[var].values[np.ix_(mask_lat, mask_lon)]

    return lons_c, lats_c, gh_2d


def draw_at_map(lons, lats, gh_2d, level_hpa, step_h, run,
                output_path, region_bbox):
    """Рисует карту АТ и сохраняет в output_path."""
    level_info = AT_LEVELS[level_hpa]
    gh_min, gh_max = level_info["range"]
    step = level_info["step"]

    # Определяем проекцию по региону
    if region_bbox == (-180, 180, -90, 90):
        proj = ccrs.Robinson()
    elif region_bbox[1] - region_bbox[0] > 180:
        proj = ccrs.Robinson()
    else:
        proj = ccrs.PlateCarree()

    fig = plt.figure(figsize=(16, 10), dpi=100)
    ax = plt.axes(projection=proj)

    if isinstance(proj, ccrs.Robinson):
        ax.set_global()
    else:
        ax.set_extent(region_bbox, crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.COASTLINE, linewidth=0.5,
                   edgecolor="#555555", zorder=3)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3,
                   edgecolor="#888888", linestyle="--",
                   alpha=0.5, zorder=3)
    ax.add_feature(cfeature.LAND, facecolor="#f5f5dc", alpha=0.3, zorder=1)

    levels = np.arange(gh_min, gh_max + step, step)
    cs = ax.contour(lons, lats, gh_2d, levels=levels,
                    colors="black", linewidths=1.2,
                    transform=ccrs.PlateCarree(), zorder=4)
    ax.clabel(cs, inline=True, fontsize=8, fmt="%d")

    run_str = run.strftime("%d.%m.%Y %H:%M UTC")
    title = f"АТ-{level_hpa} гПа · +{step_h} ч · GFS · {run_str}"
    ax.set_title(title, fontsize=14, pad=10, fontweight="bold")

    plt.savefig(output_path, bbox_inches="tight", dpi=100,
                facecolor="white")
    plt.close(fig)


def generate_at_maps(levels=(500,), steps=(0, 24),
                     regions=("nh",)):
    """Генерирует карты для всех комбинаций level × step × region."""
    run = get_latest_gfs_run()
    stamp = run.strftime("%Y%m%d%H")
    year, month, day = stamp[:4], stamp[4:6], stamp[6:8]

    out_dir = os.path.join(ARCHIVE_DIR, year, month, day)
    os.makedirs(out_dir, exist_ok=True)

    results = []
    for region_key in regions:
        bbox = REGIONS[region_key]["bbox"]
        for level in levels:
            for step in steps:
                try:
                    lons, lats, gh = read_gh_field(run, level, step, bbox)
                    fname = (f"gfs_{stamp}_{step:03d}"
                             f"_at{level}_{region_key}.png")
                    out_path = os.path.join(out_dir, fname)
                    draw_at_map(lons, lats, gh, level, step, run,
                                out_path, bbox)
                    results.append(out_path)
                    print(f"[synoptic_maps] ✓ {out_path}", flush=True)
                except Exception as e:
                    print(f"[synoptic_maps] ✗ level={level} "
                          f"step={step} region={region_key}: {e}",
                          flush=True)
                    traceback.print_exc()

    return results
'''


ROUTES_PY = '''# -*- coding: utf-8 -*-
"""Маршруты для раздела /synoptic-maps."""

import os
from flask import Blueprint, jsonify, render_template_string, request

from synoptic_maps.config import (
    AT_LEVELS, REGIONS, MODELS, STEPS, OVERLAY_LAYERS,
)
from synoptic_maps.generator import generate_at_maps, ARCHIVE_DIR
from ui import SYNOPTIC_MAPS_HTML


synoptic_maps_bp = Blueprint("synoptic_maps", __name__)


@synoptic_maps_bp.route("/synoptic-maps")
def synoptic_maps_page():
    """Страница синоптических карт АТ."""
    return render_template_string(
        SYNOPTIC_MAPS_HTML,
        levels=AT_LEVELS,
        regions=REGIONS,
        models=MODELS,
        steps=STEPS,
        overlays=OVERLAY_LAYERS,
    )


@synoptic_maps_bp.route("/api/synoptic-maps/list")
def api_at_list():
    """Список доступных PNG-карт АТ."""
    if not os.path.isdir(ARCHIVE_DIR):
        return jsonify({"files": []})
    files = []
    for root, _, names in os.walk(ARCHIVE_DIR):
        for name in names:
            if name.endswith(".png") and "_at" in name:
                rel = os.path.relpath(os.path.join(root, name), ARCHIVE_DIR)
                files.append(rel.replace(os.sep, "/"))
    return jsonify({"files": sorted(files, reverse=True)})


@synoptic_maps_bp.route("/api/synoptic-maps/generate", methods=["POST"])
def api_at_generate():
    """Ручной запуск генерации карт АТ."""
    data = request.get_json() or {}
    levels = data.get("levels", [500])
    steps = data.get("steps", [0, 24])
    regions = data.get("regions", ["nh"])
    try:
        files = generate_at_maps(
            levels=tuple(levels), steps=tuple(steps), regions=tuple(regions),
        )
        return jsonify({"status": "ok", "files": files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
'''


INIT_PY = '''# -*- coding: utf-8 -*-
"""Раздел «Синоптические карты» (глобальные карты АТ)."""
'''


SYNOPTIC_MAPS_HTML_PY = '''# -*- coding: utf-8 -*-
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

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; CartoDB &copy; OpenStreetMap',
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
        model + '_\\\\d{10}_' + step3
        + '_at' + currentLevel + '_' + region + '\\\\.png$'
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
'''


# ================================================================
# ОСНОВНАЯ ЛОГИКА
# ================================================================
def main():
    print("=" * 70)
    print("Добавление раздела «Синоптические карты»")
    print("=" * 70)

    # 1. Создать synoptic_maps/
    print("\n[1] Создание пакета synoptic_maps/")
    write_file(ROOT / "synoptic_maps" / "__init__.py", INIT_PY)
    write_file(ROOT / "synoptic_maps" / "config.py", CONFIG_PY)
    write_file(ROOT / "synoptic_maps" / "generator.py", GENERATOR_PY)
    write_file(ROOT / "synoptic_maps" / "routes.py", ROUTES_PY)

    # 2. ui/synoptic_maps.py
    print("\n[2] Создание ui/synoptic_maps.py")
    write_file(ROOT / "ui" / "synoptic_maps.py", SYNOPTIC_MAPS_HTML_PY)

    # 3. Патч ui/__init__.py
    print("\n[3] Патч ui/__init__.py")
    init_py = ROOT / "ui" / "__init__.py"
    patch_file(init_py, [
        (
            r"(from ui\.tests import \([^)]+\))",
            r"\1\n\nfrom ui.synoptic_maps import (\n"
            r"    SYNOPTIC_MAPS_HTML,\n)",
            "добавить импорт из ui.synoptic_maps",
        ),
        (
            r'("TESTS_HTML",)',
            r'\1\n    "SYNOPTIC_MAPS_HTML",',
            "добавить SYNOPTIC_MAPS_HTML в __all__",
        ),
    ])

    # 4. Патч ui/styles.py (render_header)
    print("\n[4] Патч ui/styles.py (render_header)")
    styles_py = ROOT / "ui" / "styles.py"
    patch_file(styles_py, [
        (
            r'(\("forecast",\s*"/forecast",\s*"Прогнозы"\),)',
            r'\1\n        ("synoptic_maps", "/synoptic-maps", "Синопт. карты"),',
            "добавить пункт «Синопт. карты» в render_header",
        ),
    ])

    # 5. Патч server.py
    print("\n[5] Патч server.py")
    server_py = ROOT / "server.py"
    patch_file(server_py, [
        (
            r"(from maps_routes import maps_bp\s*\n)",
            r"\1from synoptic_maps.routes import synoptic_maps_bp\n",
            "добавить импорт synoptic_maps_bp",
        ),
        (
            r"(app\.register_blueprint\(maps_bp\)\s*\n)",
            r"\1app.register_blueprint(synoptic_maps_bp)\n",
            "зарегистрировать synoptic_maps_bp",
        ),
    ])

    # 6. Патч scheduler.py
    print("\n[6] Патч scheduler.py")
    scheduler_py = ROOT / "scheduler.py"
    patch_file(scheduler_py, [
        (
            r"(def job\(\):)",
            r'''def job_synoptic_maps():
    """Генерация карт АТ каждые 6 часов."""
    print("[scheduler] Генерация синоптических карт АТ...", flush=True)
    try:
        from synoptic_maps.generator import generate_at_maps
        files = generate_at_maps(
            levels=(500, 850),
            steps=(0, 24),
            regions=("nh", "europe"),
        )
        print(f"[scheduler] Готово: {len(files)} карт АТ", flush=True)
    except Exception as e:
        print(f"[scheduler] Ошибка синоптических карт: {e}", flush=True)


\1''',
            "добавить job_synoptic_maps()",
        ),
        (
            r'(# Очистка архива раз в сутки в 03:00 UTC)',
            r'''# Генерация синоптических карт каждые 6 часов (в :40)
    _scheduler.add_job(
        job_synoptic_maps,
        "cron",
        hour="*/6",
        minute=40,
        id="synoptic_maps",
        replace_existing=True,
    )

    \1''',
            "добавить задачу в init_scheduler",
        ),
    ])

    # 7. Патч Dockerfile
    print("\n[7] Патч Dockerfile")
    dockerfile = ROOT / "Dockerfile"
    if dockerfile.exists():
        patch_file(dockerfile, [
            (
                r"(RUN pip install[^\n]*)",
                r"RUN apt-get update && apt-get install -y \\\n"
                r"    libeccodes0 libeccodes-tools \\\n"
                r"    && rm -rf /var/lib/apt/lists/*\n"
                r"\1",
                "установить libeccodes0 перед pip install",
            ),
        ])
    else:
        print("  ⚠ Dockerfile не найден — пропускаю")

    # 8. Проверка синтаксиса
    print("\n[8] Проверка синтаксиса")
    files_to_check = [
        ROOT / "synoptic_maps" / "__init__.py",
        ROOT / "synoptic_maps" / "config.py",
        ROOT / "synoptic_maps" / "generator.py",
        ROOT / "synoptic_maps" / "routes.py",
        ROOT / "ui" / "synoptic_maps.py",
        ROOT / "ui" / "__init__.py",
        ROOT / "ui" / "styles.py",
        ROOT / "server.py",
        ROOT / "scheduler.py",
    ]
    all_ok = True
    for f in files_to_check:
        if not check_syntax(f):
            all_ok = False

    # Итог
    print()
    print("=" * 70)
    if all_ok:
        print("✓ ГОТОВО")
        print("=" * 70)
        print()
        print("Что дальше:")
        print("  1. Убедитесь, что venv активирован:")
        print("       .\\venv\\Scripts\\Activate.ps1")
        print()
        print("  2. Проверьте импорт:")
        print("       python -c \"import server; print('OK')\"")
        print()
        print("  3. Запустите сервер:")
        print("       python server.py")
        print()
        print("  4. Откройте: http://localhost:5000/synoptic-maps")
        print()
        print("  5. Нажмите «Сгенерировать» — первые карты появятся через 1-3 мин")
        print()
        print("  6. Если всё работает — закоммитьте:")
        print("       git add synoptic_maps/ ui/synoptic_maps.py ui/__init__.py \\")
        print("               ui/styles.py server.py scheduler.py Dockerfile")
        print("       git commit -m \"Добавлен раздел Синоптические карты (АТ)\"")
        print("       git push origin main")
        print()
        print("Откат:")
        print("  Удалить synoptic_maps/ и ui/synoptic_maps.py")
        print("  Восстановить файлы из .backup_synoptic/")
    else:
        print("✗ БЫЛИ ОШИБКИ")
        print("=" * 70)
        print("Проверьте вывод выше. Откат:")
        print("  Удалить synoptic_maps/ и ui/synoptic_maps.py")
        print("  Восстановить файлы из .backup_synoptic/")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())