# -*- coding: utf-8 -*-
"""
Чистит templates.py:
  1. Удаляет дубликаты констант, ориентируясь на блоки-комментарии
     "# ===...===" + "# ИМЯ" + "# ===...===" перед каждой константой.
     Оставляет только ПЕРВОЕ вхождение.
  2. Убирает дублирующуюся ссылку (Прогноз) в MAPS_HTML.
  3. Проверяет синтаксис и импорт.

Создаёт бэкап templates.py.bak
"""

import re
import shutil
import sys

FILE = "templates.py"
BACKUP = "templates.py.bak"

DUP_CONSTS = [
    "TEXT_TEMPLATE",
    "SEARCH_HTML",
    "SYNOPTIC_HTML",
    "CLIMATE_HTML",
    "POINT_TEMPLATE",
]


def find_const_blocks(content, name):
    """
    Возвращает список (start, end) для каждого определения NAME.
    Начало - строка NAME = ... (или предшествующий комментарий-разделитель,
    если он есть).
    Конец - позиция перед следующим определением константы (любой)
    или перед следующим комментарием-разделителем, или конец файла.
    """
    # Все определения констант вида NAME = ... в начале строки
    const_re = re.compile(r'^([A-Z_][A-Z0-9_]*)\s*=\s*', re.MULTILINE)
    all_defs = [(m.start(), m.group(1)) for m in const_re.finditer(content)]

    # Комментарии-разделители "# ===...===" (строка из 60+ знаков =)
    sep_re = re.compile(r'^# ={20,}\s*$', re.MULTILINE)
    all_seps = [m.start() for m in sep_re.finditer(content)]

    result = []

    for i, (start, cname) in enumerate(all_defs):
        if cname != name:
            continue

        # Конец блока: следующее определение константы (любой)
        if i + 1 < len(all_defs):
            end = all_defs[i + 1][0]
            # Отступим до ближайшего комментария-разделителя перед следующим определением
            seps_before = [s for s in all_seps if s < end and s > start]
            if seps_before:
                end = seps_before[-1]
        else:
            end = len(content)

        # Начало: отступим до комментария-разделителя ПЕРЕД start, если он рядом
        seps_before_start = [s for s in all_seps if s < start]
        block_start = start
        if seps_before_start:
            last_sep = seps_before_start[-1]
            # Если между ним и start только пустые строки — включаем его
            between = content[last_sep:start]
            if between.count('\n') <= 5:  # эвристика
                # Начало блока — от самого первого = в этой секции
                # Найдём первый разделитель подряд идущих
                # (обычно их 3: ===, # ИМЯ, ===)
                prev_seps = [s for s in all_seps if s < last_sep]
                if prev_seps:
                    prev_sep = prev_seps[-1]
                    between2 = content[prev_sep:last_sep]
                    if between2.count('\n') <= 3:
                        # Есть парный разделитель - берём его
                        prev2 = [s for s in all_seps if s < prev_sep]
                        if prev2:
                            prev2_sep = prev2[-1]
                            between3 = content[prev2_sep:prev_sep]
                            if between3.count('\n') <= 3:
                                block_start = prev2_sep
                            else:
                                block_start = prev_sep
                        else:
                            block_start = prev_sep
                    else:
                        block_start = last_sep
                else:
                    block_start = last_sep

        result.append((block_start, end))

    return result


def remove_duplicates(content):
    """Удаляет все блоки константы кроме первого."""
    for name in DUP_CONSTS:
        blocks = find_const_blocks(content, name)
        if len(blocks) <= 1:
            print("  %s: %d вхождений - OK" % (name, len(blocks)))
            continue

        print("  %s: %d вхождений - удаляю %d"
              % (name, len(blocks), len(blocks) - 1))

        # Удаляем с конца, чтобы индексы не съехали
        for (bstart, bend) in reversed(blocks[1:]):
            # Съедаем лишние \n вокруг
            while bstart > 0 and content[bstart - 1] == '\n':
                bstart -= 1
            while bend < len(content) and content[bend] == '\n':
                bend += 1
            content = content[:bstart] + '\n' + content[bend:]

    return content


