# -*- coding: utf-8 -*-
"""Страница тестов."""

from ui.styles import (
    BASE_STYLE,
    COMMON_JS,
    render_header,
)
TESTS_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Тесты — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .block-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 14px; margin: 20px 0;
  }
  .block-card {
    padding: 20px 22px; border-radius: 16px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border); backdrop-filter: blur(14px);
    cursor: pointer; transition: all 0.25s;
    position: relative; overflow: hidden;
  }
  .block-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0; transition: opacity 0.3s;
  }
  .block-card:hover {
    transform: translateY(-3px); border-color: var(--border-hover);
    box-shadow: var(--card-shadow);
  }
  .block-card:hover::before { opacity: 1; }
  .block-card .icon { font-size: 28px; margin-bottom: 8px; display: block; }
  .block-card .title { font-size: 17px; font-weight: 700; margin-bottom: 6px; }
  .block-card .desc {
    color: var(--text-2); font-size: 12px; line-height: 1.5;
    margin-bottom: 10px;
  }
  .block-card .count {
    display: inline-block; padding: 3px 10px; border-radius: 6px;
    background: rgba(77,171,255,0.12); color: var(--accent);
    border: 1px solid rgba(77,171,255,0.25);
    font-size: 11px; font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
  }

  .test-area {
    margin: 20px 0; padding: 24px;
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 16px; backdrop-filter: blur(14px);
    min-height: 200px;
  }
  .progress-bar {
    height: 6px; background: rgba(120,160,255,0.1);
    border-radius: 3px; overflow: hidden; margin-bottom: 16px;
  }
  .progress-fill {
    height: 100%; background: linear-gradient(90deg, #4dabff, #7c5cff);
    transition: width 0.3s ease;
  }
  .progress-text {
    color: var(--text-2); font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 16px;
  }
  .question {
    font-size: 18px; font-weight: 600; line-height: 1.5;
    color: var(--text-0); margin-bottom: 18px;
  }
  .options { display: flex; flex-direction: column; gap: 8px; }
  .option {
    padding: 12px 16px; border-radius: 10px;
    background: rgba(15,21,36,0.4);
    border: 1px solid var(--border);
    cursor: pointer; transition: all 0.15s;
    font-size: 14px; color: var(--text-1);
    display: flex; align-items: flex-start; gap: 10px;
  }
  .option:hover { border-color: var(--border-hover); color: var(--text-0); }
  .option.selected {
    background: rgba(77,171,255,0.15);
    border-color: var(--accent); color: var(--text-0);
  }
  .option.correct {
    background: rgba(0,229,160,0.15);
    border-color: #00e5a0; color: #00e5a0;
  }
  .option.wrong {
    background: rgba(255,84,112,0.15);
    border-color: #ff5470; color: #ff5470;
  }
  .option .num {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700; color: var(--accent);
    flex-shrink: 0;
  }
  .option.correct .num { color: #00e5a0; }
  .option.wrong .num { color: #ff5470; }

  .explain-box {
    margin-top: 16px; padding: 14px 18px;
    background: rgba(77,171,255,0.08);
    border-left: 3px solid var(--accent);
    border-radius: 10px;
    font-size: 13px; color: var(--text-1); line-height: 1.6;
  }
  .explain-box .ref {
    display: block; margin-top: 8px;
    color: var(--text-2); font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
  }

  .btn-row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 20px; }
  .btn {
    padding: 12px 24px; border-radius: 10px; border: none;
    background: linear-gradient(135deg, #4dabff, #7c5cff);
    color: #fff; cursor: pointer; font-size: 14px; font-weight: 600;
    transition: opacity 0.2s;
  }
  .btn:hover { opacity: 0.9; }
  .btn:disabled {
    opacity: 0.4; cursor: not-allowed;
  }
  .btn.secondary {
    background: var(--bg-1); color: var(--text-0);
    border: 1px solid var(--border);
  }
  .btn.secondary:hover {
    background: var(--bg-2);
    border-color: var(--border-hover);
  }

  .result-box {
    text-align: center; padding: 30px 20px;
  }
  .result-score {
    font-size: 56px; font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 8px;
  }
  .result-score.good { color: #00e5a0; }
  .result-score.warn { color: #ffb547; }
  .result-score.bad  { color: #ff5470; }
  .result-text {
    color: var(--text-1); font-size: 16px;
    margin-bottom: 20px;
  }
  .result-detail {
    display: inline-block; padding: 8px 16px;
    background: rgba(15,21,36,0.4);
    border: 1px solid var(--border); border-radius: 10px;
    font-size: 13px; color: var(--text-2);
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 20px;
  }
</style>
</head>
<body>

""" + render_header("theory") + """
<h1>📝 Тесты по блокам</h1>
<div class="sub">Выбери блок — проверь знания. 20–37 вопросов, результат сразу, разбор ошибок.</div>

<div id="block-selection">
  <div class="block-grid">
    {% for key, block in tests.items() %}
    <div class="block-card" onclick="startTest('{{ key }}')">
      <span class="icon">{{ block.icon }}</span>
      <div class="title">{{ block.title }}</div>
      <div class="desc">{{ block.description }}</div>
      <span class="count">{{ block.questions | length }} вопросов</span>
    </div>
    {% endfor %}
  </div>
</div>

<div id="test-area" class="test-area" style="display:none;"></div>

<script>
var TESTS_DATA = {{ tests_json | safe }};
var currentBlock = null;
var currentQuestions = [];
var currentIndex = 0;
var currentScore = 0;
var selectedAnswer = null;
var answered = false;

function startTest(blockKey) {
  var block = TESTS_DATA[blockKey];
  if (!block) return;

  currentBlock = blockKey;
  currentQuestions = block.questions.slice();
  shuffle(currentQuestions);
  currentIndex = 0;
  currentScore = 0;
  selectedAnswer = null;
  answered = false;

  document.getElementById('block-selection').style.display = 'none';
  document.getElementById('test-area').style.display = 'block';
  renderQuestion();
}

function shuffle(arr) {
  for (var i = arr.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
  }
}

function renderQuestion() {
  var area = document.getElementById('test-area');
  if (currentIndex >= currentQuestions.length) {
    renderResult();
    return;
  }

  var q = currentQuestions[currentIndex];
  var total = currentQuestions.length;
  var progress = (currentIndex / total) * 100;

  var html = ''
    + '<div class="progress-bar"><div class="progress-fill" style="width:' + progress + '%"></div></div>'
    + '<div class="progress-text">Вопрос ' + (currentIndex + 1) + ' из ' + total
    + ' · правильных: ' + currentScore + '</div>'
    + '<div class="question">' + escapeHtml(q.q) + '</div>'
    + '<div class="options" id="options">';

  for (var i = 0; i < q.options.length; i++) {
    html += '<div class="option" data-idx="' + i + '" onclick="selectOption(' + i + ')">'
          + '<span class="num">' + (i + 1) + '.</span>'
          + '<span>' + escapeHtml(q.options[i]) + '</span>'
          + '</div>';
  }
  html += '</div>';

  html += '<div class="btn-row">'
        + '<button class="btn" id="confirm-btn" onclick="confirmAnswer()" disabled>Ответить</button>'
        + '<button class="btn secondary" onclick="exitTest()">Выйти</button>'
        + '</div>';

  area.innerHTML = html;

  selectedAnswer = null;
  answered = false;
}

function selectOption(idx) {
  if (answered) return;
  selectedAnswer = idx;
  var opts = document.querySelectorAll('.option');
  for (var i = 0; i < opts.length; i++) {
    opts[i].classList.toggle('selected', i === idx);
  }
  document.getElementById('confirm-btn').disabled = false;
}

function confirmAnswer() {
  if (answered || selectedAnswer === null) return;
  answered = true;

  var q = currentQuestions[currentIndex];
  var correct = q.correct;
  var opts = document.querySelectorAll('.option');

  for (var i = 0; i < opts.length; i++) {
    opts[i].classList.remove('selected');
    if (i === correct) opts[i].classList.add('correct');
    if (i === selectedAnswer && i !== correct) opts[i].classList.add('wrong');
  }

  if (selectedAnswer === correct) currentScore++;

  var area = document.getElementById('test-area');
  var explain = document.createElement('div');
  explain.className = 'explain-box';
  explain.innerHTML = escapeHtml(q.explain)
    + '<span class="ref">📖 ' + escapeHtml(q.ref || '—') + '</span>';
  area.insertBefore(explain, area.querySelector('.btn-row'));

  var btn = document.getElementById('confirm-btn');
  btn.textContent = (currentIndex + 1 < currentQuestions.length) ? 'Следующий →' : 'Показать результат';
  btn.disabled = false;
  btn.onclick = nextQuestion;
}

function nextQuestion() {
  currentIndex++;
  renderQuestion();
}

function renderResult() {
  var total = currentQuestions.length;
  var percent = Math.round((currentScore / total) * 100);
  var cls = percent >= 80 ? 'good' : percent >= 50 ? 'warn' : 'bad';
  var emoji = percent >= 80 ? '🎉' : percent >= 50 ? '👍' : '📚';
  var text = percent >= 80 ? 'Отличный результат!' : percent >= 50 ? 'Неплохо, но есть куда расти.' : 'Стоит повторить материал.';

  var block = TESTS_DATA[currentBlock];
  var area = document.getElementById('test-area');
  area.innerHTML = ''
    + '<div class="result-box">'
    + '  <div class="result-score ' + cls + '">' + percent + '%</div>'
    + '  <div class="result-text">' + emoji + ' ' + text + '</div>'
    + '  <div class="result-detail">' + currentScore + ' из ' + total + ' правильных</div>'
    + '  <div class="btn-row" style="justify-content:center;">'
    + '    <button class="btn" id="retry-btn">Пройти заново</button>'
    + '    <button class="btn secondary" id="exit-btn">К списку блоков</button>'
    + '  </div>'
    + '</div>';

  document.getElementById('retry-btn').onclick = function() {
    startTest(currentBlock);
  };
  document.getElementById('exit-btn').onclick = exitTest;
}

function escapeHtml(s) {
  if (s === null || s === undefined) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
</script>

""" + COMMON_JS +  """
</body>
</html>
"""
