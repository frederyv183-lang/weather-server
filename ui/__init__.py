# -*- coding: utf-8 -*-
"""
Пакет UI: реэкспорт всех шаблонов и вспомогательных функций.

Использование:
    from ui import INDEX_HTML, TABLE_TEMPLATE, render_header
"""

from ui.styles import (
    BASE_STYLE,
    COMMON_JS,
    render_top_controls,
    render_header,
    render_legend,
    render_biblio_ref,
)

from ui.hubs import (
    FORECAST_HUB_HTML,
    ANALYSIS_HUB_HTML,
    THEORY_HUB_HTML,
    INDEX_HTML,
    ABOUT_HTML,
)

from ui.forecast import (
    CHART_HTML,
    MODEL_HTML,
    TABLE_TEMPLATE,
    TEXT_TEMPLATE,
    SEARCH_HTML,
    POINT_TEMPLATE,
)

from ui.analysis import (
    VERIFY_HTML,
    VERIFY_HISTORY_HTML,
    ANALYZE_HTML,
    COMPARE_MATRICES_HTML,
    COMPARE_HTML,
    ALT_VERIFY_HTML,
    COMPARE_POINT_HTML,
)

from ui.synoptic import (
    TROPOPAUSE_HTML,
    AVIATION_HTML,
    SYNOPTIC_HTML,
)

from ui.climate import (
    CLIMATE_HTML,
)

from ui.maps import (
    MAP_HTML,
    ARCHIVE_HTML,
    MAPS_HTML,
)

from ui.theory import (
    TEACHING_HTML,
    THEORY_METHODS_HTML,
    THEORY_MATRICES_HTML,
    THEORY_INDICES_HTML,
)

from ui.bibliography import (
    BIBLIOGRAPHY_HTML,
)

from ui.tests import (
    TESTS_HTML,
)


__all__ = [
    "BASE_STYLE",
    "COMMON_JS",
    "render_top_controls",
    "render_header",
    "render_legend",
    "render_biblio_ref",
    "FORECAST_HUB_HTML",
    "ANALYSIS_HUB_HTML",
    "THEORY_HUB_HTML",
    "INDEX_HTML",
    "ABOUT_HTML",
    "CHART_HTML",
    "MODEL_HTML",
    "TABLE_TEMPLATE",
    "TEXT_TEMPLATE",
    "SEARCH_HTML",
    "POINT_TEMPLATE",
    "VERIFY_HTML",
    "VERIFY_HISTORY_HTML",
    "ANALYZE_HTML",
    "COMPARE_MATRICES_HTML",
    "COMPARE_HTML",
    "ALT_VERIFY_HTML",
    "COMPARE_POINT_HTML",
    "TROPOPAUSE_HTML",
    "AVIATION_HTML",
    "SYNOPTIC_HTML",
    "CLIMATE_HTML",
    "MAP_HTML",
    "ARCHIVE_HTML",
    "MAPS_HTML",
    "TEACHING_HTML",
    "THEORY_METHODS_HTML",
    "THEORY_MATRICES_HTML",
    "THEORY_INDICES_HTML",
    "BIBLIOGRAPHY_HTML",
    "TESTS_HTML",
]
