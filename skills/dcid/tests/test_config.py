import unittest
from pathlib import Path

from dcid.config import DEFAULT_OUTPUT_DIR, AppConfig, default_feeds


class ConfigTests(unittest.TestCase):
    def test_default_feeds_are_cnbc_only(self):
        feeds = default_feeds()

        self.assertTrue(feeds)
        self.assertTrue(all(feed.source.startswith("CNBC") for feed in feeds))

    def test_google_feeds_are_opt_in(self):
        feeds = default_feeds(include_google=True)

        self.assertTrue(any(feed.source.startswith("Google News") for feed in feeds))

    def test_default_output_dir_is_desktop_news_report(self):
        config = AppConfig(feeds=default_feeds())

        self.assertEqual(config.reports_dir, DEFAULT_OUTPUT_DIR)
        self.assertEqual(config.data_dir, DEFAULT_OUTPUT_DIR)
        self.assertEqual(DEFAULT_OUTPUT_DIR, Path("/Users/qiaowenwu/Desktop/新闻report"))


if __name__ == "__main__":
    unittest.main()
