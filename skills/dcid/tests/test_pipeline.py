import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from dcid.models import CATEGORY_AI, CATEGORY_FINANCE, Article
from dcid.pipeline import _fetch_selected_full_text, _filter_recent_articles, _recency_cutoff_hours


class PipelineTests(unittest.TestCase):
    def test_fetch_selected_full_text_only_updates_selected_articles(self):
        selected_article = Article(
            "Selected story",
            "https://example.com/selected",
            "CNBC",
            3.0,
            summary="summary",
            category=CATEGORY_AI,
        )
        skipped_article = Article(
            "Skipped story",
            "https://example.com/skipped",
            "CNBC",
            3.0,
            summary="summary",
            category=CATEGORY_FINANCE,
        )
        selected = {CATEGORY_AI: [selected_article], CATEGORY_FINANCE: []}

        with (
            patch("dcid.pipeline.fetch_page_text", return_value="full text") as fetch_page,
            patch("sys.stderr"),
        ):
            _fetch_selected_full_text(selected, 10)

        fetch_page.assert_called_once_with("https://example.com/selected", 10)
        self.assertEqual(selected_article.content, "full text")
        self.assertEqual(skipped_article.content, "")

    def test_recency_cutoff_is_48_hours_on_weekdays(self):
        self.assertEqual(_recency_cutoff_hours(datetime(2026, 7, 6).date()), 48)

    def test_recency_cutoff_is_72_hours_on_weekends(self):
        self.assertEqual(_recency_cutoff_hours(datetime(2026, 7, 5).date()), 72)

    def test_filter_recent_articles_uses_weekday_cutoff(self):
        now = datetime(2026, 7, 6, 23, 59, tzinfo=timezone.utc)
        recent = Article(
            "Recent Fed story",
            "https://example.com/recent",
            "CNBC",
            3.0,
            published_at=now - timedelta(hours=47),
        )
        stale = Article(
            "Old Fed story",
            "https://example.com/stale",
            "CNBC",
            3.0,
            published_at=now - timedelta(hours=49),
        )

        articles = _filter_recent_articles([recent, stale], now)

        self.assertEqual([article.url for article in articles], ["https://example.com/recent"])

    def test_filter_recent_articles_uses_weekend_cutoff(self):
        now = datetime(2026, 7, 5, 23, 59, tzinfo=timezone.utc)
        weekend_recent = Article(
            "Weekend Fed story",
            "https://example.com/weekend-recent",
            "CNBC",
            3.0,
            published_at=now - timedelta(hours=71),
        )
        weekend_stale = Article(
            "Too old Fed story",
            "https://example.com/weekend-stale",
            "CNBC",
            3.0,
            published_at=now - timedelta(hours=73),
        )

        articles = _filter_recent_articles([weekend_recent, weekend_stale], now)

        self.assertEqual([article.url for article in articles], ["https://example.com/weekend-recent"])


if __name__ == "__main__":
    unittest.main()
