import unittest

from dcid.models import Article
from dcid.storage import deduplicate_articles


class StorageTests(unittest.TestCase):
    def test_deduplicate_articles_by_url_and_title(self):
        articles = [
            Article("Same title", "https://example.com/a", "CNBC", 3.0),
            Article("Same title", "https://example.com/b", "Reuters", 2.5),
            Article("Different title", "https://example.com/a", "CNBC", 3.0),
        ]

        unique = deduplicate_articles(articles)

        self.assertEqual(len(unique), 1)


if __name__ == "__main__":
    unittest.main()

