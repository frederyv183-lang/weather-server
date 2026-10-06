# synoptic_maps/storage.py
# Хранилище сгенерированных карт: локально static/, на Render — /tmp.

import os


def get_archive_dir():
    """
    Папка с архивом карт.
    - Render (RENDER=true) или задан STORAGE_DIR — /tmp/synoptic_maps/archive
    - Локально — static/synoptic_maps/archive
    """
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if os.environ.get("RENDER") == "true" or os.environ.get("STORAGE_DIR"):
        storage = os.environ.get("STORAGE_DIR", "/tmp/synoptic_maps")
        return os.path.join(storage, "archive")

    return os.path.join(base, "static", "synoptic_maps", "archive")


def get_public_url(filename):
    """URL для отдачи файла браузеру."""
    return "/synoptic-maps-file/" + filename
