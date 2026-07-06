from __future__ import annotations

from dcid.models import Article, InvestmentLens


HIGH_SIGNAL_KEYWORDS = {
    "earnings",
    "revenue",
    "profit",
    "margin",
    "guidance",
    "rate cut",
    "interest rate",
    "fed",
    "inflation",
    "tariff",
    "tax",
    "stocks",
    "shares",
    "yield",
    "treasury",
    "oil",
    "acquisition",
    "merger",
    "delay",
    "delayed",
}

MEDIUM_SIGNAL_KEYWORDS = {
    "budget",
    "defense",
    "demand",
    "supply",
    "china",
    "trade",
    "regulation",
    "data center",
    "semiconductor",
    "ai",
    "cloud",
    "investment",
}

BEARISH_KEYWORDS = {
    "delay",
    "delayed",
    "snag",
    "snags",
    "falls",
    "fall",
    "tumble",
    "tumbles",
    "pressure",
    "concerns",
    "weak",
    "tariff",
    "inflation",
    "attack",
}

BULLISH_KEYWORDS = {
    "raises",
    "raised",
    "rises",
    "rise",
    "pops",
    "gain",
    "gains",
    "rebound",
    "beats",
    "buyback",
    "acquisition",
    "demand",
    "orders",
}

TICKER_KEYWORDS = {
    "nvidia": ("NVDA", "SOXX"),
    "amd": ("AMD", "SOXX"),
    "meta": ("META",),
    "google": ("GOOGL",),
    "alphabet": ("GOOGL",),
    "apple": ("AAPL",),
    "microsoft": ("MSFT",),
    "amazon": ("AMZN",),
    "tesla": ("TSLA",),
    "lockheed": ("LMT", "ITA"),
    "defense": ("ITA", "LMT"),
    "oil": ("XLE", "USO"),
    "energy": ("XLE",),
    "bond": ("TLT", "IEF"),
    "treasury": ("TLT", "IEF"),
    "yield": ("TLT", "IEF"),
    "bank": ("KRE", "XLF"),
    "semiconductor": ("SOXX", "NVDA", "AMD"),
    "data center": ("NVDA", "AMD", "GOOGL", "MSFT"),
    "tariff": ("SPY", "QQQ", "XLI", "XRT"),
    "inflation": ("SPY", "QQQ", "TLT"),
    "fed": ("SPY", "QQQ", "TLT", "KRE"),
}


def evaluate_investment_lens(article: Article) -> InvestmentLens:
    text = _article_text(article)
    high_hits = _hits(text, HIGH_SIGNAL_KEYWORDS)
    medium_hits = _hits(text, MEDIUM_SIGNAL_KEYWORDS)
    relevance_score = high_hits * 2 + medium_hits
    relevance = _relevance_label(relevance_score)
    direction = _direction_label(text)
    scope = _scope_label(text)
    tickers = _related_tickers(text)
    thesis = _thesis(article, relevance, direction, scope, tickers)
    return InvestmentLens(
        relevance=relevance,
        direction=direction,
        scope=scope,
        tickers=tickers,
        thesis=thesis,
    )


def _article_text(article: Article) -> str:
    return f"{article.title} {article.summary} {article.content}".lower()


def _hits(text: str, keywords: set[str]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def _relevance_label(score: int) -> str:
    if score >= 5:
        return "High"
    if score >= 2:
        return "Medium"
    return "Low"


def _direction_label(text: str) -> str:
    bearish_hits = _hits(text, BEARISH_KEYWORDS)
    bullish_hits = _hits(text, BULLISH_KEYWORDS)
    if bullish_hits > bearish_hits:
        return "Bullish"
    if bearish_hits > bullish_hits:
        return "Bearish"
    if bullish_hits and bearish_hits:
        return "Mixed"
    return "Unclear"


def _scope_label(text: str) -> str:
    if any(keyword in text for keyword in ("fed", "inflation", "treasury", "yield", "gdp")):
        return "Market"
    if any(keyword in text for keyword in ("semiconductor", "defense", "oil", "energy", "bank")):
        return "Sector"
    if any(keyword in text for keyword in TICKER_KEYWORDS):
        return "Single stock"
    return "Sector"


def _related_tickers(text: str) -> tuple[str, ...]:
    tickers: list[str] = []
    for keyword, keyword_tickers in TICKER_KEYWORDS.items():
        if keyword not in text:
            continue
        for ticker in keyword_tickers:
            if ticker not in tickers:
                tickers.append(ticker)
    return tuple(tickers[:8])


def _thesis(
    article: Article,
    relevance: str,
    direction: str,
    scope: str,
    tickers: tuple[str, ...],
) -> str:
    target = ", ".join(tickers) if tickers else scope.lower()
    if relevance == "High":
        return f"High-signal story for {target}: connect the event to revenue, margins, rates, or valuation before acting."
    if relevance == "Medium":
        return f"Useful watch item for {target}: likely relevant, but confirm the market transmission path."
    return f"Low-conviction market signal for {target}: read for context, not as a standalone trading input."
