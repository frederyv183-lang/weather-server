# -*- coding: utf-8 -*-
"""Страница синоптических карт v5."""

from ui.styles import BASE_STYLE, COMMON_JS, render_header


SYNOPTIC_MAPS_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Синоптические карты — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .synoptic-layout {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 16px;
    align-items: start;
  }
  @media (max-width: 1100px) {
    .synoptic-layout { grid-template-columns: 1fr; }
  }

  .viewer {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .image-wrap {
    background: #fafaf5;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 8px;
    min-height: 600px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: auto;
  }
  .image-wrap img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    display: block;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    cursor: zoom-in;
  }
  .image-wrap .placeholder {
    color: var(--text-2);
    font-size: 14px;
    text-align: center;
    padding: 40px;
  }
  .image-wrap .placeholder b {
    color: var(--text-0);
    font-size: 16px;
    display: block;
    margin-bottom: 8px;
  }
  .image-wrap .spinner {
    width: 40px; height: 40px;
    border: 4px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 16px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .panel {
    padding: 16px 18px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
    max-height: 90vh;
    overflow-y: auto;
  }
  .panel h3 {
    margin: 14px 0 8px 0;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-2);
    font-weight: 700;
  }
  .panel h3:first-child { margin-top: 0; }

  .panel select {
    width: 100%;
    padding: 8px 10px;
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-0);
    font-size: 13px;
  }

  .level-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .level-btn {
    padding: 8px 12px;
    text-align: left;
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-1);
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s;
    font-family: 'JetBrains Mono', monospace;
  }
  .level-btn:hover { border-color: var(--border-hover); }
  .level-btn.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25),
                                       rgba(124,92,255,0.25));
    border-color: var(--accent);
    color: var(--text-0);
    font-weight: 600;
  }

  .check-list label {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    color: var(--text-1);
    font-size: 13px;
    cursor: pointer;
  }
  .check-list label:hover { color: var(--text-0); }

  .btn-row {
    display: flex;
    gap: 8px;
    margin-top: 16px;
  }
  .btn-row button {
    flex: 1;
    padding: 10px 14px;
    border-radius: 10px;
    border: none;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
  }
  .btn-row button:hover { opacity: 0.9; }
  .btn-row button:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-row button.secondary {
    background: var(--bg-1);
    color: var(--text-0);
    border: 1px solid var(--border);
  }
  #status {
    margin-top: 10px;
    font-size: 11px;
    color: var(--text-2);
    font-family: 'JetBrains Mono', monospace;
    min-height: 16px;
    word-break: break-word;
  }

  .archive-list {
    list-style: none; padding: 0; margin: 6px 0 0 0;
    max-height: 240px; overflow-y: auto;
  }
  .archive-list li {
    padding: 8px 10px; margin: 4px 0;
    background: var(--bg-1); border: 1px solid var(--border);
    border-radius: 8px; font-size: 12px; cursor: pointer;
    font-family: 'JetBrains Mono', monospace;
    transition: all 0.15s;
    display: flex; justify-content: space-between;
    gap: 8px;
  }
  .archive-list li:hover {
    border-color: var(--border-hover); background: var(--bg-2);
  }
  .archive-list li.active {
    background: linear-gradient(135deg, rgba(77,171,255,0.25),
                                       rgba(124,92,255,0.25));
    border-color: var(--accent);
    color: var(--text-0);
    font-weight: 600;
  }
  .archive-list .meta {
    color: var(--text-2); font-size: 11px;
  }
  .archive-list li.active .meta { color: var(--text-1); }

  .hint {
    margin-top: 8px;
    font-size: 10px;
    color: var(--text-2);
    font-family: 'JetBrains Mono', monospace;
  }
</style>
</head>
<body>

""" + render_header("synoptic_maps") + """
<h1>🌐 Синоптические карты</h1>
<div class="sub">ЕТР + Европа · изогипсы / изотермы / изотахи · архив 3 дня</div>

