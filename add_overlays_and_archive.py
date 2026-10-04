# -*- coding: utf-8 -*-
"""
Одной командой:
  1. Подключает оверлеи (T, ветер, RH) в раздел «Синоптические карты»
  2. Добавляет архив карт АТ (хранение 3 дня) с UI
  3. Добавляет таймкод (valid time) на карту в правом нижнем углу
  4. Применяет рекомендации по загрузке: NOMADS-приоритет, timeout=180,
     retry, remove_grib=False, HERBIE_SAVE_DIR
  5. Обновляет Dockerfile для Render

Запуск:
    python add_overlays_and_archive.py

Откат:
    Восстановить файлы из .backup_overlays/
"""

import io
import os
import re
import shutil
import sys
from pathlib import Path

# UTF-8 вывод
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8",
                                  errors="replace")


ROOT = Path.cwd()
BACKUP_DIR = ROOT / ".backup_overlays"


# ================================================================
# УТИЛИТЫ
# ================================================================
def backup(path: Path) -> None:
    if not path.exists():
        return
    rel = path.relative_to(ROOT)
    dst = BACKUP_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)
    print(f"  ← бэкап: {rel}")


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  ✓ {path.relative_to(ROOT)}  ({len(content)} симв.)")


def check_syntax(path: Path) -> bool:
    try:
        src = path.read_text(encoding="utf-8")
        compile(src, str(path), "exec")
        print(f"  ✓ {path.relative_to(ROOT)}: синтаксис OK")
        return True
    except SyntaxError as e:
        print(f"  ✗ {path.relative_to(ROOT)}: SyntaxError: {e}")
        return False


