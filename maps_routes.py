# -*- coding: utf-8 -*-
"""
Маршруты для страницы /maps и API генерации карт.
Включая API для архива.
"""

import os

from flask import Blueprint, jsonify, request, render_template_string

from maps_generator import (
    generate_all_layers, MAPS_DIR, ARCHIVE_DIR, get_meta,
)
from templates import MAPS_HTML


maps_bp = Blueprint("maps", __name__)


@maps_bp.route("/maps")
def maps_page():
    """Интерактивная карта с чекбоксами слоёв и поиском региона."""
    meta = get_meta()
    return render_template_string(MAPS_HTML, meta=meta)


@maps_bp.route("/api/maps-meta")
def api_maps_meta():
    return jsonify(get_meta())


@maps_bp.route("/api/maps-list")
def api_maps_list():
    """Список всех PNG-слоёв в корне static/maps/ (последний прогон)."""
    if not os.path.isdir(MAPS_DIR):
        return jsonify({"files": []})
    files = [f for f in os.listdir(MAPS_DIR)
             if f.endswith(".png")]
    return jsonify({"files": sorted(files)})


@maps_bp.route("/api/maps-archive")
def api_maps_archive():
    """
    Список архивных прогонов.

    Возвращает:
    {
      "runs": [
        {
          "date": "2026-09-22",
          "stamp": "icon-eu_2026092206",
          "files": ["icon-eu_2026092206_012_t2m.png", ...]
        }, ...
      ]
    }
    """
    if not os.path.isdir(ARCHIVE_DIR):
        return jsonify({"runs": []})

    runs = []
    for year in sorted(os.listdir(ARCHIVE_DIR), reverse=True):
        year_dir = os.path.join(ARCHIVE_DIR, year)
        if not os.path.isdir(year_dir):
            continue
        for month in sorted(os.listdir(year_dir), reverse=True):
            month_dir = os.path.join(year_dir, month)
            if not os.path.isdir(month_dir):
                continue
            for day in sorted(os.listdir(month_dir), reverse=True):
                day_dir = os.path.join(month_dir, day)
                if not os.path.isdir(day_dir):
                    continue

                files = [f for f in os.listdir(day_dir) if f.endswith(".png")]

                # Группируем по model_YYYYMMDDHH
                stamps = {}
                for f in files:
                    parts = f.split("_")
                    if len(parts) >= 2:
                        key = parts[0] + "_" + parts[1]
                        stamps.setdefault(key, []).append(f)

                for key, files_list in sorted(stamps.items(), reverse=True):
                    runs.append({
                        "date": f"{year}-{month}-{day}",
                        "stamp": key,
                        "files": sorted(files_list),
                    })

    runs.sort(key=lambda x: x["stamp"], reverse=True)
    return jsonify({"runs": runs})


@maps_bp.route("/api/maps-archive-files")
def api_maps_archive_files():
    """
    Возвращает список файлов для конкретного прогона.

    Query: ?stamp=icon-eu_2026092206
    """
    stamp = request.args.get("stamp", "").strip()
    if not stamp or "_" not in stamp:
        return jsonify({"files": [], "error": "stamp required"})

    # Извлекаем дату из stamp: model_YYYYMMDDHH
    parts = stamp.split("_")
    if len(parts) < 2 or len(parts[1]) < 10:
        return jsonify({"files": [], "error": "bad stamp"})

    model = parts[0]
    date_str = parts[1]  # YYYYMMDDHH
    year, month, day = date_str[:4], date_str[4:6], date_str[6:8]

    archive_dir = os.path.join(ARCHIVE_DIR, year, month, day)
    if not os.path.isdir(archive_dir):
        return jsonify({"files": [], "error": "no archive"})

    # Фильтруем по префиксу stamp
    prefix = f"{model}_{date_str}_"
    files = [f for f in os.listdir(archive_dir)
             if f.startswith(prefix) and f.endswith(".png")]

    return jsonify({
        "files": sorted(files),
        "base_url": f"/static/maps/archive/{year}/{month}/{day}/",
    })

# ==================================================================
# АРХИВ ПРОГОНОВ — СТРАНИЦА
# ==================================================================
@maps_bp.route("/archive")
def archive_page():
    """Отдельная страница со списком архивных прогонов и картой."""
    from templates import ARCHIVE_HTML
    meta = get_meta()
    return render_template_string(ARCHIVE_HTML, meta=meta)


@maps_bp.route("/archive/<stamp>")
def archive_run(stamp):
    """Конкретный архивный прогон."""
    from templates import ARCHIVE_HTML
    meta = get_meta()
    return render_template_string(ARCHIVE_HTML, meta=meta)


# ==================================================================
# СКАЧИВАНИЕ ZIP-ОМ
# ==================================================================
@maps_bp.route("/api/maps-archive-zip/<stamp>")
def api_archive_zip(stamp):
    """Упаковка всех PNG одного прогона в ZIP."""
    import io
    import zipfile
    from flask import send_file

    parts = stamp.split("_")
    if len(parts) < 2 or len(parts[1]) < 10:
        return jsonify({"error": "bad stamp"}), 400

    model = parts[0]
    date_str = parts[1]
    year, month, day = date_str[:4], date_str[4:6], date_str[6:8]

    archive_dir = os.path.join(ARCHIVE_DIR, year, month, day)
    if not os.path.isdir(archive_dir):
        return jsonify({"error": "no archive"}), 404

    prefix = f"{model}_{date_str}_"
    files = [f for f in os.listdir(archive_dir)
             if f.startswith(prefix) and f.endswith(".png")]

    if not files:
        return jsonify({"error": "no files"}), 404

    # Собираем ZIP в памяти
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in sorted(files):
            fpath = os.path.join(archive_dir, fname)
            zf.write(fpath, arcname=fname)
    buf.seek(0)

    return send_file(
        buf,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{stamp}.zip",
    )

@maps_bp.route("/api/update-maps", methods=["POST"])
def api_update_maps():
    """Ручной запуск генерации карт."""
    data = request.get_json() or {}
    models = data.get("models", ["icon-eu"])
    steps = data.get("steps", [12])
    fields = data.get("fields", ["t_2m", "pmsl", "u_10m", "v_10m"])

    try:
        files = generate_all_layers(
            models=models, steps=steps, fields=fields,
        )
        return jsonify({"status": "ok", "files": files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500