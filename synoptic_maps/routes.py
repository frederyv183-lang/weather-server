# -*- coding: utf-8 -*-
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