# ================================================================
# НОВЫЙ GENERATOR.PY (полная замена)
# ================================================================
GENERATOR_PY = r'''# -*- coding: utf-8 -*-
"""
Генерация глобальных карт абсолютной топографии (АТ) через NOAA GFS.

Поддерживает:
  - Базовый слой: изогипсы HGT на любом уровне (850/700/500/300/200/100)
  - Оверлеи: TMP (заливка), UGRD/VGRD (барбы), RH (изолинии)
  - Таймкод (valid time) в правом нижнем углу
  - Retry при таймауте NOMADS/AWS
"""

import os
import time
import traceback
from datetime import datetime, timedelta, timezone

import numpy as np
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from synoptic_maps.config import AT_LEVELS, REGIONS


OUTPUT_DIR = "static/synoptic_maps"
ARCHIVE_DIR = os.path.join(OUTPUT_DIR, "archive")

# Сколько дней хранить архив
ARCHIVE_RETENTION_DAYS = 3

# Таймаут и число попыток скачивания GRIB
DOWNLOAD_TIMEOUT = 180
DOWNLOAD_RETRIES = 2
DOWNLOAD_RETRY_DELAY = 5   # секунд между попытками


def get_latest_gfs_run():
    """Ближайший гарантированно доступный прогон GFS (задержка ~5 ч)."""
    now = datetime.now(timezone.utc) - timedelta(hours=5)
    hour = (now.hour // 6) * 6
    return now.replace(hour=hour, minute=0, second=0, microsecond=0)


def read_at_field(run, level_hpa, step_h, region_bbox, overlays=None):
    """
    Читает поле HGT + опционально TMP, UGRD/VGRD, RH из GRIB GFS.

    Возвращает dict:
        {
          "lons": 1D np.array, "lats": 1D np.array,
          "gh":   2D (м),
          "t":    2D (°C) или None,
          "u":    2D (м/с) или None,
          "v":    2D (м/с) или None,
          "rh":   2D (%) или None,
        }
    """
    from herbie import Herbie

    overlays = list(overlays or [])

    # Приоритет источников: NOMADS первый (обычно быстрее из РФ)
    H = Herbie(
        run.strftime("%Y-%m-%d %H:%M"),
        model="gfs",
        product="pgrb2.0p25",
        fxx=step_h,
        priority=["nomads", "aws"],
        verbose=False,
    )

    # Собираем список переменных для скачивания
    search_parts = [f"HGT:{level_hpa} mb"]
    if "t_850" in overlays and level_hpa == 850:
        search_parts.append("TMP:850 mb")
    if "t_500" in overlays and level_hpa == 500:
        search_parts.append("TMP:500 mb")
    if "wind" in overlays:
        search_parts.append(f"UGRD:{level_hpa} mb")
        search_parts.append(f"VGRD:{level_hpa} mb")
    if "rh_700" in overlays and level_hpa == 700:
        search_parts.append("RH:700 mb")

    search = "|".join(search_parts)

    # --- Retry при таймауте ---
    ds = None
    last_err = None
    for attempt in range(1, DOWNLOAD_RETRIES + 1):
        try:
            ds = H.xarray(
                search,
                download_kwargs={"timeout": DOWNLOAD_TIMEOUT},
                remove_grib=False,
            )
            break
        except Exception as e:
            last_err = e
            print(f"[synoptic_maps] Попытка {attempt}/{DOWNLOAD_RETRIES} "
                  f"не удалась: {e}", flush=True)
            if attempt < DOWNLOAD_RETRIES:
                time.sleep(DOWNLOAD_RETRY_DELAY)

    if ds is None:
        raise RuntimeError(f"Скачивание не удалось после "
                           f"{DOWNLOAD_RETRIES} попыток: {last_err}")

    # cfgrib иногда возвращает список датасетов
    if isinstance(ds, list):
        ds = xr.merge(ds, compat="override")

    # --- Приведение координат ---
    lons = ds.longitude.values
    if lons.max() > 180:
        lons = np.where(lons > 180, lons - 360, lons)
        order = np.argsort(lons)
        lons = lons[order]
        ds = ds.isel(longitude=order)

    lats = ds.latitude.values
    if lats[0] > lats[-1]:
        lats = lats[::-1]
        ds = ds.isel(latitude=slice(None, None, -1))

    # --- Обрезка по региону ---
    lon_min, lon_max, lat_min, lat_max = region_bbox
    mask_lon = (lons >= lon_min) & (lons <= lon_max)
    mask_lat = (lats >= lat_min) & (lats <= lat_max)

    lons_c = lons[mask_lon]
    lats_c = lats[mask_lat]

    def _get(var_candidates):
        for name in var_candidates:
            if name in ds.data_vars:
                return ds[name].values[np.ix_(mask_lat, mask_lon)]
        # Поиск по подстроке
        for name in ds.data_vars:
            for cand in var_candidates:
                if cand.lower() in name.lower():
                    return ds[name].values[np.ix_(mask_lat, mask_lon)]
        return None

    gh = _get(["gh", "hgt"])
    if gh is None:
        gh = ds[list(ds.data_vars)[0]].values[np.ix_(mask_lat, mask_lon)]

    t = _get(["t", "tmp"])
    if t is not None:
        # K → °C (GFS на изобарических уровнях отдаёт T в K)
        t_mean = float(np.nanmean(t))
        if t_mean > 100:
            t = t - 273.15

    u = _get(["u", "ugrd"])
    v = _get(["v", "vgrd"])
    rh = _get(["r", "rh"])

    return {
        "lons": lons_c,
        "lats": lats_c,
        "gh": gh,
        "t": t,
        "u": u,
        "v": v,
        "rh": rh,
    }


def _fmt_valid_time(run, step_h):
    """Возвращает строку 'valid time' = run + step_h часов."""
    valid = run + timedelta(hours=step_h)
    return valid.strftime("%d.%m.%Y %H:%M UTC")


def draw_at_map(field, level_hpa, step_h, run,
                output_path, region_bbox, overlays=None):
    """Рисует карту АТ с оверлеями и таймкодом."""
    overlays = overlays or []
    lons, lats = field["lons"], field["lats"]

    level_info = AT_LEVELS[level_hpa]
    gh_min, gh_max = level_info["range"]
    step = level_info["step"]

    # Проекция
    if region_bbox == (-180, 180, -90, 90) or (region_bbox[1] - region_bbox[0] > 180):
        proj = ccrs.Robinson()
    else:
        proj = ccrs.PlateCarree()

    fig = plt.figure(figsize=(16, 10), dpi=100)
    ax = plt.axes(projection=proj)
    if isinstance(proj, ccrs.Robinson):
        ax.set_global()
    else:
        ax.set_extent(region_bbox, crs=ccrs.PlateCarree())

    # === Оверлей: температура заливкой ===
    if field["t"] is not None and ("t_850" in overlays or "t_500" in overlays):
        levels_t = np.arange(-60, 40, 5)
        cf = ax.contourf(lons, lats, field["t"], levels=levels_t,
                         cmap="RdYlBu_r", alpha=0.55,
                         transform=ccrs.PlateCarree(), extend="both",
                         zorder=1)
        cbar = fig.colorbar(cf, ax=ax, orientation="horizontal",
                            pad=0.04, shrink=0.55)
        cbar.set_label("Температура, °C", fontsize=10)

    # === Базовый слой: изогипсы АТ ===
    levels_gh = np.arange(gh_min, gh_max + step, step)
    cs = ax.contour(lons, lats, field["gh"], levels=levels_gh,
                    colors="black", linewidths=1.2,
                    transform=ccrs.PlateCarree(), zorder=4)
    ax.clabel(cs, inline=True, fontsize=8, fmt="%d")

    # === Оверлей: влажность изолиниями ===
    if field["rh"] is not None and "rh_700" in overlays:
        cs_rh = ax.contour(lons, lats, field["rh"],
                           levels=[40, 60, 80, 90, 95],
                           colors="blue", linewidths=0.8,
                           linestyles="dashed",
                           transform=ccrs.PlateCarree(), zorder=3)
        ax.clabel(cs_rh, inline=True, fontsize=7, fmt="%d%%")

    # === Оверлей: ветер барбами ===
    if field["u"] is not None and field["v"] is not None and "wind" in overlays:
        s = max(1, len(lons) // 50)
        ax.barbs(lons[::s], lats[::s],
                 field["u"][::s, ::s], field["v"][::s, ::s],
                 length=5, linewidth=0.4,
                 transform=ccrs.PlateCarree(), zorder=5)

    # === География ===
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5,
                   edgecolor="#555555", zorder=6)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3,
                   edgecolor="#888888", linestyle="--",
                   alpha=0.5, zorder=6)

    # === Заголовок ===
    run_str = run.strftime("%d.%m.%Y %H:%M UTC")
    title = f"АТ-{level_hpa} гПа · +{step_h} ч · GFS"
    ax.set_title(title, fontsize=15, pad=10, fontweight="bold")

    # === Таймкод в правом нижнем углу (valid time) ===
    valid_str = _fmt_valid_time(run, step_h)
    txt = ax.text(
        0.99, 0.01,
        f"Прогноз на: {valid_str}\nЗапуск: {run_str}",
        transform=ax.transAxes,
        fontsize=10,
        fontfamily="monospace",
        horizontalalignment="right",
        verticalalignment="bottom",
        bbox=dict(
            boxstyle="round,pad=0.4",
            facecolor="white",
            edgecolor="#333333",
            alpha=0.9,
        ),
        zorder=10,
    )

    plt.savefig(output_path, bbox_inches="tight", dpi=100,
                facecolor="white")
    plt.close(fig)


def _overlay_suffix(overlays):
    """Формирует суффикс имени файла из списка оверлеев."""
    if not overlays:
        return ""
    return "_" + "_".join(sorted(overlays))


def generate_at_maps(levels=(500,), steps=(0, 24),
                     regions=("nh",), overlays=None):
    """Генерирует карты для всех комбинаций level × step × region."""
    overlays = list(overlays or [])
    run = get_latest_gfs_run()
    stamp = run.strftime("%Y%m%d%H")
    year, month, day = stamp[:4], stamp[4:6], stamp[6:8]

    out_dir = os.path.join(ARCHIVE_DIR, year, month, day)
    os.makedirs(out_dir, exist_ok=True)

    suffix = _overlay_suffix(overlays)
    results = []

    for region_key in regions:
        bbox = REGIONS[region_key]["bbox"]
        for level in levels:
            for step in steps:
                try:
                    field = read_at_field(run, level, step, bbox,
                                          overlays=overlays)
                    fname = (f"gfs_{stamp}_{step:03d}"
                             f"_at{level}_{region_key}{suffix}.png")
                    out_path = os.path.join(out_dir, fname)
                    draw_at_map(field, level, step, run,
                                out_path, bbox, overlays=overlays)
                    results.append(out_path)
                    print(f"[synoptic_maps] ✓ {out_path}", flush=True)
                except Exception as e:
                    print(f"[synoptic_maps] ✗ level={level} "
                          f"step={step} region={region_key}: {e}",
                          flush=True)
                    traceback.print_exc()

    return results


def cleanup_old_archive():
    """Удаляет папки старше ARCHIVE_RETENTION_DAYS дней."""
    if not os.path.isdir(ARCHIVE_DIR):
        return 0

    cutoff = datetime.now() - timedelta(days=ARCHIVE_RETENTION_DAYS)
    removed = 0

    for year in os.listdir(ARCHIVE_DIR):
        ypath = os.path.join(ARCHIVE_DIR, year)
        if not (os.path.isdir(ypath) and year.isdigit()):
            continue
        for month in os.listdir(ypath):
            mpath = os.path.join(ypath, month)
            if not (os.path.isdir(mpath) and month.isdigit()):
                continue
            for day in os.listdir(mpath):
                dpath = os.path.join(mpath, day)
                if not (os.path.isdir(dpath) and day.isdigit()):
                    continue
                try:
                    d = datetime(int(year), int(month), int(day))
                except ValueError:
                    continue
                if d < cutoff:
                    try:
                        shutil.rmtree(dpath)
                        removed += 1
                        print(f"[synoptic_maps] Удалён архив: "
                              f"{year}/{month}/{day}", flush=True)
                    except Exception as e:
                        print(f"[synoptic_maps] Ошибка удаления: {e}",
                              flush=True)

    return removed


import shutil  # нужен для cleanup_old_archive
'''


