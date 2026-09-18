# -*- coding: utf-8 -*-
"""
Словари: коды погоды, иконки, направления ветра.
"""

CODE_TO_TEXT = {
    0: "Ясно", 1: "Преим. ясно", 2: "Перем. обл.", 3: "Пасмурно",
    45: "Туман", 48: "Изморозь",
    51: "Слабая морось", 53: "Морось", 55: "Сильная морось",
    61: "Слабый дождь", 63: "Дождь", 65: "Сильный дождь",
    66: "Переохл. дождь", 67: "Сильный переохл. дождь",
    71: "Слабый снег", 73: "Снег", 75: "Сильный снег",
    77: "Снежные зёрна",
    80: "Слабые ливни", 81: "Ливни", 82: "Сильные ливни",
    85: "Слабый снегопад", 86: "Сильный снегопад",
    95: "Гроза", 96: "Гроза с градом", 99: "Сильная гроза",
}

WEATHER_ICONS = {
    "clear": """<svg viewBox="0 0 64 64" width="48" height="48">
      <circle cx="32" cy="32" r="12" fill="#ffb547"/>
      <g stroke="#ffb547" stroke-width="3" stroke-linecap="round">
        <line x1="32" y1="6" x2="32" y2="14"/><line x1="32" y1="50" x2="32" y2="58"/>
        <line x1="6" y1="32" x2="14" y2="32"/><line x1="50" y1="32" x2="58" y2="32"/>
        <line x1="13" y1="13" x2="19" y2="19"/><line x1="45" y1="45" x2="51" y2="51"/>
        <line x1="13" y1="51" x2="19" y2="45"/><line x1="45" y1="19" x2="51" y2="13"/>
      </g></svg>""",
    "mostly-clear": """<svg viewBox="0 0 64 64" width="48" height="48">
      <circle cx="24" cy="26" r="10" fill="#ffb547"/>
      <path d="M22 40 Q22 32 32 32 Q42 32 42 40 Q50 40 50 46 Q50 52 42 52 L22 52 Q14 52 14 46 Q14 40 22 40 Z"
            fill="#a8b4d0" opacity="0.9"/></svg>""",
    "partly-cloudy": """<svg viewBox="0 0 64 64" width="48" height="48">
      <circle cx="22" cy="22" r="8" fill="#ffb547"/>
      <path d="M18 42 Q18 34 28 34 Q36 34 38 40 Q48 38 50 46 Q52 54 44 54 L20 54 Q12 54 12 46 Q12 40 18 42 Z"
            fill="#a8b4d0"/></svg>""",
    "overcast": """<svg viewBox="0 0 64 64" width="48" height="48">
      <path d="M14 44 Q14 34 26 34 Q34 34 38 40 Q50 38 52 46 Q54 54 44 54 L18 54 Q10 54 10 46 Q10 40 14 44 Z"
            fill="#8892b0"/></svg>""",
    "fog": """<svg viewBox="0 0 64 64" width="48" height="48">
      <g stroke="#a8b4d0" stroke-width="3" stroke-linecap="round" opacity="0.85">
        <line x1="10" y1="22" x2="54" y2="22"/>
        <line x1="10" y1="30" x2="54" y2="30"/>
        <line x1="10" y1="38" x2="54" y2="38"/>
        <line x1="10" y1="46" x2="54" y2="46"/>
      </g></svg>""",
    "rain": """<svg viewBox="0 0 64 64" width="48" height="48">
      <path d="M14 36 Q14 28 24 28 Q32 28 36 34 Q46 32 48 40 Q50 46 42 46 L18 46 Q10 46 10 40 Q10 36 14 36 Z"
            fill="#8892b0"/>
      <g stroke="#4dabff" stroke-width="3" stroke-linecap="round">
        <line x1="20" y1="50" x2="18" y2="58"/>
        <line x1="32" y1="50" x2="30" y2="58"/>
        <line x1="44" y1="50" x2="42" y2="58"/>
      </g></svg>""",
    "showers": """<svg viewBox="0 0 64 64" width="48" height="48">
      <path d="M14 34 Q14 26 24 26 Q32 26 36 32 Q46 30 48 38 Q50 44 42 44 L18 44 Q10 44 10 38 Q10 34 14 34 Z"
            fill="#8892b0"/>
      <circle cx="22" cy="52" r="2.5" fill="#4dabff"/>
      <circle cx="34" cy="54" r="2.5" fill="#4dabff"/>
      <circle cx="46" cy="52" r="2.5" fill="#4dabff"/></svg>""",
    "snow": """<svg viewBox="0 0 64 64" width="48" height="48">
      <path d="M14 36 Q14 28 24 28 Q32 28 36 34 Q46 32 48 40 Q50 46 42 46 L18 46 Q10 46 10 40 Q10 36 14 36 Z"
            fill="#8892b0"/>
      <g stroke="#b4dcff" stroke-width="2" stroke-linecap="round">
        <g transform="translate(20,54)"><line x1="-3" y1="0" x2="3" y2="0"/><line x1="0" y1="-3" x2="0" y2="3"/></g>
        <g transform="translate(32,56)"><line x1="-3" y1="0" x2="3" y2="0"/><line x1="0" y1="-3" x2="0" y2="3"/></g>
        <g transform="translate(44,54)"><line x1="-3" y1="0" x2="3" y2="0"/><line x1="0" y1="-3" x2="0" y2="3"/></g>
      </g></svg>""",
    "snow-showers": """<svg viewBox="0 0 64 64" width="48" height="48">
      <path d="M14 34 Q14 26 24 26 Q32 26 36 32 Q46 30 48 38 Q50 44 42 44 L18 44 Q10 44 10 38 Q10 34 14 34 Z"
            fill="#8892b0"/>
      <g stroke="#b4dcff" stroke-width="2" stroke-linecap="round">
        <g transform="translate(20,54) rotate(45)"><line x1="-3" y1="0" x2="3" y2="0"/><line x1="0" y1="-3" x2="0" y2="3"/></g>
        <g transform="translate(34,55) rotate(45)"><line x1="-3" y1="0" x2="3" y2="0"/><line x1="0" y1="-3" x2="0" y2="3"/></g>
        <g transform="translate(46,54) rotate(45)"><line x1="-3" y1="0" x2="3" y2="0"/><line x1="0" y1="-3" x2="0" y2="3"/></g>
      </g></svg>""",
    "thunder": """<svg viewBox="0 0 64 64" width="48" height="48">
      <path d="M14 34 Q14 26 24 26 Q32 26 36 32 Q46 30 48 38 Q50 44 42 44 L18 44 Q10 44 10 38 Q10 34 14 34 Z"
            fill="#8892b0"/>
      <polygon points="32,44 26,54 32,54 28,62 40,50 34,50 38,44" fill="#ffb547"/></svg>""",
    "unknown": """<svg viewBox="0 0 64 64" width="48" height="48">
      <circle cx="32" cy="32" r="16" fill="none" stroke="#6b7694" stroke-width="2"/>
      <text x="32" y="38" text-anchor="middle" fill="#6b7694"
            font-size="20" font-family="Inter">?</text></svg>""",
}

_WIND_SECTORS = [
    "С", "ССВ", "СВ", "ВСВ", "В", "ВЮВ", "ЮВ", "ЮЮВ",
    "Ю", "ЮЮЗ", "ЮЗ", "ЗЮЗ", "З", "ЗСЗ", "СЗ", "ССЗ",
]
_WIND_ARROWS = ["↓", "↙", "←", "↖", "↑", "↗", "→", "↘",
                "↓", "↙", "←", "↖", "↑", "↗", "→", "↘"]