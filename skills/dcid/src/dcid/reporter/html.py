from __future__ import annotations

from datetime import date
from html import escape

from dcid.models import CATEGORY_AI, CATEGORY_FINANCE, CATEGORY_OTHER, CATEGORY_TITLES, Article
from dcid.reporter.markdown import (
    VOCABULARY_TERMS,
    _display_direction,
    _display_relevance,
    _display_scope,
    _offline_article_analysis,
)


def render_html_report(
    report_date: date,
    selected: dict[str, list[Article]],
    macro_summary: str,
) -> str:
    body = [
        "<!doctype html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>Daily CNBC Intelligence Digest - {escape(report_date.isoformat())}</title>",
        f"<style>{_CSS}</style>",
        "</head>",
        "<body>",
        '<main class="page">',
        '<header class="hero">',
        "<p>Daily CNBC Intelligence Digest</p>",
        f"<h1>{escape(report_date.isoformat())} 市场情报精读</h1>",
        "<p>CNBC-only market, policy, macro, and stock-impact digest.</p>",
        "</header>",
        _render_toc(selected),
        _render_category(CATEGORY_AI, selected.get(CATEGORY_AI, [])),
        _render_category(CATEGORY_FINANCE, selected.get(CATEGORY_FINANCE, [])),
        _render_category(CATEGORY_OTHER, selected.get(CATEGORY_OTHER, [])),
        _render_vocabulary(),
        _render_macro_summary(macro_summary),
        "</main>",
        "</body>",
        "</html>",
    ]
    return "\n".join(body)


def render_raw_articles_html(report_date: date, articles: list[Article]) -> str:
    rows = "\n".join(_render_raw_article_row(article) for article in articles)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="zh-CN">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>Raw CNBC Articles - {escape(report_date.isoformat())}</title>",
            f"<style>{_CSS}</style>",
            "</head>",
            "<body>",
            '<main class="page">',
            '<header class="hero">',
            "<p>Raw CNBC Articles</p>",
            f"<h1>{escape(report_date.isoformat())} 抓取文章索引</h1>",
            f"<p>{len(articles)} unique articles before market-relevance filtering.</p>",
            "</header>",
            '<section class="section">',
            "<h2>All Raw Articles</h2>",
            '<div class="table-wrap">',
            "<table>",
            "<thead><tr><th>Title</th><th>Source</th><th>Category</th><th>Score</th><th>Summary</th></tr></thead>",
            f"<tbody>{rows}</tbody>",
            "</table>",
            "</div>",
            "</section>",
            "</main>",
            "</body>",
            "</html>",
        ]
    )


def _render_toc(selected: dict[str, list[Article]]) -> str:
    items: list[str] = []
    for category in (CATEGORY_AI, CATEGORY_FINANCE, CATEGORY_OTHER):
        articles = selected.get(category, [])
        items.append(
            f'<a href="#{escape(category)}"><strong>{escape(CATEGORY_TITLES[category])}</strong>'
            f"<span>{len(articles)} articles</span></a>"
        )
    return f'<nav class="toc">{"".join(items)}</nav>'


def _render_category(category: str, articles: list[Article]) -> str:
    cards = "\n".join(_render_article(article, index) for index, article in enumerate(articles, 1))
    if not cards:
        cards = '<p class="empty">No articles selected for this category today.</p>'
    return "\n".join(
        [
            f'<section class="section" id="{escape(category)}">',
            f"<h2>{escape(CATEGORY_TITLES[category])}</h2>",
            cards,
            "</section>",
        ]
    )


def _render_article(article: Article, index: int) -> str:
    analysis = article.analysis or _offline_article_analysis(article)
    return "\n".join(
        [
            '<article class="article-card">',
            f'<div class="article-index">Article {index}</div>',
            f"<h3>{escape(article.title)}</h3>",
            '<div class="meta">',
            f"<span>{escape(article.source)}</span>",
            f'<a href="{escape(article.url)}">Open article</a>',
            f"<span>Score {article.score:.2f}</span>",
            "</div>",
            _render_investment_lens(article),
            '<div class="analysis">',
            _markdown_to_html(analysis),
            "</div>",
            "</article>",
        ]
    )


def _render_investment_lens(article: Article) -> str:
    lens = article.investment_lens
    tickers = ", ".join(lens.tickers) if lens.tickers else "N/A"
    return "\n".join(
        [
            '<div class="investment-lens">',
            "<h4>Investment Lens (投资视角)</h4>",
            f'<span class="pill relevance-{escape(lens.relevance.lower())}">{escape(_display_relevance(lens.relevance))}</span>',
            f"<p><strong>News tilt, not trading advice (新闻倾向，不是买卖建议):</strong> {escape(_display_direction(lens.direction))}</p>",
            f"<p><strong>Scope (影响范围):</strong> {escape(_display_scope(lens.scope))}</p>",
            f"<p><strong>Tickers / ETFs (相关股票 / ETF):</strong> {escape(tickers)}</p>",
            f"<p><strong>Thesis (股票市场逻辑):</strong> {escape(lens.thesis)}</p>",
            "</div>",
        ]
    )


