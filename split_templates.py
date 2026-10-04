# -*- coding: utf-8 -*-
"""
Автоматически разрезает templates.py на пакет ui/.

Запуск:
    python split_templates.py

Что делает:
    1. Читает templates.py.
    2. Через AST находит все верхнеуровневые определения (константы + функции).
    3. Раскладывает их по файлам пакета ui/ согласно карте DISTRIBUTION.
    4. Создаёт ui/__init__.py с реэкспортом.
    5. Делает бэкап templates.py.backup_before_split.
    6. Проверяет синтаксис каждого нового файла и импорт ui.

После проверки:
    - Убедитесь, что python -c "import server" работает.
    - Удалите templates.py вручную или через git rm.
"""

import ast
import os
import shutil
import sys
import io

# ----------------------------------------------------------------
# UTF-8 вывод в Windows-консоли
# ----------------------------------------------------------------
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8",
                                  errors="replace")


SOURCE = "templates.py"
BACKUP = "templates.py.backup_before_split"
UI_DIR = "ui"

# ================================================================
# КАРТА: какое имя -> в какой файл пакета ui/
# ================================================================
# Всё, что не указано, попадёт в "misc.py" (маловероятно)
DISTRIBUTION = {
    # -------- ui/styles.py --------
    "BASE_STYLE":             "styles",
    "COMMON_JS":              "styles",
    "render_top_controls":    "styles",
    "render_header":          "styles",
    "render_legend":          "styles",
    "render_biblio_ref":      "styles",

    # -------- ui/hubs.py --------
    "FORECAST_HUB_HTML":      "hubs",
    "ANALYSIS_HUB_HTML":      "hubs",
    "THEORY_HUB_HTML":        "hubs",
    "INDEX_HTML":             "hubs",
    "ABOUT_HTML":             "hubs",

    # -------- ui/forecast.py --------
    "TABLE_TEMPLATE":         "forecast",
    "TEXT_TEMPLATE":          "forecast",
    "CHART_HTML":             "forecast",
    "MODEL_HTML":             "forecast",
    "SEARCH_HTML":            "forecast",
    "POINT_TEMPLATE":         "forecast",

    # -------- ui/analysis.py --------
    "VERIFY_HTML":            "analysis",
    "VERIFY_HISTORY_HTML":    "analysis",
    "ANALYZE_HTML":           "analysis",
    "ALT_VERIFY_HTML":        "analysis",
    "COMPARE_MATRICES_HTML":  "analysis",
    "COMPARE_HTML":           "analysis",
    "COMPARE_POINT_HTML":     "analysis",

    # -------- ui/synoptic.py --------
    "SYNOPTIC_HTML":          "synoptic",
    "AVIATION_HTML":          "synoptic",
    "TROPOPAUSE_HTML":        "synoptic",

    # -------- ui/climate.py --------
    "CLIMATE_HTML":           "climate",

    # -------- ui/maps.py --------
    "MAP_HTML":               "maps",
    "MAPS_HTML":              "maps",
    "ARCHIVE_HTML":           "maps",

    # -------- ui/theory.py --------
    "TEACHING_HTML":          "theory",
    "THEORY_METHODS_HTML":    "theory",
    "THEORY_MATRICES_HTML":   "theory",
    "THEORY_INDICES_HTML":    "theory",

    # -------- ui/bibliography.py --------
    "BIBLIOGRAPHY_HTML":      "bibliography",

    # -------- ui/tests.py --------
    "TESTS_HTML":             "tests",
}

# Модули, которые импортируют из styles:
STYLE_IMPORTS = {
    "hubs":         ["BASE_STYLE", "COMMON_JS", "render_header", "render_legend"],
    "forecast":     ["BASE_STYLE", "COMMON_JS", "render_header", "render_legend"],
    "analysis":     ["BASE_STYLE", "COMMON_JS", "render_header", "render_legend",
                     "render_biblio_ref"],
    "synoptic":     ["BASE_STYLE", "COMMON_JS", "render_header", "render_legend",
                     "render_biblio_ref"],
    "climate":      ["BASE_STYLE", "COMMON_JS", "render_header", "render_legend",
                     "render_biblio_ref"],
    "maps":         ["BASE_STYLE", "COMMON_JS", "render_header"],
    "theory":       ["BASE_STYLE", "COMMON_JS", "render_header", "render_legend",
                     "render_biblio_ref"],
    "bibliography": ["BASE_STYLE", "COMMON_JS", "render_header", "render_legend"],
    "tests":        ["BASE_STYLE", "COMMON_JS", "render_header"],
}