<div class="synoptic-layout">

  <div class="panel">
    <h3>Уровень</h3>
    <div class="level-list" id="level-list">
      {% for key, info in levels.items() %}
        <div class="level-btn {% if key == 500 %}active{% endif %}"
             data-level="{{ key }}">{{ info.name }}</div>
      {% endfor %}
    </div>

    <h3>Относительная топография</h3>
    <div class="level-list">
      <div class="level-btn ot-btn" data-ot="ot_500_1000">{{ ot.name }}</div>
    </div>

    <h3>Срок прогноза</h3>
    <select id="step-select">
      {% for step in steps %}
        <option value="{{ step }}" {% if step == 24 %}selected{% endif %}>
          +{{ step }} ч
        </option>
      {% endfor %}
    </select>

    <h3>Слои</h3>
    <div class="check-list">
      <label><input type="checkbox" id="cb-isohypse" checked> Изогипсы</label>
      <label><input type="checkbox" id="cb-isotherm" checked> Изотермы</label>
      <label><input type="checkbox" id="cb-isotach"  checked> Изотахи</label>
    </div>

    <div class="btn-row">
      <button onclick="updateImage()">Показать</button>
    </div>
    <div class="btn-row" style="margin-top:8px;">
      <button onclick="generateAll()" id="btn-generate"
              class="secondary">⚙ Сгенерировать</button>
    </div>
    <div id="status">Готов к работе</div>
    <div class="hint">💡 Клик по карте → открыть PNG в новой вкладке</div>

    <h3 style="margin-top:20px;">📂 Архив прогонов</h3>
    <ul class="archive-list" id="archive-list">
      <li style="justify-content:center;color:var(--text-2);">Загрузка...</li>
    </ul>
  </div>

  <div class="viewer">
    <div class="image-wrap" id="image-wrap">
      <div class="placeholder">
        <b>Карта ещё не сгенерирована</b>
        Нажмите «⚙ Сгенерировать» в панели слева.
      </div>
    </div>
  </div>

</div>

<script>
var currentLevel = "500";
var currentOt = null;
var mode = "at";
var currentStamp = null;

// --- Уровни АТ ---
document.querySelectorAll('.level-btn:not(.ot-btn)').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.level-btn').forEach(
      function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    currentLevel = btn.dataset.level;
    currentOt = null;
    mode = "at";
    updateImage();
  });
});

// --- ОТ ---
document.querySelectorAll('.ot-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.level-btn').forEach(
      function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    currentOt = btn.dataset.ot;
    mode = "ot";
    updateImage();
  });
});

// --- Автоперерисовка ---
['step-select', 'cb-isohypse', 'cb-isotherm', 'cb-isotach'].forEach(
  function(id) {
    document.getElementById(id).addEventListener('change', updateImage);
  });

function getSelectedOverlays() {
  var o = [];
  if (document.getElementById('cb-isohypse').checked) o.push('h');
  if (document.getElementById('cb-isotherm').checked) o.push('t');
  if (document.getElementById('cb-isotach').checked)  o.push('w');
  return o;
}

function updateImage() {
  var step = document.getElementById('step-select').value;
  var h = document.getElementById('cb-isohypse').checked;
  var t = document.getElementById('cb-isotherm').checked;
  var w = document.getElementById('cb-isotach').checked;
  var status = document.getElementById('status');
  status.textContent = 'Поиск...';

  var levelParam = (mode === "ot") ? "ot_500_1000" : currentLevel;

  fetch('/api/synoptic-maps/find', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      level: levelParam,
      step: parseInt(step),
      region: 'etr',
      stamp: currentStamp,
      show_isohypse: h, show_isotherm: t, show_isotach: w,
    }),
  })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.file) {
        showImage('/static/synoptic_maps/archive/' + data.file);
        status.textContent = '✓ ' + data.file.split('/').pop();
        // Запомним stamp из имени файла
        var m = data.file.match(/gfs_(\\d{10})_/);
        if (m) {
          currentStamp = m[1];
          markActiveRun(m[1]);
          // Сохраним в URL
          var url = new URL(window.location);
          url.searchParams.set('stamp', m[1]);
          history.replaceState(null, '', url);
        }
      } else {
        showPlaceholder('Нет карты для этих фильтров',
          'Нажмите «Сгенерировать» или выберите другой прогон.');
        status.textContent = 'Нет данных.';
      }
    })
    .catch(function(e) { status.textContent = '✗ ' + e.message; });
}

