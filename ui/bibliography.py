# -*- coding: utf-8 -*-
"""Библиография."""

from ui.styles import (
    BASE_STYLE,
    COMMON_JS,
    render_header,
    render_legend,
)
BIBLIOGRAPHY_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Библиография — weather-msk</title>
""" + BASE_STYLE + """
<style>
  .toc {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 20px 0 28px 0;
    padding: 14px 18px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    backdrop-filter: blur(14px);
  }
  .toc a {
    padding: 6px 12px;
    border-radius: 8px;
    text-decoration: none;
    font-size: 13px;
    font-weight: 500;
    background: rgba(77, 171, 255, 0.08);
    border: 1px solid rgba(77, 171, 255, 0.2);
    color: var(--accent);
    transition: all 0.2s;
  }
  .toc a:hover {
    background: rgba(77, 171, 255, 0.15);
    border-color: var(--border-hover);
  }

  .biblio-section {
    margin: 32px 0;
    padding: 22px 24px;
    background: linear-gradient(135deg, var(--card-bg), var(--card-bg-2));
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
    scroll-margin-top: 20px;
  }
  .biblio-section h2 {
    margin: 0 0 18px 0;
    font-size: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, var(--text-0), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .biblio-section h2 .icon {
    -webkit-text-fill-color: initial;
    color: var(--accent);
  }

  .biblio-item {
    margin: 14px 0;
    padding: 16px 18px;
    background: rgba(15, 21, 36, 0.5);
    border: 1px solid var(--border);
    border-radius: 12px;
    transition: all 0.2s;
  }
  .biblio-item:hover {
    border-color: var(--border-hover);
  }
  .biblio-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-0);
    margin-bottom: 4px;
    line-height: 1.4;
  }
  .biblio-authors {
    color: var(--text-1);
    font-size: 13px;
    margin-bottom: 4px;
  }
  .biblio-source {
    color: var(--text-2);
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 10px;
  }
  .biblio-note {
    color: var(--text-1);
    font-size: 13px;
    line-height: 1.6;
    padding-top: 10px;
    border-top: 1px solid rgba(120, 160, 255, 0.08);
  }
  .biblio-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 10px;
  }
  .biblio-tag {
    padding: 3px 9px;
    font-size: 11px;
    border-radius: 6px;
    background: rgba(77, 171, 255, 0.1);
    border: 1px solid rgba(77, 171, 255, 0.25);
    color: var(--accent);
    font-family: 'JetBrains Mono', monospace;
  }
</style>
</head>
<body>
""" + render_header("theory") + """
<h1>📖 Библиография</h1>
<div class="sub">Источники, использованные в разделах сайта</div>

<div class="toc">
  {% for key, topic in bibliography.items() %}
    <a href="#{{ key }}">{{ topic.icon }} {{ topic.title }}</a>
  {% endfor %}
</div>

{% for key, topic in bibliography.items() %}
<div class="biblio-section" id="{{ key }}">
  <h2><span class="icon">{{ topic.icon }}</span>{{ topic.title }}</h2>

  {% for item in topic.sources %}
  <div class="biblio-item">
    <div class="biblio-title">«{{ item.title }}»{% if item.edition %} — {{ item.edition }}{% endif %}</div>
    <div class="biblio-authors">{{ item.authors }}</div>
    <div class="biblio-source">
      {{ item.source }}{% if item.year %}, {{ item.year }}{% endif %}{% if item.pages %}. {{ item.pages }}{% endif %}
    </div>
    {% if item.note %}
      <div class="biblio-note">{{ item.note }}</div>
    {% endif %}
    {% if item.tags %}
      <div class="biblio-tags">
        {% for tag in item.tags %}
          <span class="biblio-tag">{{ tag }}</span>
        {% endfor %}
      </div>
    {% endif %}
  </div>
  {% endfor %}
</div>
{% endfor %}

""" + COMMON_JS +  render_legend("bibliography") + """
</body>
</html>
"""