# Русские описания для docstring каждого модуля
MODULE_DESCR = {
    "styles":       "Базовые стили, общий JS, вспомогательные функции рендера.",
    "hubs":         "Хабы: главная, прогноз, анализ, теория, О проекте.",
    "forecast":     "Страницы прогнозов: таблица, текст, график, модель, поиск.",
    "analysis":     "Страницы анализа и верификации: verify, analyze, matrices.",
    "synoptic":     "Синоптика, авиация, тропопауза.",
    "climate":      "Климатические индексы (ENSO/SSW/PV).",
    "maps":         "Карты погоды: интерактивная карта и архив.",
    "theory":       "Теория: методы, матрицы, индексы, учебные примеры.",
    "bibliography": "Библиография.",
    "tests":        "Страница тестов.",
}

# Импорты, которые должны быть в шапке каждого модуля
MODULE_HEADER_IMPORTS = {
    "styles": [
        "from core.dictionaries import (",
        "    CODE_TO_TEXT, WEATHER_ICONS, LEGEND_ITEMS, BIBLIOGRAPHY_ITEMS,",
        ")",
        "from core.config import DEFAULT_LOCATION",
    ],
    "hubs":         [],
    "forecast":     [],
    "analysis":     [],
    "synoptic":     [],
    "climate":      [],
    "maps":         [],
    "theory":       [],
    "bibliography": [],
    "tests":        [],
}


# ================================================================
# ШАГ 1. Парсим исходник через AST
# ================================================================
def parse_source(path):
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=path)
    lines = source.splitlines(keepends=True)
    return source, tree, lines


def find_top_definitions(tree, lines):
    """
    Возвращает список (name, kind, start_line, end_line, body_text),
    где kind = 'const' | 'func' | 'import' | 'docstring' | 'other'.
    Строки 0-based (start включительно, end исключительно).
    """
    defs = []
    for node in tree.body:
        kind = None
        name = None

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            kind = "import"
            name = f"__import_{node.lineno}__"

        elif isinstance(node, ast.FunctionDef) and node.name.startswith("render_"):
            kind = "func"
            name = node.name

        elif isinstance(node, ast.Assign):
            # NAME = ...
            if (len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)):
                name = node.targets[0].id
                kind = "const"

        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str) and defs == []:
            # docstring модуля
            kind = "docstring"
            name = "__docstring__"

        if kind is None:
            continue

        start = node.lineno - 1  # 0-based
        # Включаем декораторы
        if getattr(node, "decorator_list", None):
            start = min(d.lineno for d in node.decorator_list) - 1

        # end_lineno включает последнюю строку — берём +1
        end = node.end_lineno  # уже 1-based «последняя строка», end = end (0-based exclusive)

        body = "".join(lines[start:end])
        defs.append({
            "name": name,
            "kind": kind,
            "start": start,
            "end": end,
            "body": body,
        })

    return defs


# ================================================================
# ШАГ 2. Раскладываем по модулям
# ================================================================
def distribute(defs):
    """
    Возвращает dict: module_name -> list of def dicts.
    Плюс отдельно список импортов и docstring.
    """
    modules = {}
    imports = []
    docstring = None

    for d in defs:
        if d["kind"] == "import":
            imports.append(d)
            continue
        if d["kind"] == "docstring":
            docstring = d
            continue

        module = DISTRIBUTION.get(d["name"])
        if module is None:
            print(f"  [!] Не знаю, куда положить {d['name']!r} — кладу в misc")
            module = "misc"

        modules.setdefault(module, []).append(d)

    return modules, imports, docstring