# ================================================================
# НОВЫЙ ROUTES.PY
# ================================================================
ROUTES_PY = r'''# -*- coding: utf-8 -*-
"""Маршруты для раздела /synoptic-maps с архивом и оверлеями."""

import os
from flask import Blueprint, jsonify, render_template_string, request

from synoptic_maps.config import (
    AT_LEVELS, REGIONS, MODELS, STEPS, OVERLAY_LAYERS,
)
from synoptic_maps.generator import (
    generate_at_maps, ARCHIVE_DIR, cleanup_old_archive,
)
from ui import SYNOPTIC_MAPS_HTML


synoptic_maps_bp = Blueprint("synoptic_maps", __name__)


@synoptic_maps_bp.route("/synoptic-maps")
def synoptic_maps_page():
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
    """Список всех PNG-карт АТ из архива (свежие — первыми)."""
    if not os.path.isdir(ARCHIVE_DIR):
        return jsonify({"files": []})

    files = []
    for root, _, names in os.walk(ARCHIVE_DIR):
        for name in names:
            if name.endswith(".png") and "_at" in name:
                rel = os.path.relpath(os.path.join(root, name), ARCHIVE_DIR)
                files.append(rel.replace(os.sep, "/"))

    # Сортируем по имени (stamp в начале даёт естественный порядок)
    files.sort(reverse=True)
    return jsonify({"files": files})


@synoptic_maps_bp.route("/api/synoptic-maps/runs")
def api_at_runs():
    """
    Список прогонов (уникальных stamp), сгруппированных по дате.

    Возвращает:
        {"runs": [
            {"date": "2026-10-04", "stamp": "2026100400",
             "files": [...], "count": N},
            ...
        ]}
    """
    if not os.path.isdir(ARCHIVE_DIR):
        return jsonify({"runs": []})

    runs = {}
    for root, _, names in os.walk(ARCHIVE_DIR):
        for name in names:
            if not (name.endswith(".png") and "_at" in name):
                continue
            # Формат: gfs_YYYYMMDDHH_NNN_atXXX_REGION[_overlays].png
            parts = name.split("_")
            if len(parts) < 3 or len(parts[1]) < 10:
                continue
            stamp = parts[1]           # YYYYMMDDHH
            date_str = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}"
            rel = os.path.relpath(os.path.join(root, name), ARCHIVE_DIR)
            rel = rel.replace(os.sep, "/")

            if stamp not in runs:
                runs[stamp] = {
                    "date": date_str,
                    "stamp": stamp,
                    "files": [],
                }
            runs[stamp]["files"].append(rel)

    # Сортируем по stamp (свежие первыми)
    result = sorted(runs.values(),
                    key=lambda r: r["stamp"], reverse=True)
    for r in result:
        r["count"] = len(r["files"])
        r["files"].sort()
    return jsonify({"runs": result})


@synoptic_maps_bp.route("/api/synoptic-maps/generate", methods=["POST"])
def api_at_generate():
    """Ручная генерация карт АТ с оверлеями."""
    data = request.get_json() or {}
    levels = data.get("levels", [500])
    steps = data.get("steps", [0, 24])
    regions = data.get("regions", ["nh"])
    overlays = data.get("overlays", [])
    try:
        files = generate_at_maps(
            levels=tuple(levels),
            steps=tuple(steps),
            regions=tuple(regions),
            overlays=tuple(overlays),
        )
        # Заодно чистим старый архив
        cleanup_old_archive()
        return jsonify({"status": "ok", "files": files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@synoptic_maps_bp.route("/api/synoptic-maps/cleanup", methods=["POST"])
def api_at_cleanup():
    """Ручная очистка старого архива."""
    try:
        removed = cleanup_old_archive()
        return jsonify({"status": "ok", "removed": removed})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
'''


