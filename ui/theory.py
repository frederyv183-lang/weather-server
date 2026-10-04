# -*- coding: utf-8 -*-
"""Теория: методы, матрицы, индексы, учебные примеры."""

from ui.styles import (
    BASE_STYLE,
    COMMON_JS,
    render_header,
    render_legend,
    render_biblio_ref,
)
TEACHING_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Учебные примеры — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .topic-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    gap: 16px; margin: 20px 0;
  }
  .topic-card {
    padding: 20px 22px; border-radius: 16px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border); backdrop-filter: blur(14px);
    transition: all 0.25s;
  }
  .topic-card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--card-shadow);
    transform: translateY(-2px);
  }
  .topic-card h3 {
    margin: 0 0 8px 0; font-size: 17px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .topic-card .source {
    font-size: 11px; color: var(--text-2); margin-bottom: 10px;
    font-family: 'JetBrains Mono', monospace;
  }
  .topic-card p {
    color: var(--text-1); font-size: 13px; line-height: 1.6;
    margin: 0 0 12px 0;
  }
  .topic-card .formula {
    background: rgba(15,21,36,0.5); padding: 10px 14px;
    border-radius: 8px; border: 1px solid var(--border);
    font-family: 'JetBrains Mono', monospace; font-size: 12px;
    color: var(--accent); margin: 10px 0; overflow-x: auto;
  }
  .topic-card .links {
    display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px;
  }
  .topic-card .links a {
    padding: 6px 12px; border-radius: 8px; text-decoration: none;
    font-size: 12px; font-weight: 600;
    background: rgba(77,171,255,0.10);
    border: 1px solid rgba(77,171,255,0.3);
    color: var(--accent);
    transition: all 0.2s;
  }
  .topic-card .links a:hover {
    background: rgba(77,171,255,0.20);
    border-color: var(--border-hover);
  }
</style>
</head>
<body>

""" + render_header("theory") + """
<h1>📚 Учебные примеры и методы</h1>
<div class="sub">По учебнику О. Г. Богаткина «Авиационные прогнозы погоды» (СПб, 2010)</div>

<div class="topic-grid">

  <div class="topic-card fade-in">
    <h3>🌡 Прогноз минимальной температуры</h3>
    <div class="source">Богаткин, гл. 5.2, с. 114–118</div>
    <p>Методы А. С. Зверева, М. Е. Берлянда, Михельсона, Куприянова.
       Учёт облачности и ветра через коэффициент <i>m</i>.</p>
    <div class="formula">T<sub>мин</sub> = T<sub>13</sub> − 0.5·(T<sub>13</sub> − T<sub>d13</sub>) − 6</div>
    <div class="formula">T<sub>мин</sub> = T<sub>макс</sub> − m·A</div>
    <div class="links">
      <a href="/forecast/gfs/tushino">📊 Таблица</a>
      <a href="/point-chart?lat=55.85&lon=37.44&name=Тушино">📈 График</a>
    </div>
  </div>

  <div class="topic-card fade-in">
    <h3>💨 Прогноз ветра у земли</h3>
    <div class="source">Богаткин, гл. 6.3, с. 131–138</div>
    <p>Метод А. С. Зверева (по градиенту давления), метод О. Г. Богаткина
       (по барической тенденции), определение порывов.</p>
    <div class="formula">U = 2·B − 1   (шкала Бофорта)</div>
    <div class="formula">U<sub>пор</sub> = U<sub>ср</sub> + 0.5·U<sub>ср</sub></div>
    <div class="links">
      <a href="/forecast/gfs/tushino">📊 Таблица</a>
      <a href="/point-chart?lat=55.85&lon=37.44&name=Тушино">📈 Ветер</a>
    </div>
  </div>

  <div class="topic-card fade-in">
    <h3>☁️ Прогноз низкой облачности</h3>
    <div class="source">Богаткин, гл. 8.3, с. 161–172</div>
    <p>Формулы Ипполитова, Ферреля, метод Е. И. Гоголевой, ГАМЦ,
       В. М. Ярковой, прогноз облачности ниже 400 м в Красноярске.</p>
    <div class="formula">H = 122·(T − T<sub>d</sub>)<sub>0</sub>   (Феррель)</div>
    <div class="formula">H = 24·(100 − R)   (Ипполитов)</div>
    <div class="links">
      <a href="/forecast/gfs/tushino">📊 Таблица</a>
      <a href="/point-synoptic?lat=55.85&lon=37.44&name=Тушино">🌡 Синоптика</a>
    </div>
  </div>

  <div class="topic-card fade-in">
    <h3>🌫 Прогноз туманов</h3>
    <div class="source">Богаткин, гл. 9, с. 176–202</div>
    <p>Методы Н. В. Петренко, Б. В. Кирюхина, А. С. Зверева, Д. Н. Лаврищева,
       Р. М. Меджитова. Радиационные и адвективные туманы. Морозные туманы.</p>
    <div class="formula">T<sub>т</sub> = T<sub>d</sub> − ΔT<sub>d</sub></div>
    <div class="formula">S<sub>м</sub> = 60 / q<sup>0.5</sup></div>
    <div class="links">
      <a href="/aviation/gfs/tushino">✈️ Авиация</a>
      <a href="/alt-verify/tushino?phenomenon=fog">📋 Матрица (туман)</a>
    </div>
  </div>

  <div class="topic-card fade-in">
    <h3>⛈ Прогноз гроз и града</h3>
    <div class="source">Богаткин, гл. 10, с. 203–238</div>
    <p>Метод частицы, методы Н. В. Лебедевой, Бейли, Вайтинга, Фауста,
       Г. Д. Решетова, И. А. Славина, Кокса. Прогноз града и смерчей.</p>
    <div class="formula">K = 2·T<sub>850</sub> − T<sub>500</sub> − D<sub>850</sub> − D<sub>700</sub>   (Вайтинг)</div>
    <div class="formula">A ≥ 0   →   гроза   (Фатеев)</div>
    <div class="links">
      <a href="/aviation/gfs/tushino">✈️ Авиация</a>
      <a href="/alt-verify/tushino?phenomenon=thunder">📋 Матрица (гроза)</a>
    </div>
  </div>

  <div class="topic-card fade-in">
    <h3>🌧 Прогноз осадков и видимости</h3>
    <div class="source">Богаткин, гл. 11–12, с. 239–263</div>
    <p>Моросящие, обложные, ливневые осадки. Гололёд и гололедица.
       Прогноз видимости в туманах, осадках, метелях, пыльных бурях.</p>
    <div class="formula">S<sub>м</sub> = 2.3·10<sup>4</sup> / (r·q)</div>
    <div class="formula">L = T<sub>инв</sub> − T<sub>0</sub> − (0.0778·D² + 0.67·D)</div>
    <div class="links">
      <a href="/forecast/gfs/tushino">📊 Таблица</a>
      <a href="/verify/tushino">✅ Проверка</a>
    </div>
  </div>

</div>

""" + render_biblio_ref("aviation", "гл. 5–12") + """
""" + COMMON_JS +  """
</body>
</html>
"""




THEORY_METHODS_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Методы прогноза — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .method-block {
    margin: 24px 0;
    padding: 22px 24px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
  }
  .method-block h2 {
    margin: 0 0 14px 0;
    font-size: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .method-block p {
    color: var(--text-1);
    font-size: 14px;
    line-height: 1.7;
    margin: 10px 0;
  }
  .formula {
    background: rgba(15, 21, 36, 0.6);
    padding: 14px 18px;
    border-radius: 10px;
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--accent);
    margin: 14px 0;
    overflow-x: auto;
    line-height: 1.8;
  }
  .method-block ul {
    color: var(--text-1);
    font-size: 14px;
    line-height: 1.8;
    padding-left: 22px;
  }
  .method-block ul li { margin: 6px 0; }
  .method-block ul li b { color: var(--text-0); }
</style>
</head>
<body>

""" + render_header("theory") + """
<h1>📐 Методы прогноза</h1>
<div class="sub">Изоэнтропический анализ · потенциальная завихрённость · PV-аномалии</div>

<div class="method-block">
  <h2>🌀 Изоэнтропический анализ</h2>
  <p>
    <b>Идея.</b> Адиабатические процессы в атмосфере сохраняют потенциальную
    температуру θ. Движение воздуха происходит преимущественно вдоль
    изоэнтропических поверхностей (θ = const). Анализ на этих поверхностях
    выявляет динамически активные зоны, невидимые на изобарических картах.
  </p>

  <div class="formula">
θ = T · (p₀ / p)^(R/cp)
  </div>

  <p>
    где T — температура (K), p — давление (гПа), p₀ = 1000 гПа,
    R/cp ≈ 0.286 — отношение газовой постоянной к удельной теплоёмкости.
  </p>

  <p>
    <b>Применение.</b> Изоэнтропические карты используют для:
  </p>
  <ul>
    <li>выявления <b>складок тропопаузы</b> (где PV-аномалии опускаются в тропосферу);</li>
    <li>диагностики <b>струйных течений</b> и зон сильного ветра;</li>
    <li>анализа <b>фронтальных зон</b> — на изоэнтропах фронт виден как сгущение изолиний θ;</li>
    <li>прогноза <b>циклогенеза</b> — по аномалиям PV на 300–330 K.</li>
  </ul>
</div>

<div class="method-block">
  <h2>📊 Потенциальная завихрённость (PV)</h2>
  <p>
    <b>Ertel PV</b> — индикатор динамической устойчивости. Сохраняется при
    адиабатических процессах, что делает его идеальным трассером.
  </p>

  <div class="formula">
PV = −g · (ζ + f) · (∂θ / ∂p)
  </div>

  <p>
    где g = 9.81 м/с², ζ — относительная завихрённость, f = 2Ω·sin(φ) —
    параметр Кориолиса, θ — потенциальная температура, p — давление (Па).
  </p>

  <p>
    <b>Единица измерения:</b> 1 PVU = 10⁻⁶ м²·К·кг⁻¹·с⁻¹.
  </p>

  <p>
    <b>Пороги:</b>
  </p>
  <ul>
    <li><b>&lt; 0.5 PVU</b> — тропосферный воздух;</li>
    <li><b>2 PVU</b> — динамическая тропопауза (стандарт WMO);</li>
    <li><b>&gt; 4 PVU</b> — стратосферный воздух, вторгшийся в тропосферу.</li>
  </ul>

  <p>
    <b>PV-аномалии</b> — области с высоким PV, опустившиеся в тропосферу —
    связаны с:
  </p>
  <ul>
    <li>складками тропопаузы;</li>
    <li>струйными течениями на их периферии;</li>
    <li>циклогенезом (положительная PV-аномалия);</li>
    <li>турбулентностью в верхней тропосфере.</li>
  </ul>
</div>

<div class="method-block">
  <h2>🔬 Синоптический метод</h2>
  <p>
    Комплексный анализ приземных и высотных карт: приземное давление,
    барическая тенденция, геопотенциал H₅₀₀, адвекция температуры,
    фронтальные разделы, струйное течение.
  </p>

  <p>
    <b>Уровни анализа:</b>
  </p>
  <ul>
    <li><b>925 гПа</b> (~800 м) — приземный слой, инверсии, туманы;</li>
    <li><b>850 гПа</b> (~1500 м) — пограничный слой, адвекция тепла/холода;</li>
    <li><b>700 гПа</b> (~3000 м) — влагосодержание, слои конвекции;</li>
    <li><b>500 гПа</b> (~5500 м) — ведущий поток, гребни и ложбины;</li>
    <li><b>300 гПа</b> (~9000 м) — струйное течение, зона тропопаузы.</li>
  </ul>
</div>

""" + render_biblio_ref("synoptic", "гл. 3–4") + """
""" + COMMON_JS +  render_legend("synoptic") + """
</body>
</html>
"""




THEORY_MATRICES_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Матрицы и критерии — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .crit-block {
    margin: 24px 0;
    padding: 22px 24px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
  }
  .crit-block h2 {
    margin: 0 0 14px 0;
    font-size: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .crit-block p {
    color: var(--text-1);
    font-size: 14px;
    line-height: 1.7;
  }
  .formula {
    background: rgba(15, 21, 36, 0.6);
    padding: 14px 18px;
    border-radius: 10px;
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--accent);
    margin: 14px 0;
    overflow-x: auto;
    line-height: 1.8;
  }

  .matrix-2x2 {
    display: grid;
    grid-template-columns: 100px 1fr 1fr;
    gap: 6px;
    margin: 20px 0;
    max-width: 520px;
  }
  .matrix-cell {
    padding: 16px 12px;
    text-align: center;
    border-radius: 10px;
    font-family: 'JetBrains Mono', monospace;
  }
  .matrix-cell.header {
    background: transparent;
    color: var(--text-2);
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .matrix-cell.axis {
    background: transparent;
    color: var(--text-2);
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 10px;
  }
  .matrix-cell.hits {
    background: rgba(0, 229, 160, 0.15);
    color: #00e5a0;
    border: 1px solid rgba(0, 229, 160, 0.3);
  }
  .matrix-cell.correct {
    background: rgba(77, 171, 255, 0.12);
    color: #4dabff;
    border: 1px solid rgba(77, 171, 255, 0.25);
  }
  .matrix-cell.misses {
    background: rgba(255, 84, 112, 0.15);
    color: #ff5470;
    border: 1px solid rgba(255, 84, 112, 0.3);
  }
  .matrix-cell.false {
    background: rgba(255, 181, 71, 0.15);
    color: #ffb547;
    border: 1px solid rgba(255, 181, 71, 0.3);
  }
  .matrix-cell .num { font-size: 22px; font-weight: 700; display: block; }
  .matrix-cell .lbl { font-size: 10px; opacity: 0.8; display: block; margin-top: 2px; }

  .crit-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin-top: 14px;
  }
  .crit-table th {
    text-align: left;
    padding: 10px 12px;
    color: var(--text-2);
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  .crit-table td {
    padding: 10px 12px;
    border-bottom: 1px solid rgba(120, 160, 255, 0.06);
    color: var(--text-1);
  }
  .crit-table tr:hover td { background: rgba(77, 171, 255, 0.05); }
  .crit-table td.formula-cell {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--accent);
  }
  .crit-table td.name { color: var(--text-0); font-weight: 600; }
</style>
</head>
<body>

""" + render_header("theory") + """
<h1>📋 Матрицы и критерии успешности</h1>
<div class="sub">Матрица сопряжённости 2×2 · критерии Хандожко · интерпретация</div>

<div class="crit-block">
  <h2>📋 Матрица сопряжённости (2×2)</h2>
  <p>
    Основной инструмент верификации альтернативных прогнозов
    («явление будет / не будет»). Сопоставляет прогноз с фактом по 4 категориям.
  </p>

  <div class="matrix-2x2">
    <div class="matrix-cell header"></div>
    <div class="matrix-cell header">Факт: ДА</div>
    <div class="matrix-cell header">Факт: НЕТ</div>

    <div class="matrix-cell axis">Прогноз: ДА</div>
    <div class="matrix-cell hits">
      <span class="num">a</span>
      <span class="lbl">Hits</span>
    </div>
    <div class="matrix-cell false">
      <span class="num">b</span>
      <span class="lbl">False alarms</span>
    </div>

    <div class="matrix-cell axis">Прогноз: НЕТ</div>
    <div class="matrix-cell misses">
      <span class="num">c</span>
      <span class="lbl">Misses</span>
    </div>
    <div class="matrix-cell correct">
      <span class="num">d</span>
      <span class="lbl">Correct negatives</span>
    </div>
  </div>

  <p>
    где <b>a</b> — попадания (прогноз ДА / факт ДА),
    <b>b</b> — ложные тревоги (прогноз ДА / факт НЕТ),
    <b>c</b> — пропуски (прогноз НЕТ / факт ДА),
    <b>d</b> — правильные отрицания (прогноз НЕТ / факт НЕТ).
  </p>
</div>

<div class="crit-block">
  <h2>📊 Критерии Хандожко</h2>
  <p>
    Формулы для оценки качества альтернативных прогнозов
    (Хандожко Л. А., «Экономическая эффективность метеорологических прогнозов», Обнинск, 2008).
  </p>

  <table class="crit-table">
    <thead>
      <tr>
        <th>Критерий</th>
        <th>Формула</th>
        <th>Интерпретация</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="name">p — общая оправдываемость</td>
        <td class="formula-cell">(a + d) / (a + b + c + d)</td>
        <td>Доля всех правильных прогнозов. p → 1 — идеал.</td>
      </tr>
      <tr>
        <td class="name">H — точность попаданий</td>
        <td class="formula-cell">a / (a + b)</td>
        <td>Насколько оправданы «ДА»-прогнозы. H → 1 — нет ложных тревог.</td>
      </tr>
      <tr>
        <td class="name">τ — критерий Обухова (полнота)</td>
        <td class="formula-cell">a / (a + c)</td>
        <td>Доля пойманных событий. τ → 1 — нет пропусков.</td>
      </tr>
      <tr>
        <td class="name">v — критерий Хайдке</td>
        <td class="formula-cell">(a − b) / (a + b)</td>
        <td>Баланс попаданий и ложных тревог. v ∈ [−1, 1].</td>
      </tr>
      <tr>
        <td class="name">Q — критерий Пирси-Обухова</td>
        <td class="formula-cell">(a·d − b·c) / ((a+c)(b+d))</td>
        <td>Корреляция прогноза и факта. Q → 1 — идеал.</td>
      </tr>
      <tr>
        <td class="name">S — критерий Хайдке</td>
        <td class="formula-cell">p − v</td>
        <td>Компромисс между p и v. S → 1 — идеал.</td>
      </tr>
      <tr>
        <td class="name">A — критерий успешности</td>
        <td class="formula-cell">(a + d) / (a + b + c + d)</td>
        <td>Синоним p. Используется в некоторых источниках.</td>
      </tr>
      <tr>
        <td class="name">F1 — F-мера</td>
        <td class="formula-cell">2·a / (2a + b + c)</td>
        <td>Гармоническое среднее precision и recall. F1 → 1 — идеал.</td>
      </tr>
    </tbody>
  </table>
</div>

<div class="crit-block">
  <h2>🎯 Пороги интерпретации</h2>
  <table class="crit-table">
    <thead>
      <tr>
        <th>Критерий</th>
        <th>Плохо</th>
        <th>Средне</th>
        <th>Хорошо</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="name">p</td>
        <td>&lt; 0.7</td>
        <td>0.7 – 0.9</td>
        <td>&gt; 0.9</td>
      </tr>
      <tr>
        <td class="name">H</td>
        <td>&lt; 0.4</td>
        <td>0.4 – 0.6</td>
        <td>&gt; 0.6</td>
      </tr>
      <tr>
        <td class="name">τ</td>
        <td>&lt; 0.4</td>
        <td>0.4 – 0.6</td>
        <td>&gt; 0.6</td>
      </tr>
      <tr>
        <td class="name">v</td>
        <td>&lt; 0</td>
        <td>0 – 0.3</td>
        <td>&gt; 0.3</td>
      </tr>
      <tr>
        <td class="name">Q</td>
        <td>&lt; 0.2</td>
        <td>0.2 – 0.5</td>
        <td>&gt; 0.5</td>
      </tr>
      <tr>
        <td class="name">F1</td>
        <td>&lt; 0.3</td>
        <td>0.3 – 0.5</td>
        <td>&gt; 0.5</td>
      </tr>
    </tbody>
  </table>

  <p style="margin-top:16px;font-size:13px;">
    Пороги — ориентировочные, зависят от явления. Для редких явлений
    (гроза, туман) p легко завышается за счёт «правильных отрицаний»,
    поэтому смотреть надо в первую очередь на <b>H</b>, <b>τ</b> и <b>F1</b>.
  </p>
</div>

<div class="crit-block">
  <h2>⚖️ Сравнение моделей</h2>
  <p>
    Для сравнения моделей по матрицам переходи на страницу
    <a href="/compare-matrices/tushino" style="color:var(--accent);text-decoration:none;font-weight:600;">🔀 Сравнить модели по матрицам</a>
    — там для каждого явления строится матрица 2×2 по каждой модели
    и считается набор критериев.
  </p>
  <p>
    Для одной модели — страница
    <a href="/alt-verify/tushino" style="color:var(--accent);text-decoration:none;font-weight:600;">📋 Матрица альтернативных прогнозов</a>.
  </p>
</div>

""" + render_biblio_ref("matrices", "гл. 2–3") + """
""" + COMMON_JS +  render_legend("matrices") + """
</body>
</html>
"""




THEORY_INDICES_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Индексы неустойчивости — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .idx-block {
    margin: 24px 0;
    padding: 22px 24px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
  }
  .idx-block h2 {
    margin: 0 0 14px 0;
    font-size: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .idx-block p {
    color: var(--text-1);
    font-size: 14px;
    line-height: 1.7;
  }
  .formula {
    background: rgba(15, 21, 36, 0.6);
    padding: 14px 18px;
    border-radius: 10px;
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--accent);
    margin: 14px 0;
    overflow-x: auto;
    line-height: 1.8;
  }
  .idx-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin-top: 14px;
  }
  .idx-table th {
    text-align: left;
    padding: 10px 12px;
    color: var(--text-2);
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  .idx-table td {
    padding: 10px 12px;
    border-bottom: 1px solid rgba(120, 160, 255, 0.06);
    color: var(--text-1);
  }
  .idx-table tr:hover td { background: rgba(77, 171, 255, 0.05); }
  .idx-table td.name { color: var(--text-0); font-weight: 600; }
  .idx-table td.good { color: #00e5a0; }
  .idx-table td.warn { color: #ffb547; }
  .idx-table td.bad  { color: #ff5470; }
</style>
</head>
<body>

""" + render_header("theory") + """
<h1>⚡ Индексы неустойчивости</h1>
<div class="sub">LI · K-Index · CAPE · ΔT(850−500) · сдвиг ветра · интерпретация</div>

<div class="idx-block">
  <h2>⚡ K-Index (индекс Вайтинга)</h2>
  <p>
    Интегральный индекс конвективной неустойчивости. Учитывает
    вертикальный градиент температуры и влагосодержание в слое 850–500 гПа.
  </p>

  <div class="formula">
K = (T₈₅₀ − T₅₀₀) + Td₈₅₀ − (T₇₀₀ − Td₇₀₀)
  </div>

  <table class="idx-table">
    <thead>
      <tr>
        <th>Значение K</th>
        <th>Интерпретация</th>
        <th>Вероятность грозы</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">&lt; 15</td><td>Устойчиво</td><td class="good">0 %</td></tr>
      <tr><td class="name">15 – 20</td><td>Слабая неустойчивость</td><td class="good">до 20 %</td></tr>
      <tr><td class="name">20 – 25</td><td>Умеренная</td><td class="warn">20 – 40 %</td></tr>
      <tr><td class="name">25 – 30</td><td>Сильная</td><td class="warn">40 – 60 %</td></tr>
      <tr><td class="name">30 – 35</td><td>Очень сильная</td><td class="bad">60 – 80 %</td></tr>
      <tr><td class="name">&gt; 35</td><td>Экстремальная, грозы с градом</td><td class="bad">&gt; 80 %</td></tr>
    </tbody>
  </table>
</div>

<div class="idx-block">
  <h2>📈 Lifted Index (LI)</h2>
  <p>
    Разность температур между частицей, поднятой адиабатически до 500 гПа,
    и окружающей средой на том же уровне.
  </p>

  <div class="formula">
LI = T₅₀₀(окружение) − T₅₀₀(частица)
  </div>

  <table class="idx-table">
    <thead>
      <tr>
        <th>LI</th>
        <th>Интерпретация</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">&gt; +2</td><td class="good">Устойчиво</td></tr>
      <tr><td class="name">0 … +2</td><td class="good">Слабая неустойчивость</td></tr>
      <tr><td class="name">−2 … 0</td><td class="warn">Умеренная</td></tr>
      <tr><td class="name">−4 … −2</td><td class="warn">Сильная</td></tr>
      <tr><td class="name">−6 … −4</td><td class="bad">Очень сильная</td></tr>
      <tr><td class="name">&lt; −6</td><td class="bad">Экстремальная</td></tr>
    </tbody>
  </table>
</div>

<div class="idx-block">
  <h2>🔋 CAPE</h2>
  <p>
    Convective Available Potential Energy — доступная потенциальная
    энергия конвекции. Площадь на диаграмме T–ln p между кривой
    состояния частицы и кривой стратификации в слое положительной плавучести.
  </p>

  <div class="formula">
CAPE = g · ∫ (T_ч − T_окр) / T_окр · dz
  </div>

  <table class="idx-table">
    <thead>
      <tr>
        <th>CAPE, Дж/кг</th>
        <th>Интерпретация</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">&lt; 300</td><td class="good">Слабая конвекция</td></tr>
      <tr><td class="name">300 – 800</td><td class="good">Умеренная</td></tr>
      <tr><td class="name">800 – 1500</td><td class="warn">Сильная</td></tr>
      <tr><td class="name">1500 – 2500</td><td class="bad">Очень сильная</td></tr>
      <tr><td class="name">&gt; 2500</td><td class="bad">Экстремальная</td></tr>
    </tbody>
  </table>
</div>

<div class="idx-block">
  <h2>🌡 ΔT(850 − 500)</h2>
  <p>
    Грубый индикатор конвекции. Разность температур между 850 и 500 гПа.
  </p>

  <div class="formula">
ΔT = T₈₅₀ − T₅₀₀
  </div>

  <table class="idx-table">
    <thead>
      <tr>
        <th>ΔT, °C</th>
        <th>Интерпретация</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">&lt; 20</td><td class="good">Устойчиво</td></tr>
      <tr><td class="name">20 – 24</td><td class="good">Слабая</td></tr>
      <tr><td class="name">24 – 28</td><td class="warn">Умеренная</td></tr>
      <tr><td class="name">28 – 32</td><td class="bad">Сильная</td></tr>
      <tr><td class="name">&gt; 32</td><td class="bad">Экстремальная</td></tr>
    </tbody>
  </table>
</div>

<div class="idx-block">
  <h2>💨 Сдвиг ветра (850 → 300 гПа)</h2>
  <p>
    Векторная разность ветра между уровнями. Важен для организации
    конвекции: сильный сдвиг + высокая CAPE = угроза смерчей.
  </p>

  <div class="formula">
ΔV = √[(u₃₀₀ − u₈₅₀)² + (v₃₀₀ − v₈₅₀)²]
  </div>

  <table class="idx-table">
    <thead>
      <tr>
        <th>Сдвиг, м/с</th>
        <th>Интерпретация</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">&lt; 10</td><td>Слабый</td></tr>
      <tr><td class="name">10 – 15</td><td>Умеренный</td></tr>
      <tr><td class="name">15 – 20</td><td class="warn">Сильный — организация гроз</td></tr>
      <tr><td class="name">&gt; 20</td><td class="bad">Очень сильный — угроза смерчей</td></tr>
    </tbody>
  </table>
</div>

<div class="idx-block">
  <h2>📊 Комбинированная вероятность грозы</h2>
  <p>
    В проекте используется взвешенная сумма:
  </p>

  <div class="formula">
P = 0.25·P(K) + 0.40·P(LI) + 0.35·P(CAPE)
  </div>

  <p>
    где P(K), P(LI), P(CAPE) — вероятности по каждому индексу
    из таблиц выше. Веса подобраны эмпирически по Богаткину.
  </p>
</div>

<div class="idx-block">
  <h2>🌫 Туман (метод Кирюхина)</h2>
  <p>
    Модифицированный метод Б. В. Кирюхина. Проверяются 5 условий,
    каждое даёт +1 балл. Итоговый балл 0–5.
  </p>

  <table class="idx-table">
    <thead>
      <tr>
        <th>Условие</th>
        <th>Порог</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">Дефицит точки росы</td><td>ΔTd ≤ 2 °C</td></tr>
      <tr><td class="name">Ветер</td><td>0.5 – 3 м/с</td></tr>
      <tr><td class="name">Облачность</td><td>&lt; 30 %</td></tr>
      <tr><td class="name">Ночные часы</td><td>0 – 9 ч</td></tr>
      <tr><td class="name">Относительная влажность</td><td>RH ≥ 90 %</td></tr>
    </tbody>
  </table>

  <table class="idx-table" style="margin-top:16px;">
    <thead>
      <tr>
        <th>Балл</th>
        <th>Вероятность тумана</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="name">0 – 1</td><td class="good">Нет</td></tr>
      <tr><td class="name">2</td><td class="good">Слабая</td></tr>
      <tr><td class="name">3</td><td class="warn">Умеренная</td></tr>
      <tr><td class="name">4</td><td class="bad">Высокая</td></tr>
      <tr><td class="name">5</td><td class="bad">Очень высокая</td></tr>
    </tbody>
  </table>
</div>

""" + render_biblio_ref("aviation", "гл. 9–10") + """
""" + COMMON_JS +  render_legend("synoptic") + """
</body>
</html>
"""