# ================================================================
# ШАГ 3. Записываем модули
# ================================================================
def write_module(module_name, definitions):
    path = os.path.join(UI_DIR, f"{module_name}.py")

    header = [
        "# -*- coding: utf-8 -*-",
        f'"""{MODULE_DESCR.get(module_name, "Модуль UI.")}"""',
        "",
    ]

    # Импорты
    header_imports = MODULE_HEADER_IMPORTS.get(module_name, [])
    for line in header_imports:
        header.append(line)
    if header_imports:
        header.append("")

    # Если это не styles — импортируем нужные имена из styles
    if module_name != "styles":
        style_names = STYLE_IMPORTS.get(module_name, [])
        if style_names:
            header.append("from ui.styles import (")
            for name in style_names:
                header.append(f"    {name},")
            header.append(")")
            header.append("")

    # Собираем тело
    body_parts = []
    for d in definitions:
        body_parts.append(d["body"])
        if not d["body"].endswith("\n"):
            body_parts.append("\n")
        body_parts.append("\n\n")  # две пустые строки между определениями

    content = "\n".join(header) + "\n".join(body_parts).rstrip() + "\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    # Проверка синтаксиса
    try:
        compile(content, path, "exec")
        print(f"  ✓ {path}  ({len(definitions)} определений, "
              f"{len(content)} символов)")
    except SyntaxError as e:
        print(f"  ✗ {path}: SyntaxError: {e}")
        return False

    return True


