# -*- coding: utf-8 -*-
"""
Удаляет строки 5144..6185 из templates.py (вторые вхождения
TEXT_TEMPLATE, SEARCH_HTML, POINT_TEMPLATE, SYNOPTIC_HTML, CLIMATE_HTML).

Делает бэкап templates.py.bak2
"""

import shutil
import sys
import io

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                  errors='replace')

FILE = 'templates.py'
BACKUP = 'templates.py.bak2'

# Границы удаляемого блока (включительно), 1-based
START = 5144
END = 6185

# Бэкап
shutil.copy(FILE, BACKUP)
print("Бэкап: %s" % BACKUP)

# Читаем
with open(FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Было строк: %d" % len(lines))

# Проверяем границы
if START < 1 or END > len(lines) or START > END:
    print("ОШИБКА: диапазон %d..%d вне файла (строк: %d)"
          % (START, END, len(lines)))
    sys.exit(1)

print("")
print("Первая удаляемая строка  (%d): %s" % (START, lines[START - 1].rstrip()))
print("Последняя удаляемая строка(%d): %s" % (END, lines[END - 1].rstrip()))
print("")

# Удаляем: строки с индексами START-1 .. END-1 (0-based)
new_lines = lines[:START - 1] + lines[END:]

print("Стало строк: %d" % len(new_lines))
print("Удалено строк: %d" % (len(lines) - len(new_lines)))

# Записываем
with open(FILE, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# Проверка синтаксиса
print("")
print("Проверка синтаксиса Python...")
try:
    content = ''.join(new_lines)
    compile(content, FILE, 'exec')
    print("  OK: синтаксис корректен")
except SyntaxError as e:
    print("  FAIL: SyntaxError: %s" % e)
    print("  Откат: copy %s %s" % (BACKUP, FILE))
    sys.exit(1)

# Проверка импорта
print("")
print("Проверка импорта...")
try:
    for mod in ['templates']:
        if mod in sys.modules:
            del sys.modules[mod]
    import templates
    print("  OK: templates импортирован")
    for name in ['TEXT_TEMPLATE', 'SEARCH_HTML', 'POINT_TEMPLATE',
                 'SYNOPTIC_HTML', 'CLIMATE_HTML',
                 'ALT_VERIFY_HTML', 'BIBLIOGRAPHY_HTML',
                 'MAPS_HTML', 'ARCHIVE_HTML']:
        val = getattr(templates, name, None)
        print("    %-25s: %s символов"
              % (name, len(val) if val else 'ОТСУТСТВУЕТ'))
except Exception as e:
    print("  FAIL: %s" % e)
    print("  Откат: copy %s %s" % (BACKUP, FILE))
    sys.exit(1)

print("")
print("=" * 60)
print("ГОТОВО")
print("=" * 60)
print("Откат: copy %s %s" % (BACKUP, FILE))