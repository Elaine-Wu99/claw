import unittest

from dcid.classifier import classify_article
from dcid.models import CATEGORY_AI, CATEGORY_FINANCE, Article


class ClassifierTests(unittest.TestCase):
    def test_ai_keyword_classification(self):
        article = Article(
            title="Nvidia shares rise as AI chip demand grows",
            url="https://example.com/ai",
            source="Test",
            source_weight=1.0,
        )

        result = classify_article(article)

        self.assertEqual(result.category, CATEGORY_AI)
        self.assertGreater(result.confidence, 0.5)

    def test_finance_keyword_classification(self):
        article = Article(
            title="Treasury yields fall after Fed inflation comments",
            url="https://example.com/finance",
            source="Test",
            source_weight=1.0,
        )

        result = classify_article(article)

        self.assertEqual(result.category, CATEGORY_FINANCE)
        self.assertGreater(result.confidence, 0.5)


if __name__ == "__main__":
    unittest.main()

