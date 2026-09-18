# -*- coding: utf-8 -*-
"""
TTL-кэш в памяти.
"""

import time
import threading


class TTLCache:
    def __init__(self, ttl_seconds=600):
        self.ttl = ttl_seconds
        self._data = {}
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            item = self._data.get(key)
            if not item:
                return None
            value, expires = item
            if time.time() > expires:
                self._data.pop(key, None)
                return None
            return value

    def set(self, key, value):
        with self._lock:
            self._data[key] = (value, time.time() + self.ttl)

    def clear(self):
        with self._lock:
            self._data.clear()


# Глобальные экземпляры кэшей
_forecast_cache = TTLCache(ttl_seconds=600)
_verify_cache = TTLCache(ttl_seconds=3600)
_current_cache = TTLCache(ttl_seconds=300)