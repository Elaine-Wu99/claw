from __future__ import annotations

from datetime import date

from dcid.models import CATEGORY_AI, CATEGORY_FINANCE, CATEGORY_OTHER, CATEGORY_TITLES, Article


VOCABULARY_TERMS = [
    ("benchmark", "A standard reference point used to compare market performance."),
    ("yield", "The return earned on a bond, often moving opposite to bond prices."),
    ("rate cut", "A central bank reduction in policy interest rates."),
    ("inflation", "A broad rise in prices that reduces purchasing power."),
    ("earnings", "Company profit results reported quarterly or annually."),
    ("guidance", "A company's forecast for future performance."),
    ("rally", "A sustained rise in asset prices."),
    ("tumble", "A sharp decline in price or value."),
    ("soft landing", "A slowdown that avoids recession while cooling inflation."),
    ("risk appetite", "Investor willingness to buy higher-risk assets."),
    ("Treasury", "U.S. government debt securities watched as rate benchmarks."),
    ("valuation", "The market price of an asset relative to fundamentals."),
    ("outlook", "Forward-looking expectations for an economy, company, or market."),
    ("volatility", "The scale and speed of price movement."),
    ("pre-market", "Trading activity before regular U.S. market hours."),
]


def render_report(
    report_date: date,
    selected: dict[str, list[Article]],
    macro_summary: str,
) -> str:
    sections = [
        "# Daily CNBC Intelligence Digest",
        f"Date: {report_date.isoformat()}",
        "",
        "---",
        "",
        _render_category(CATEGORY_AI, selected.get(CATEGORY_AI, [])),
        "",
        "---",
        "",
        _render_category(CATEGORY_FINANCE, selected.get(CATEGORY_FINANCE, [])),
        "",
        "---",
        "",
        _render_category(CATEGORY_OTHER, selected.get(CATEGORY_OTHER, [])),
        "",
        "---",
        "",
        "# Key Vocabulary Today",
        "",
        *[f"- {term}: {definition}" for term, definition in VOCABULARY_TERMS],
        "",
        "---",
        "",
        "# Macro Summary Insight",
        "",
        macro_summary,
        "",
    ]
    return "\n".join(sections)


def _render_category(category: str, articles: list[Article]) -> str:
    lines = [f"# {CATEGORY_TITLES[category]} (Top 5)", ""]
    if not articles:
        lines.append("_No articles selected for this category today._")
        return "\n".join(lines)
    for index, article in enumerate(articles, start=1):
        lines.extend(
            [
                f"[Article {index}]",
                "",
                article.analysis or _offline_article_analysis(article),
                "",
            ]
        )
    return "\n".join(lines).strip()


def _offline_article_analysis(article: Article) -> str:
    excerpt = article.summary or article.content or "No article summary was available from the feed."
    return f"""# {article.title}

Source: {article.source}
URL: {article.url}
Score: {article.score:.2f}

## Chinese Translation
Offline analysis mode is enabled, so no natural Chinese translation was generated.

## Sentence-by-Sentence Breakdown
- Feed excerpt: {excerpt}

## Key Vocabulary
- market: A broad term for tradable assets or investor activity.

## Macro Context
The available feed text is preserved above. Run with `OPENAI_API_KEY` for grounded macro interpretation.

## CNBC Writing Style Insight
Offline mode does not infer newsroom style beyond the supplied text."""

