# -*- coding: utf-8 -*-
"""
Показывает все определения констант NAME = ... в templates.py
и отмечает дубликаты.

Запуск:
    python check_dups.py
"""

import sys
import io

# Чтобы русский вывод работал в cmd/PowerShell
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FILE = 'templates.py'

# Все константы, которые нас интересуют
NAMES = [
    'BASE_STYLE',
    'COMMON_JS',
    'FORECAST_HUB_HTML',
    'ANALYSIS_HUB_HTML',
    'THEORY_HUB_HTML',
    'INDEX_HTML',
    'ABOUT_HTML',
    'MAP_HTML',
    'TEACHING_HTML',
    'TROPOPAUSE_HTML',
    'VERIFY_HTML',
    'VERIFY_HISTORY_HTML',
    'ANALYZE_HTML',
    'AVIATION_HTML',
    'COMPARE_MATRICES_HTML',
    'CHART_HTML',
    'COMPARE_HTML',
    'MODEL_HTML',
    'TABLE_TEMPLATE',
    'TEXT_TEMPLATE',
    'SEARCH_HTML',
    'POINT_TEMPLATE',
    'SYNOPTIC_HTML',
    'CLIMATE_HTML',
    'ALT_VERIFY_HTML',
    'BIBLIOGRAPHY_HTML',
    'THEORY_METHODS_HTML',
    'THEORY_MATRICES_HTML',
    'THEORY_INDICES_HTML',
    'TESTS_HTML',
    'COMPARE_POINT_HTML',
    'ARCHIVE_HTML',
    'MAPS_HTML',
]


def main():
    try:
        with open(FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Файл %s не найден. Запусти скрипт из папки проекта." % FILE)
        return 1
    except Exception as e:
        print("Ошибка чтения файла: %s" % e)
        return 1

    lines = content.splitlines()
    print("Файл: %s" % FILE)
    print("Строк: %d, символов: %d" % (len(lines), len(content)))
    print("")

    # ==========================================================
    # 1. Все определения NAME = ... (в начале строки, без отступов)
    # ==========================================================
    print("=" * 72)
    print("Все определения NAME = ... (в начале строки, без отступов):")
    print("=" * 72)

    found = {name: [] for name in NAMES}

    for i, line in enumerate(lines, 1):
        for name in NAMES:
            # NAME = ... или NAME=...
            if line.startswith(name + ' =') or line.startswith(name + '='):
                found[name].append(i)
                preview = line.rstrip()[:88]
                print("  стр. %5d: %s" % (i, preview))
                break

    print("")
    print("=" * 72)
    print("Итог по каждой константе:")
    print("=" * 72)

    total_dups = 0
    for name in NAMES:
        positions = found[name]
        if len(positions) == 0:
            status = "НЕ НАЙДЕНА"
        elif len(positions) == 1:
            status = "OK"
        else:
            status = "ДУБЛИКАТ x%d" % len(positions)
            total_dups += len(positions) - 1
        pos_str = ", ".join("стр. %d" % p for p in positions) if positions else ""
        print("  %-28s : %-15s %s" % (name, status, pos_str))

    print("")
    print("=" * 72)
    print("Всего дубликатов (лишних определений): %d" % total_dups)
    print("=" * 72)

    # ==========================================================
    # 2. Для каждой константы с дубликатами — где находится её блок
    # ==========================================================
    if total_dups > 0:
        print("")
        print("=" * 72)
        print("Границы блоков для констант с дубликатами:")
        print("=" * 72)

        # Все определения любых констант + строки-разделители "# ===="
        all_defs = []
        for i, line in enumerate(lines, 1):
            for name in NAMES:
                if line.startswith(name + ' =') or line.startswith(name + '='):
                    all_defs.append((i, name))
                    break

        # Строки-разделители "# ===...===="
        sep_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('# ====') and set(stripped) <= set('#= '):
                sep_lines.append(i)

        for name in NAMES:
            positions = found[name]
            if len(positions) <= 1:
                continue

            print("")
            print("--- %s ---" % name)
            for idx, start_line in enumerate(positions):
                # Находим начало блока — разделитель выше start_line
                block_start = start_line
                prev_seps = [s for s in sep_lines if s < start_line]
                if prev_seps:
                    last_sep = prev_seps[-1]
                    # Если между last_sep и start_line <= 5 строк — включаем
                    if start_line - last_sep <= 5:
                        block_start = last_sep
                        # Парный разделитель выше (шапка из 3 строк)
                        prev2 = [s for s in prev_seps if s < last_sep]
                        if prev2 and last_sep - prev2[-1] <= 3:
                            block_start = prev2[-1]

                # Находим конец блока — следующее определение любой константы
                next_defs = [(l, n) for (l, n) in all_defs if l > start_line]
                if next_defs:
                    next_def_line = next_defs[0][0]
                    # Отступим к разделителю перед next_def
                    seps_before_next = [s for s in sep_lines
                                        if s < next_def_line and s > start_line]
                    if seps_before_next:
                        block_end = seps_before_next[-1] - 1
                    else:
                        block_end = next_def_line - 1
                else:
                    block_end = len(lines)

                marker = "← ОСТАВИТЬ" if idx == 0 else "← УДАЛИТЬ"
                print("  вхождение #%d: строки %d..%d  (%d строк)  %s"
                      % (idx + 1, block_start, block_end,
                         block_end - block_start + 1, marker))

    return 0


if __name__ == '__main__':
    sys.exit(main())