# ================================================================
# НОВЫЙ UI/SYNOPTIC_MAPS.PY (полная замена)
# ================================================================
SYNOPTIC_MAPS_HTML_PY = r'''# -*- coding: utf-8 -*-
"""Страница синоптических карт АТ (с оверлеями и архивом)."""

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
    position: relative;
  }
  .panel {
    padding: 16px 18px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
    max-height: 85vh;
    overflow-y: auto;
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
  .panel label:hover { color: var(--text-0); }
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
  .btn-row button:hover { opacity: 0.9; }
  #status {
    margin-top: 10px;
    font-size: 11px;
    color: var(--text-2);
    font-family: 'JetBrains Mono', monospace;
    min-height: 16px;
    word-break: break-word;
  }

  /* Архив */
  .archive-list {
    list-style: none;
    padding: 0;
    margin: 6px 0 0 0;
    max-height: 200px;
    overflow-y: auto;
  }
  .archive-list li {
    padding: 8px 10px;
    margin: 4px 0;
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: 8px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    justify-content: space-between;
    gap: 8px;
  }
  .archive-list li:hover {
    border-color: var(--border-hover);
    background: var(--bg-2);
  }
  .archive-list li.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.20),
                                       rgba(124,92,255,0.20));
    border-color: var(--accent);
  }
  .archive-list .stamp {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    color: var(--text-0);
  }
  .archive-list .meta {
    color: var(--text-2);
    font-size: 11px;
  }
</style>
</head>
<body>

""" + render_header("synoptic_maps") + """
<h1>🌐 Синоптические карты</h1>
<div class="sub">Абсолютная топография (АТ) · GFS · глобально · архив 3 дня</div>

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

    <h3>Доп. слои</h3>
    {% for key, ov in overlays.items() %}
      <label>
        <input type="checkbox" class="overlay-check" data-key="{{ key }}">
        {{ ov.name }}
      </label>
    {% endfor %}

    <div class="btn-row">
      <button onclick="updateMap()">Обновить</button>
      <button class="secondary" onclick="generateMaps()">⚙ Сгенерировать</button>
    </div>
    <div id="status">Готов к работе</div>

    <h3 style="margin-top:20px;">📂 Архив прогонов</h3>
    <ul class="archive-list" id="archive-list">
      <li style="justify-content:center;color:var(--text-2);">
        Загрузка...
      </li>
    </ul>
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
var currentLayer = null;

// --- Уровень АТ ---
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

// --- Выбранные оверлеи ---
function getSelectedOverlays() {
  var overlays = [];
  document.querySelectorAll('.overlay-check:checked').forEach(function(cb) {
    overlays.push(cb.dataset.key);
  });
  return overlays;
}

// --- Автозагрузка списка оверлеев при изменении ---
document.querySelectorAll('.overlay-check').forEach(function(cb) {
  cb.addEventListener('change', updateMap);
});

// --- Обновление карты ---
function updateMap() {
  var model = document.getElementById('model-select').value;
  var region = document.getElementById('region-select').value;
  var step = document.getElementById('step-select').value;
  var overlays = getSelectedOverlays();
  var status = document.getElementById('status');
  status.textContent = 'Поиск данных...';

  var overlaySuffix = overlays.length
    ? '_' + overlays.slice().sort().join('_')
    : '';

  fetch('/api/synoptic-maps/list')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var files = data.files || [];
      var step3 = String(step).padStart(3, '0');
      var re = new RegExp(
        model + '_\\\\d{10}_' + step3
        + '_at' + currentLevel + '_' + region
        + overlaySuffix + '\\\\.png$'
      );
      var match = files.find(function(f) { return re.test(f); });

      if (!match) {
        status.textContent = 'Нет данных. Нажмите «Сгенерировать» '
          + 'или выберите другой прогон в архиве.';
        if (currentLayer) {
          map.removeLayer(currentLayer);
          currentLayer = null;
        }
        return;
      }

      showFile(match);
      status.textContent = '✓ ' + match.split('/').pop();
    })
    .catch(function(e) { status.textContent = '✗ ' + e.message; });
}

function showFile(relPath) {
  var url = '/static/synoptic_maps/archive/' + relPath;

  // Определяем регион из имени файла
  var m = relPath.match(/_at\\d+_([a-z]+)/);
  var regionKey = m ? m[1] : 'nh';
  var bbox = REGION_BOUNDS[regionKey] || [-90, -180, 90, 180];

  if (currentLayer) map.removeLayer(currentLayer);
  currentLayer = L.imageOverlay(
    url,
    [[bbox[0], bbox[1]], [bbox[2], bbox[3]]],
    { opacity: 0.9 }
  ).addTo(map);

  map.fitBounds([[bbox[0], bbox[1]], [bbox[2], bbox[3]]]);
}

// --- Генерация ---
function generateMaps() {
  var model = document.getElementById('model-select').value;
  var region = document.getElementById('region-select').value;
  var step = parseInt(document.getElementById('step-select').value);
  var overlays = getSelectedOverlays();
  var status = document.getElementById('status');
  status.textContent = '⏳ Генерация... (1–3 мин, может дольше)';

  fetch('/api/synoptic-maps/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      levels: [currentLevel],
      steps: [step],
      regions: [region],
      overlays: overlays,
    }),
  })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.status === 'ok') {
        status.textContent = '✓ Готово: ' + data.files.length + ' файлов';
        loadArchive();
        setTimeout(updateMap, 1000);
      } else {
        status.textContent = '✗ ' + (data.message || '?');
      }
    })
    .catch(function(e) { status.textContent = '✗ ' + e.message; });
}

// --- Архив ---
function loadArchive() {
  fetch('/api/synoptic-maps/runs')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var list = document.getElementById('archive-list');
      var runs = data.runs || [];

      if (!runs.length) {
        list.innerHTML = '<li style="justify-content:center;'
          + 'color:var(--text-2);">Архив пуст</li>';
        return;
      }

      var html = '';
      runs.slice(0, 20).forEach(function(run) {
        var yyyy = run.stamp.substr(0, 4);
        var mm   = run.stamp.substr(4, 2);
        var dd   = run.stamp.substr(6, 2);
        var hh   = run.stamp.substr(8, 2);
        var label = dd + '.' + mm + ' ' + hh + ':00 UTC';

        html += '<li data-stamp="' + run.stamp + '">'
              + '<span class="stamp">' + label + '</span>'
              + '<span class="meta">' + run.count + ' файлов</span>'
              + '</li>';
      });
      list.innerHTML = html;

      // Клик по прогону — открыть его первую карту
      list.querySelectorAll('li[data-stamp]').forEach(function(li) {
        li.addEventListener('click', function() {
          list.querySelectorAll('li').forEach(function(x) {
            x.classList.remove('active');
          });
          li.classList.add('active');

          // Ищем подходящий файл с текущими фильтрами
          var stamp = li.dataset.stamp;
          fetch('/api/synoptic-maps/list')
            .then(function(r) { return r.json(); })
            .then(function(data) {
              var overlays = getSelectedOverlays();
              var suffix = overlays.length
                ? '_' + overlays.slice().sort().join('_')
                : '';
              var step = document.getElementById('step-select').value;
              var step3 = String(step).padStart(3, '0');
              var region = document.getElementById('region-select').value;
              var model = document.getElementById('model-select').value;
              var re = new RegExp(
                model + '_' + stamp + '_' + step3
                + '_at' + currentLevel + '_' + region
                + suffix + '\\\\.png$'
              );
              var match = (data.files || []).find(function(f) {
                return re.test(f);
              });
              if (match) {
                showFile(match);
                document.getElementById('status').textContent =
                  '✓ Архив: ' + match.split('/').pop();
              } else {
                // Иначе — просто первый файл этого прогона
                var first = (data.files || []).find(function(f) {
                  return f.indexOf('_' + stamp + '_') !== -1;
                });
                if (first) {
                  showFile(first);
                  document.getElementById('status').textContent =
                    'Архив: ' + first.split('/').pop();
                } else {
                  document.getElementById('status').textContent =
                    'В этом прогоне нет подходящих файлов';
                }
              }
            });
        });
      });
    })
    .catch(function(e) {
      document.getElementById('archive-list').innerHTML =
        '<li style="color:#ff5470;">Ошибка: ' + e.message + '</li>';
    });
}

// Автозагрузка
updateMap();
loadArchive();
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
    print("Оверлеи + архив + таймкод для «Синоптических карт»")
    print("=" * 70)

    if not (ROOT / "synoptic_maps").is_dir():
        print("✗ Папка synoptic_maps/ не найдена.")
        print("  Сначала запустите add_synoptic_maps.py")
        return 1

    # [1] generator.py
    print("\n[1] Замена synoptic_maps/generator.py")
    backup(ROOT / "synoptic_maps" / "generator.py")
    write_file(ROOT / "synoptic_maps" / "generator.py", GENERATOR_PY)

    # [2] routes.py
    print("\n[2] Замена synoptic_maps/routes.py")
    backup(ROOT / "synoptic_maps" / "routes.py")
    write_file(ROOT / "synoptic_maps" / "routes.py", ROUTES_PY)

    # [3] ui/synoptic_maps.py
    print("\n[3] Замена ui/synoptic_maps.py")
    backup(ROOT / "ui" / "synoptic_maps.py")
    write_file(ROOT / "ui" / "synoptic_maps.py", SYNOPTIC_MAPS_HTML_PY)

    # [4] scheduler.py — обновить задачу job_synoptic_maps
    print("\n[4] Патч scheduler.py (cleanup + overlays)")
    scheduler_py = ROOT / "scheduler.py"
    if scheduler_py.exists():
        backup(scheduler_py)
        text = scheduler_py.read_text(encoding="utf-8")
        # Добавляем cleanup в job_synoptic_maps
        new_job = (
            'def job_synoptic_maps():\n'
            '    """Генерация карт АТ + очистка старого архива."""\n'
            '    print("[scheduler] Генерация синоптических карт АТ...", flush=True)\n'
            '    try:\n'
            '        from synoptic_maps.generator import (\n'
            '            generate_at_maps, cleanup_old_archive,\n'
            '        )\n'
            '        files = generate_at_maps(\n'
            '            levels=(500, 850),\n'
            '            steps=(0, 24),\n'
            '            regions=("nh", "europe"),\n'
            '            overlays=("t_850",),\n'
            '        )\n'
            '        removed = cleanup_old_archive()\n'
            '        print(f"[scheduler] Готово: {len(files)} карт АТ, "\n'
            '              f"удалено старых: {removed}", flush=True)\n'
            '    except Exception as e:\n'
            '        print(f"[scheduler] Ошибка синоптических карт: {e}", flush=True)\n'
        )
        # Паттерн: заменить старую job_synoptic_maps
        pattern = r'def job_synoptic_maps\(\):.*?(?=\n\ndef |\n\n# |\Z)'
        new_text, n = re.subn(pattern, new_job.rstrip() + "\n",
                              text, count=1, flags=re.DOTALL)
        if n == 0:
            print("  ⚠ не нашёл job_synoptic_maps в scheduler.py — пропускаю")
        else:
            scheduler_py.write_text(new_text, encoding="utf-8")
            print("  ✓ job_synoptic_maps обновлён (overlays + cleanup)")
    else:
        print("  ⚠ scheduler.py не найден")

    # [5] Dockerfile — добавить переменную окружения
    print("\n[5] Патч Dockerfile (HERBIE_SAVE_DIR)")
    dockerfile = ROOT / "Dockerfile"
    if dockerfile.exists():
        backup(dockerfile)
        text = dockerfile.read_text(encoding="utf-8")
        if "HERBIE_SAVE_DIR" not in text:
            # Добавляем переменную окружения
            text = text.rstrip() + (
                "\n\n# Herbie cache (для GRIB-файлов)\n"
                'ENV HERBIE_SAVE_DIR=/tmp/herbie_cache\n'
            )
            dockerfile.write_text(text, encoding="utf-8")
            print("  ✓ HERBIE_SAVE_DIR добавлен в Dockerfile")
        else:
            print("  ✓ HERBIE_SAVE_DIR уже присутствует")
    else:
        print("  ⚠ Dockerfile не найден")

    # [6] Проверка синтаксиса
    print("\n[6] Проверка синтаксиса")
    files_to_check = [
        ROOT / "synoptic_maps" / "generator.py",
        ROOT / "synoptic_maps" / "routes.py",
        ROOT / "ui" / "synoptic_maps.py",
        ROOT / "scheduler.py",
    ]
    all_ok = True
    for f in files_to_check:
        if f.exists() and not check_syntax(f):
            all_ok = False

    # Итог
    print()
    print("=" * 70)
    if all_ok:
        print("✓ ГОТОВО")
        print("=" * 70)
        print()
        print("Что сделано:")
        print("  ✓ Оверлеи (T, ветер, RH) — backend + frontend")
        print("  ✓ Архив карт за 3 дня + UI со списком прогонов")
        print("  ✓ Таймкод (valid time) в правом нижнем углу")
        print("  ✓ Приоритет NOMADS, timeout=180, retry×2, remove_grib=False")
        print("  ✓ HERBIE_SAVE_DIR в Dockerfile")
        print()
        print("Что дальше:")
        print("  1. Перезапустите сервер:")
        print("       python server.py")
        print()
        print("  2. Откройте: http://localhost:5000/synoptic-maps")
        print()
        print("  3. Поставьте галочки доп. слоёв (например, «Температура 850 гПа»)")
        print("     и нажмите «Сгенерировать»")
        print()
        print("  4. Смотрите архив прогонов внизу панели")
        print()
        print("Откат:")
        print("  Восстановить файлы из .backup_overlays/")
    else:
        print("✗ БЫЛИ ОШИБКИ")
        print("=" * 70)
        print("Проверьте вывод выше. Откат:")
        print("  Восстановить файлы из .backup_overlays/")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())