def _render_vocabulary() -> str:
    items = "\n".join(
        f"<li><strong>{escape(term)}</strong>: {escape(definition)}</li>"
        for term, definition in VOCABULARY_TERMS
    )
    return f'<section class="section"><h2>Key Vocabulary Today</h2><ul class="vocab">{items}</ul></section>'


def _render_macro_summary(macro_summary: str) -> str:
    return (
        '<section class="section"><h2>Macro Summary Insight</h2>'
        f'<div class="analysis">{_markdown_to_html(macro_summary)}</div></section>'
    )


def _render_raw_article_row(article: Article) -> str:
    title = f'<a href="{escape(article.url)}">{escape(article.title)}</a>'
    summary = escape(article.summary or article.content[:240])
    category = escape(article.category or "unclassified")
    return (
        "<tr>"
        f"<td>{title}</td>"
        f"<td>{escape(article.source)}</td>"
        f"<td>{category}</td>"
        f"<td>{article.score:.2f}</td>"
        f"<td>{summary}</td>"
        "</tr>"
    )


def _markdown_to_html(markdown: str) -> str:
    html_lines: list[str] = []
    in_list = False
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue
        if line.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h5>{escape(line[4:])}</h5>")
            continue
        if line.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h4>{escape(line[3:])}</h4>")
            continue
        if line.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3>{escape(line[2:])}</h3>")
            continue
        if line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{escape(line[2:])}</li>")
            continue
        if in_list:
            html_lines.append("</ul>")
            in_list = False
        html_lines.append(f"<p>{escape(line)}</p>")
    if in_list:
        html_lines.append("</ul>")
    return "\n".join(html_lines)


_CSS = """
:root {
  color-scheme: light;
  --bg: #f6f7f9;
  --panel: #ffffff;
  --text: #171717;
  --muted: #62646a;
  --line: #dedfe3;
  --accent: #155eef;
  --high: #0f7a3a;
  --medium: #9a5b00;
  --low: #777;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.55;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.page { max-width: 1100px; margin: 0 auto; padding: 32px 20px 64px; }
.hero { padding: 26px 0 18px; border-bottom: 1px solid var(--line); }
.hero p { margin: 0 0 8px; color: var(--muted); }
.hero h1 { margin: 0 0 8px; font-size: 34px; line-height: 1.15; }
.toc { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 22px 0; }
.toc a { display: block; padding: 14px; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; }
.toc span { display: block; color: var(--muted); font-size: 14px; }
.section { margin-top: 28px; }
.section h2 { margin: 0 0 14px; font-size: 24px; }
.article-card { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 20px; margin: 14px 0; }
.article-index { color: var(--muted); font-size: 14px; margin-bottom: 6px; }
.article-card h3 { margin: 0 0 10px; font-size: 22px; line-height: 1.25; }
.meta { display: flex; flex-wrap: wrap; gap: 12px; color: var(--muted); font-size: 14px; margin-bottom: 14px; }
.investment-lens { border-left: 4px solid var(--accent); background: #f2f5ff; padding: 12px 14px; border-radius: 6px; margin: 14px 0 18px; }
.investment-lens p { margin: 5px 0; }
.pill { display: inline-block; padding: 3px 9px; border-radius: 999px; color: #fff; font-size: 13px; font-weight: 700; margin-bottom: 6px; }
.relevance-high { background: var(--high); }
.relevance-medium { background: var(--medium); }
.relevance-low { background: var(--low); }
.analysis h3 { font-size: 20px; margin: 18px 0 10px; }
.analysis h4 { font-size: 18px; margin: 18px 0 8px; }
.analysis h5 { font-size: 16px; margin: 14px 0 6px; }
.analysis p { margin: 8px 0; }
.analysis ul, .vocab { padding-left: 22px; }
.empty { color: var(--muted); }
.table-wrap { overflow-x: auto; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; }
table { width: 100%; border-collapse: collapse; min-width: 780px; }
th, td { text-align: left; vertical-align: top; padding: 10px; border-bottom: 1px solid var(--line); }
th { background: #eef0f4; }
@media (max-width: 780px) {
  .toc { grid-template-columns: 1fr; }
  .hero h1 { font-size: 28px; }
}
"""