function showImage(url) {
  var wrap = document.getElementById('image-wrap');
  var img = document.createElement('img');
  img.src = url;
  img.alt = 'Синоптическая карта';
  img.title = 'Клик — открыть в новой вкладке';
  img.style.cursor = 'zoom-in';
  img.onclick = function() { window.open(url, '_blank'); };
  wrap.innerHTML = '';
  wrap.appendChild(img);
}

function showPlaceholder(title, sub) {
  document.getElementById('image-wrap').innerHTML =
    '<div class="placeholder"><b>' + title + '</b>' + sub + '</div>';
}

function showSpinner(text) {
  document.getElementById('image-wrap').innerHTML =
    '<div class="placeholder"><div class="spinner"></div>' +
    '<b>Генерация...</b>' + text + '</div>';
}

function generateAll() {
  var h = document.getElementById('cb-isohypse').checked;
  var t = document.getElementById('cb-isotherm').checked;
  var w = document.getElementById('cb-isotach').checked;
  var btn = document.getElementById('btn-generate');
  var status = document.getElementById('status');
  btn.disabled = true;
  showSpinner('Все уровни × 5 сроков × 1 регион.');
  status.textContent = '⏳ Генерация... (5–15 минут)';

  fetch('/api/synoptic-maps/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      levels: null,
      steps: [0, 12, 24, 48, 72],
      regions: ['etr'],
      show_isohypse: h, show_isotherm: t, show_isotach: w,
      include_ot: true,
    }),
  })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      btn.disabled = false;
      if (data.status === 'ok') {
        status.textContent = '✓ Готово: ' + data.count + ' карт';
        loadArchive();
        setTimeout(updateImage, 500);
      } else {
        status.textContent = '✗ ' + (data.message || '?');
        showPlaceholder('Ошибка генерации', data.message || '');
      }
    })
    .catch(function(e) {
      btn.disabled = false;
      status.textContent = '✗ ' + e.message;
    });
}

// --- Архив ---
function loadArchive() {
  fetch('/api/synoptic-maps/runs')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var list = document.getElementById('archive-list');
      var runs = data.runs || [];
      if (!runs.length) {
        list.innerHTML = '<li style="text-align:center;color:var(--text-2);">' +
          'Архив пуст</li>';
        return;
      }
      var html = '';
      runs.slice(0, 20).forEach(function(run) {
        var yyyy = run.stamp.substr(0, 4);
        var mm   = run.stamp.substr(4, 2);
        var dd   = run.stamp.substr(6, 2);
        var hh   = run.stamp.substr(8, 2);
        var label = dd + '.' + mm + ' ' + hh + ':00 UTC';
        html += '<li data-stamp="' + run.stamp + '">' +
                '<span>' + label + '</span>' +
                '<span class="meta">' + run.count + ' шт</span></li>';
      });
      list.innerHTML = html;

      list.querySelectorAll('li[data-stamp]').forEach(function(li) {
        li.addEventListener('click', function() {
          currentStamp = li.dataset.stamp;
          markActiveRun(currentStamp);
          // Обновим URL
          var url = new URL(window.location);
          url.searchParams.set('stamp', currentStamp);
          history.replaceState(null, '', url);
          // Загрузим карту из этого прогона
          updateImage();
        });
      });

      // Проверим URL-параметр
      var urlStamp = new URL(window.location).searchParams.get('stamp');
      if (urlStamp) {
        currentStamp = urlStamp;
        markActiveRun(urlStamp);
      }
    });
}

function markActiveRun(stamp) {
  document.querySelectorAll('.archive-list li').forEach(function(li) {
    li.classList.toggle('active', li.dataset.stamp === stamp);
  });
}

// Автозагрузка
loadArchive();
setTimeout(updateImage, 300);
</script>

""" + COMMON_JS + """
</body>
</html>
"""
