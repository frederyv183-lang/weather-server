# -*- coding: utf-8 -*-
"""
patch_ui.py — патч для ui/forecast.py и ui/synoptic.py:
добавляет блок сводки за сутки (situation + phenomena).

Запуск: python patch_ui.py
Идемпотентен: повторный запуск безопасен.
"""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent


def read(p): return p.read_text(encoding="utf-8")
def write(p, t): p.write_text(t, encoding="utf-8"); print(f"  записан: {p.name}")


# ============================================================
# ui/forecast.py — TABLE_TEMPLATE
# ============================================================

def patch_ui_forecast():
    print("\n[1/2] ui/forecast.py — TABLE_TEMPLATE")
    path = ROOT / "ui" / "forecast.py"
    if not path.exists():
        print("  SKIP: файл не найден")
        return
    text = read(path)
    marker = "[PATCH ui.forecast.day_summary]"
    if marker in text:
        print("  SKIP: уже пропатчен")
        return

    # --- 1. CSS ---
    # Ищем любой .error-box в TABLE_TEMPLATE (первое вхождение)
    css_pattern = re.compile(
        r'(\.error-box\s*\{[^}]*\})',
        re.DOTALL,
    )
    css_new = r'''\1

  /* [PATCH ui.forecast.day_summary] */
  .day-summary {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin: 8px 0 12px 0;
    padding: 10px 14px;
    background: rgba(77, 171, 255, 0.06);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    font-size: 13px;
    color: var(--text-1);
  }
  .day-summary .situation {
    font-weight: 700;
    color: var(--accent);
  }
  .day-summary .phenomena {
    color: var(--text-0);
  }'''

    if css_pattern.search(text):
        text = css_pattern.sub(css_new, text, count=1)
        print("  CSS добавлен")
    else:
        print("  WARN: .error-box не найден — CSS не добавлен")

    # --- 2. HTML ---
    # Ищем day-header с day-title и day-events
    html_pattern = re.compile(
        r'(<div class="day-header">\s*\n'
        r'\s*<div class="day-title">.*?</div>\s*\n'
        r'\s*<div class="day-events">.*?</div>\s*\n'
        r'\s*</div>\s*\n)'
        r'(\s*<div style="overflow-x:auto;">)',
        re.DOTALL,
    )
    html_new = r'''\1
  <!-- [PATCH ui.forecast.day_summary] -->
  {% if day.summary %}
  <div class="day-summary">
    <span class="situation">🌍 {{ day.summary.situation }}</span>
    <span class="phenomena">{{ day.summary.phenomena }}</span>
  </div>
  {% endif %}

\2'''

    if html_pattern.search(text):
        text = html_pattern.sub(html_new, text, count=1)
        print("  HTML добавлен")
    else:
        print("  WARN: day-header не найден — HTML не добавлен")

    write(path, text)


# ============================================================
# ui/synoptic.py — AVIATION_HTML
# ============================================================

def patch_ui_synoptic():
    print("\n[2/2] ui/synoptic.py — AVIATION_HTML")
    path = ROOT / "ui" / "synoptic.py"
    if not path.exists():
        print("  SKIP: файл не найден")
        return
    text = read(path)
    marker = "[PATCH ui.synoptic.day_summary]"
    if marker in text:
        print("  SKIP: уже пропатчен")
        return

    # --- 1. CSS ---
    # Ищем .error-box внутри AVIATION_HTML (второе вхождение .error-box в файле)
    # Проще: ищем уникальный кусок перед </style> в AVIATION_HTML
    css_pattern = re.compile(
        r'(\.error-box\s*\{[^}]*\})'
        r'(\s*</style>\s*\n\s*</head>\s*\n\s*<body>\s*\n\s*""" \+ render_header\("forecast"\) \+ """\s*\n\s*<h1>✈️ Авиационные прогнозы</h1>)',
        re.DOTALL,
    )
    css_new = r'''\1

  /* [PATCH ui.synoptic.day_summary] */
  .day-summary {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin: 8px 0 12px 0;
    padding: 10px 14px;
    background: rgba(77, 171, 255, 0.06);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    font-size: 13px;
    color: var(--text-1);
  }
  .day-summary .situation {
    font-weight: 700;
    color: var(--accent);
  }
  .day-summary .phenomena {
    color: var(--text-0);
  }
\2'''

    if css_pattern.search(text):
        text = css_pattern.sub(css_new, text, count=1)
        print("  CSS добавлен")
    else:
        # Fallback: ищем просто .error-box и добавляем CSS перед ним
        # (первое вхождение в файле может быть в другом шаблоне)
        print("  WARN: точный CSS-паттерн не найден, пробую fallback...")
        # Ищем <h1>✈️ Авиационные прогнозы</h1> и вставляем CSS перед </style>
        # выше этого места
        idx = text.find("<h1>✈️ Авиационные прогнозы</h1>")
        if idx > 0:
            # Ищем </style> перед этим индексом
            style_end = text.rfind("</style>", 0, idx)
            if style_end > 0:
                css_block = '''
  /* [PATCH ui.synoptic.day_summary] */
  .day-summary {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin: 8px 0 12px 0;
    padding: 10px 14px;
    background: rgba(77, 171, 255, 0.06);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    font-size: 13px;
    color: var(--text-1);
  }
  .day-summary .situation {
    font-weight: 700;
    color: var(--accent);
  }
  .day-summary .phenomena {
    color: var(--text-0);
  }
'''
                text = text[:style_end] + css_block + text[style_end:]
                print("  CSS добавлен (fallback)")
        else:
            print("  WARN: <h1>✈️ Авиационные прогнозы</h1> не найден — CSS не добавлен")

    # --- 2. HTML ---
    # Ищем day-block с day-header (только заголовок, без day-events)
    html_pattern = re.compile(
        r'(<div class="day-block fade-in">\s*\n'
        r'\s*<div class="day-header">\s*\n'
        r'\s*<div class="day-title">.*?</div>\s*\n'
        r'\s*</div>\s*\n)'
        r'(\s*<div style="overflow-x:auto;">)',
        re.DOTALL,
    )
    html_new = r'''\1
  <!-- [PATCH ui.synoptic.day_summary] -->
  {% if day.summary %}
  <div class="day-summary">
    <span class="situation">🌍 {{ day.summary.situation }}</span>
    <span class="phenomena">{{ day.summary.phenomena }}</span>
  </div>
  {% endif %}

\2'''

    if html_pattern.search(text):
        text = html_pattern.sub(html_new, text, count=1)
        print("  HTML добавлен")
    else:
        print("  WARN: day-block/day-header не найден — HTML не добавлен")

    write(path, text)


def main():
    print("=" * 60)
    print("patch_ui.py — патч для ui/forecast.py и ui/synoptic.py")
    print("=" * 60)
    patch_ui_forecast()
    patch_ui_synoptic()
    print("\n" + "=" * 60)
    print("Готово. Проверьте:")
    print("  python -c \"t=open('ui/forecast.py',encoding='utf-8').read(); print('forecast:', '[PATCH ui.forecast.day_summary]' in t)\"")
    print("  python -c \"t=open('ui/synoptic.py',encoding='utf-8').read(); print('synoptic:', '[PATCH ui.synoptic.day_summary]' in t)\"")
    print("=" * 60)


if __name__ == "__main__":
    main()