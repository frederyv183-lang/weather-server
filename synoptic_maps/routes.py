# -*- coding: utf-8 -*-
"""Маршруты для раздела /synoptic-maps (v5)."""

import os
from flask import Blueprint, jsonify, render_template_string, request

from synoptic_maps.config import (
    AT_LEVELS, REGIONS, MODELS, STEPS, OVERLAY_LAYERS, OT,
)
from synoptic_maps.generator import (
    generate_maps, ARCHIVE_DIR, cleanup_old_archive,
)
from ui import SYNOPTIC_MAPS_HTML


synoptic_maps_bp = Blueprint("synoptic_maps", __name__)


@synoptic_maps_bp.route("/synoptic-maps")
def synoptic_maps_page():
    levels_sorted = dict(sorted(
        AT_LEVELS.items(),
        key=lambda kv: kv[1].get("sort_order", 999),
    ))
    return render_template_string(
        SYNOPTIC_MAPS_HTML,
        levels=levels_sorted,
        regions=REGIONS,
        models=MODELS,
        steps=STEPS,
        overlays=OVERLAY_LAYERS,
        ot=OT,
    )


@synoptic_maps_bp.route("/api/synoptic-maps/list")
def api_at_list():
    if not os.path.isdir(ARCHIVE_DIR):
        return jsonify({"files": []})
    files = []
    for root, _, names in os.walk(ARCHIVE_DIR):
        for name in names:
            if name.endswith(".png"):
                rel = os.path.relpath(os.path.join(root, name), ARCHIVE_DIR)
                files.append(rel.replace(os.sep, "/"))
    files.sort(reverse=True)
    return jsonify({"files": files})


@synoptic_maps_bp.route("/api/synoptic-maps/runs")
def api_at_runs():
    if not os.path.isdir(ARCHIVE_DIR):
        return jsonify({"runs": []})
    runs = {}
    for root, _, names in os.walk(ARCHIVE_DIR):
        for name in names:
            if not name.endswith(".png"):
                continue
            parts = name.split("_")
            if len(parts) < 3 or len(parts[1]) < 10:
                continue
            stamp = parts[1]
            date_str = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}"
            rel = os.path.relpath(os.path.join(root, name), ARCHIVE_DIR)
            rel = rel.replace(os.sep, "/")
            if stamp not in runs:
                runs[stamp] = {"date": date_str, "stamp": stamp, "files": []}
            runs[stamp]["files"].append(rel)
    result = sorted(runs.values(), key=lambda r: r["stamp"], reverse=True)
    for r in result:
        r["count"] = len(r["files"])
    return jsonify({"runs": result})


@synoptic_maps_bp.route("/api/synoptic-maps/generate", methods=["POST"])
def api_at_generate():
    data = request.get_json() or {}
    levels = data.get("levels")
    steps = data.get("steps", [0, 12, 24, 48, 72])
    regions = data.get("regions", ["etr"])
    show_h = data.get("show_isohypse", True)
    show_t = data.get("show_isotherm", True)
    show_w = data.get("show_isotach", True)
    try:
        files = generate_maps(
            levels=levels, steps=tuple(steps), regions=tuple(regions),
            show_isohypse=show_h, show_isotherm=show_t,
            show_isotach=show_w,
            include_ot=data.get("include_ot", True),
        )
        cleanup_old_archive()
        return jsonify({"status": "ok", "files": files,
                        "count": len(files)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@synoptic_maps_bp.route("/api/synoptic-maps/find", methods=["POST"])
def api_at_find():
    """Находит последний подходящий PNG по фильтрам."""
    data = request.get_json() or {}
    level = data.get("level")
    step = data.get("step")
    region = data.get("region", "etr")
    stamp_filter = data.get("stamp")
    show_h = data.get("show_isohypse", True)
    show_t = data.get("show_isotherm", True)
    show_w = data.get("show_isotach", True)

    def suffix(h, t, w):
        parts = []
        if h: parts.append("h")
        if t: parts.append("t")
        if w: parts.append("w")
        return ("_" + "".join(parts)) if parts else "_none"

    suf = suffix(show_h, show_t, show_w)
    step3 = str(step).zfill(3)

    if str(level).startswith("ot_"):
        level_token = str(level)
    else:
        level_token = f"at{level}"

    if not os.path.isdir(ARCHIVE_DIR):
        return jsonify({"file": None})

    matches = []
    for root, _, names in os.walk(ARCHIVE_DIR):
        for name in names:
            if not name.startswith("gfs_"):
                continue
            if not name.endswith(f"_{step3}_{level_token}_{region}{suf}.png"):
                continue
            if stamp_filter:
                parts = name.split("_")
                if len(parts) > 1 and parts[1] != stamp_filter:
                    continue
            rel = os.path.relpath(
                os.path.join(root, name), ARCHIVE_DIR
            ).replace(os.sep, "/")
            matches.append(rel)
    matches.sort(reverse=True)
    return jsonify({"file": matches[0] if matches else None})