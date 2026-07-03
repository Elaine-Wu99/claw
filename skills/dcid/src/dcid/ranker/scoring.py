from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from dcid.classifier.rules import AI_KEYWORDS, FINANCE_KEYWORDS
from dcid.models import CATEGORIES, Article


def rank_articles(articles: list[Article], now: datetime | None = None) -> list[Article]:
    current_time = now or datetime.now(timezone.utc)
    for article in articles:
        article.score = (
            _recency_weight(article, current_time)
            + article.source_weight
            + _keyword_relevance(article)
            + _engagement_proxy(article)
        )
    return sorted(articles, key=lambda item: item.score, reverse=True)


def select_top_by_category(
    articles: list[Article],
    top_per_category: int,
    category_filter: str = "all",
) -> dict[str, list[Article]]:
    selected: dict[str, list[Article]] = defaultdict(list)
    for article in articles:
        if article.category is None:
            continue
        if category_filter != "all" and article.category != category_filter:
            continue
        if len(selected[article.category]) < top_per_category:
            selected[article.category].append(article)
    return {category: selected.get(category, []) for category in CATEGORIES}


def _recency_weight(article: Article, now: datetime) -> float:
    if article.published_at is None:
        return 0.75
    age_hours = max((now - article.published_at).total_seconds() / 3600, 0)
    if age_hours <= 6:
        return 3.0
    if age_hours <= 12:
        return 2.25
    if age_hours <= 24:
        return 1.5
    if age_hours <= 48:
        return 0.75
    return 0.25


def _keyword_relevance(article: Article) -> float:
    text = f"{article.title} {article.summary} {article.content}".lower()
    keywords = AI_KEYWORDS | FINANCE_KEYWORDS
    return min(2.0, sum(0.2 for keyword in keywords if keyword in text))


def _engagement_proxy(article: Article) -> float:
    title_bonus = min(len(article.title) / 120, 0.5)
    summary_bonus = 0.5 if len(article.summary) >= 120 else 0.0
    return title_bonus + summary_bonus

