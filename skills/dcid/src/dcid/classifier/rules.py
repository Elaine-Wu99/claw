from __future__ import annotations

from dcid.models import CATEGORY_AI, CATEGORY_FINANCE, CATEGORY_OTHER, Article, Classification


AI_KEYWORDS = {
    "ai",
    "artificial intelligence",
    "openai",
    "nvidia",
    "gpu",
    "chip",
    "chips",
    "semiconductor",
    "llm",
    "model",
    "datacenter",
    "data center",
    "cloud",
}

FINANCE_KEYWORDS = {
    "fed",
    "federal reserve",
    "inflation",
    "cpi",
    "ppi",
    "rates",
    "rate cut",
    "yield",
    "treasury",
    "oil",
    "jobs",
    "payrolls",
    "earnings",
    "stocks",
    "market",
    "markets",
    "recession",
    "gdp",
}


def classify_article(article: Article) -> Classification:
    if article.category in {CATEGORY_AI, CATEGORY_FINANCE, CATEGORY_OTHER}:
        return Classification(article.category, 0.85, "feed default")

    text = f"{article.title} {article.summary} {article.content}".lower()
    ai_hits = _keyword_hits(text, AI_KEYWORDS)
    finance_hits = _keyword_hits(text, FINANCE_KEYWORDS)

    if ai_hits > finance_hits and ai_hits > 0:
        return Classification(CATEGORY_AI, min(0.95, 0.55 + ai_hits * 0.1), "rule keywords")
    if finance_hits > 0:
        return Classification(
            CATEGORY_FINANCE,
            min(0.95, 0.55 + finance_hits * 0.1),
            "rule keywords",
        )
    return Classification(CATEGORY_OTHER, 0.6, "default")


def _keyword_hits(text: str, keywords: set[str]) -> int:
    return sum(1 for keyword in keywords if keyword in text)