def fix_maps_duplicate_back_link(content):
    """Убирает дублирующуюся ссылку Прогноз в MAPS_HTML."""
    a1 = '<a class="back" href="/forecast">'
    a2 = '</a>'
    dup_re = re.compile(
        re.escape(a1) + r'[^\n]*' + re.escape(a2) + r'\n'
        + re.escape(a1) + r'[^\n]*' + re.escape(a2)
    )
    new_content, n = dup_re.subn(
        a1 + '\u2190 \u041f\u0440\u043e\u0433\u043d\u043e\u0437' + a2,
        content
    )
    if n:
        print("  Убрано дублирующихся ссылок: %d" % n)
        return new_content
    print("  Дублирующихся ссылок не найдено")
    return content


def check_maps_html_clean(content):
    """Проверяет, что в MAPS_HTML нет архивных JS-функций."""
    m = re.search(r'^MAPS_HTML\s*=\s*r?"""', content, re.MULTILINE)
    if not m:
        print("  MAPS_HTML не найден - пропускаю проверку")
        return

    start = m.start()
    close = content.find('\n' + '"""', m.end())
    if close == -1:
        maps = content[start:]
    else:
        maps = content[start:close]

    problems = []
    for token in ['archiveRuns', 'loadArchive', 'loadArchiveRun',
                  'switchToLatest', 'archive-select']:
        if token in maps:
            problems.append(token)

    if problems:
        print("  ! В MAPS_HTML остались: %s" % ', '.join(problems))
    else:
        print("  OK: MAPS_HTML чистый (нет архивных JS-функций)")


def main():
    print("=" * 60)
    print("Очистка templates.py")
    print("=" * 60)

    shutil.copy(FILE, BACKUP)
    print("Бэкап: %s" % BACKUP)

    with open(FILE, "r", encoding="utf-8") as f:
        content = f.read()
    original_size = len(content)
    print("Исходный размер: %d символов" % original_size)

    print("")
    print("[1] Дубликаты констант:")
    content = remove_duplicates(content)

    print("")
    print("[2] Дублирующаяся ссылка в MAPS_HTML:")
    content = fix_maps_duplicate_back_link(content)

    with open(FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print("")
    print("Новый размер: %d символов" % len(content))
    print("Удалено: %d символов" % (original_size - len(content)))

    print("")
    print("[3] Проверка синтаксиса Python:")
    try:
        compile(content, FILE, 'exec')
        print("  OK: синтаксис Python корректен")
    except SyntaxError as e:
        print("  FAIL: SyntaxError: %s" % e)
        print("  Откат: copy %s %s" % (BACKUP, FILE))
        return 1

    print("")
    print("[4] Импорт модуля:")
    try:
        if 'templates' in sys.modules:
            del sys.modules['templates']
        import templates
        print("  OK: templates импортирован")
        for name in ['ARCHIVE_HTML', 'MAPS_HTML', 'TEXT_TEMPLATE',
                     'SEARCH_HTML', 'SYNOPTIC_HTML', 'CLIMATE_HTML',
                     'POINT_TEMPLATE']:
            val = getattr(templates, name, None)
            if val is None:
                print("    %s: ОТСУТСТВУЕТ" % name)
            else:
                print("    %s: %d символов" % (name, len(val)))
    except Exception as e:
        print("  FAIL: ошибка импорта: %s" % e)
        print("  Откат: copy %s %s" % (BACKUP, FILE))
        return 1

    print("")
    print("[5] Проверка MAPS_HTML:")
    check_maps_html_clean(content)

    print("")
    print("=" * 60)
    print("ГОТОВО")
    print("=" * 60)
    print("Бэкап: %s" % BACKUP)
    print("Откат: copy templates.py.bak templates.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())