# ================================================================
# ШАГ 4. __init__.py
# ================================================================
def write_init(modules):
    """Генерирует ui/__init__.py с реэкспортом всего."""

    # Порядок важен: styles первым
    order = [
        "styles",
        "hubs",
        "forecast",
        "analysis",
        "synoptic",
        "climate",
        "maps",
        "theory",
        "bibliography",
        "tests",
    ]
    # добавляем то, что осталось
    for m in modules:
        if m not in order:
            order.append(m)

    lines = [
        "# -*- coding: utf-8 -*-",
        '"""',
        "Пакет UI: реэкспорт всех шаблонов и вспомогательных функций.",
        "",
        "Использование:",
        "    from ui import INDEX_HTML, TABLE_TEMPLATE, render_header",
        '"""',
        "",
    ]

    all_names = []

    for module in order:
        defs = modules.get(module, [])
        if not defs:
            continue
        lines.append(f"from ui.{module} import (")
        for d in defs:
            lines.append(f"    {d['name']},")
            all_names.append(d["name"])
        lines.append(")")
        lines.append("")

    lines.append("")
    lines.append("__all__ = [")
    for name in all_names:
        lines.append(f'    "{name}",')
    lines.append("]")
    lines.append("")

    content = "\n".join(lines)
    path = os.path.join(UI_DIR, "__init__.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        compile(content, path, "exec")
        print(f"  ✓ {path}  ({len(all_names)} имён реэкспортировано)")
    except SyntaxError as e:
        print(f"  ✗ {path}: SyntaxError: {e}")
        return False

    return True


# ================================================================
# ШАГ 5. Проверка импорта
# ================================================================
def check_import():
    print()
    print("[5] Проверка импорта ui ...")
    try:
        # Свежий импорт
        for mod in list(sys.modules.keys()):
            if mod == "ui" or mod.startswith("ui."):
                del sys.modules[mod]

        sys.path.insert(0, os.getcwd())
        import ui

        # Обязательные имена
        required = [
            "BASE_STYLE", "COMMON_JS",
            "render_top_controls", "render_header",
            "render_legend", "render_biblio_ref",
            "INDEX_HTML", "FORECAST_HUB_HTML", "ANALYSIS_HUB_HTML",
            "THEORY_HUB_HTML", "ABOUT_HTML",
            "TABLE_TEMPLATE", "TEXT_TEMPLATE", "CHART_HTML",
            "MODEL_HTML", "SEARCH_HTML", "POINT_TEMPLATE",
            "VERIFY_HTML", "VERIFY_HISTORY_HTML", "ANALYZE_HTML",
            "ALT_VERIFY_HTML", "COMPARE_MATRICES_HTML",
            "COMPARE_HTML", "COMPARE_POINT_HTML",
            "SYNOPTIC_HTML", "AVIATION_HTML", "TROPOPAUSE_HTML",
            "CLIMATE_HTML",
            "MAP_HTML", "MAPS_HTML", "ARCHIVE_HTML",
            "TEACHING_HTML", "THEORY_METHODS_HTML",
            "THEORY_MATRICES_HTML", "THEORY_INDICES_HTML",
            "BIBLIOGRAPHY_HTML", "TESTS_HTML",
        ]
        missing = [n for n in required if not hasattr(ui, n)]
        if missing:
            print(f"  ✗ Отсутствуют имена: {missing}")
            return False

        print(f"  ✓ Импорт ui успешен. Все {len(required)} имён на месте.")
        # Показать размеры нескольких ключевых
        for name in ["INDEX_HTML", "TABLE_TEMPLATE", "MAPS_HTML"]:
            val = getattr(ui, name)
            print(f"    {name}: {len(val)} символов")

        return True
    except Exception as e:
        import traceback
        print(f"  ✗ Ошибка импорта: {e}")
        traceback.print_exc()
        return False


# ================================================================
# MAIN
# ================================================================
def main():
    print("=" * 70)
    print("Разрезание templates.py на пакет ui/")
    print("=" * 70)

    if not os.path.exists(SOURCE):
        print(f"✗ Файл {SOURCE} не найден. Запустите скрипт из корня проекта.")
        return 1

    # 1. Бэкап
    if not os.path.exists(BACKUP):
        shutil.copy(SOURCE, BACKUP)
        print(f"[1] Бэкап: {BACKUP}")
    else:
        print(f"[1] Бэкап уже существует: {BACKUP}")

    # 2. Парсинг
    print(f"[2] Парсинг {SOURCE} ...")
    source, tree, lines = parse_source(SOURCE)
    defs = find_top_definitions(tree, lines)
    print(f"    Найдено верхнеуровневых определений: {len(defs)}")

    consts = [d for d in defs if d["kind"] == "const"]
    funcs  = [d for d in defs if d["kind"] == "func"]
    imps   = [d for d in defs if d["kind"] == "import"]
    docs   = [d for d in defs if d["kind"] == "docstring"]
    print(f"    Констант: {len(consts)}, функций: {len(funcs)}, "
          f"импортов: {len(imps)}, docstring: {len(docs)}")

    # 3. Раскладка
    print(f"[3] Раскладка по модулям ...")
    modules, imports, docstring = distribute(defs)
    for m in sorted(modules.keys()):
        print(f"    ui/{m}.py: {len(modules[m])} определений")

    # 4. Создание папки ui/
    if not os.path.isdir(UI_DIR):
        os.makedirs(UI_DIR)
        print(f"[4] Создана папка {UI_DIR}/")
    else:
        print(f"[4] Папка {UI_DIR}/ уже существует")

    # 5. Запись модулей
    print(f"[5] Запись модулей ...")
    ok = True
    for module_name in sorted(modules.keys()):
        # styles всегда первым
        pass
    # сортируем так, чтобы styles был первым
    order = ["styles"] + [m for m in sorted(modules.keys()) if m != "styles"]
    for module_name in order:
        if module_name not in modules:
            continue
        if not write_module(module_name, modules[module_name]):
            ok = False

    # 6. __init__.py
    print(f"[6] Создание ui/__init__.py ...")
    if not write_init(modules):
        ok = False

    if not ok:
        print()
        print("✗ Были ошибки при записи модулей.")
        print(f"  Откат: удалите папку {UI_DIR}/ и восстановите {SOURCE} из {BACKUP}")
        return 1

    # 7. Проверка импорта
    print()
    ok = check_import()

    print()
    print("=" * 70)
    if ok:
        print("✓ ГОТОВО")
        print("=" * 70)
        print()
        print("Что дальше:")
        print("  1. Обновите импорт в server.py:")
        print("        from ui import (...)")
        print("     вместо 'from templates import (...)'")
        print()
        print("  2. Обновите импорт в maps_routes.py:")
        print("        from ui import MAPS_HTML, ARCHIVE_HTML")
        print()
        print("  3. Проверьте:")
        print("        python -c \"import server; print('OK')\"")
        print("        python server.py")
        print()
        print("  4. Только после успешной проверки удалите templates.py:")
        print("        git rm templates.py")
        print("     (бэкап останется: templates.py.backup_before_split)")
    else:
        print("✗ БЫЛИ ОШИБКИ")
        print("=" * 70)
        print("Проверьте вывод выше. Откат:")
        print(f"  rm -rf {UI_DIR}/")
        print(f"  cp {BACKUP} {SOURCE}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())