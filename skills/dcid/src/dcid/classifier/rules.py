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
    "analyst",
    "bank",
    "bond",
    "bonds",
    "budget",
    "central bank",
    "consumer",
    "credit",
    "cpi",
    "debt",
    "deficit",
    "demand",
    "dollar",
    "dow",
    "earnings",
    "economy",
    "equity",
    "fed",
    "federal reserve",
    "fiscal",
    "forecast",
    "gdp",
    "guidance",
    "housing",
    "inflation",
    "interest rate",
    "investor",
    "investors",
    "jobs",
    "market",
    "markets",
    "oil",
    "payrolls",
    "ppi",
    "prices",
    "profit",
    "rate cut",
    "rates",
    "recession",
    "revenue",
    "s&p 500",
    "shares",
    "spending",
    "stocks",
    "treasury",
    "treasuries",
    "treasurys",
    "yield",
    "yields",
}

POLICY_MARKET_KEYWORDS = {
    "antitrust",
    "china",
    "congress",
    "export",
    "import",
    "regulation",
    "sanction",
    "sanctions",
    "subsidy",
    "tariff",
    "tariffs",
    "tax",
    "taxes",
    "trade",
    "white house",
}

EXCLUDED_TOPIC_KEYWORDS = {
    "balogun",
    "celebrity",
    "coach",
    "fifa",
    "game suspension",
    "golf",
    "lacrosse",
    "movie",
    "nba",
    "nfl",
    "nhl",
    "olympic",
    "player",
    "red card",
    "soccer",
    "tennis",
    "travel",
    "world cup",
}

MARKET_RELEVANCE_KEYWORDS = FINANCE_KEYWORDS | POLICY_MARKET_KEYWORDS | {
    "acquisition",
    "ai boom",
    "buyback",
    "chipmaker",
    "chipmakers",
    "data center",
    "deal",
    "ipo",
    "merger",
    "nvidia",
    "semiconductor",
    "semiconductors",
    "stock market",
    "valuation",
}


def classify_article(article: Article) -> Classification:
    if article.category in {CATEGORY_AI, CATEGORY_FINANCE, CATEGORY_OTHER}:
        return Classification(article.category, 0.85, "feed default")

    text = _article_text(article)
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


def is_market_relevant(article: Article) -> bool:
    text = _article_text(article)
    market_hits = _keyword_hits(text, MARKET_RELEVANCE_KEYWORDS)
    if market_hits == 0:
        return False
    excluded_hits = _keyword_hits(text, EXCLUDED_TOPIC_KEYWORDS)
    if excluded_hits and market_hits < 2:
        return False
    return True


def _article_text(article: Article) -> str:
    return f"{article.title} {article.summary} {article.content}".lower()


def _keyword_hits(text: str, keywords: set[str]) -> int:
    return sum(1 for keyword in keywords if keyword in text)
