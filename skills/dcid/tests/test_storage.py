import unittest
from datetime import date
from tempfile import TemporaryDirectory

from dcid.models import Article
from dcid.storage import deduplicate_articles, store_raw_articles_html, write_html_report


class StorageTests(unittest.TestCase):
    def test_deduplicate_articles_by_url_and_title(self):
        articles = [
            Article("Same title", "https://example.com/a", "CNBC", 3.0),
            Article("Same title", "https://example.com/b", "Reuters", 2.5),
            Article("Different title", "https://example.com/a", "CNBC", 3.0),
        ]

        unique = deduplicate_articles(articles)

        self.assertEqual(len(unique), 1)

    def test_write_html_outputs(self):
        with TemporaryDirectory() as tmpdir:
            from pathlib import Path

            base = Path(tmpdir)
            report_path = write_html_report("<html>report</html>", base / "reports", date(2026, 1, 1))
            raw_path = store_raw_articles_html("<html>raw</html>", base / "data", date(2026, 1, 1))

            self.assertTrue(report_path.exists())
            self.assertTrue(raw_path.exists())
            self.assertEqual(report_path.name, "2026-01-01-dcid.html")
            self.assertEqual(raw_path.name, "2026-01-01.html")


if __name__ == "__main__":
    unittest.main()
