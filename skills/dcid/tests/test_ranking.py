import unittest
from datetime import datetime, timedelta, timezone

from dcid.models import CATEGORY_FINANCE, Article
from dcid.ranker import rank_articles, select_top_by_category


class RankingTests(unittest.TestCase):
    def test_rank_articles_prefers_recent_weighted_sources(self):
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        old_article = Article(
            title="Market update",
            url="https://example.com/old",
            source="Other",
            source_weight=1.0,
            published_at=now - timedelta(days=3),
            category=CATEGORY_FINANCE,
        )
        recent_article = Article(
            title="Fed market inflation update",
            url="https://example.com/recent",
            source="CNBC",
            source_weight=3.0,
            published_at=now - timedelta(hours=2),
            category=CATEGORY_FINANCE,
        )

        ranked = rank_articles([old_article, recent_article], now=now)

        self.assertEqual(ranked[0].url, recent_article.url)

    def test_select_top_by_category_limits_count(self):
        articles = [
            Article(
                title=f"Fed market story {index}",
                url=f"https://example.com/{index}",
                source="CNBC",
                source_weight=3.0,
                category=CATEGORY_FINANCE,
            )
            for index in range(7)
        ]

        selected = select_top_by_category(articles, 5, "all")

        self.assertEqual(len(selected[CATEGORY_FINANCE]), 5)


if __name__ == "__main__":
    unittest.main()

