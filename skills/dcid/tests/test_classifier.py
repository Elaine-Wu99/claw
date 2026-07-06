import unittest

from dcid.classifier import classify_article
from dcid.classifier.llm import _parse_classifier_response
from dcid.classifier.rules import is_market_relevant
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

    def test_market_relevance_excludes_sports_politics(self):
        article = Article(
            title="Trump asked FIFA to review Balogun's World Cup game suspension",
            url="https://example.com/sports",
            source="CNBC Top News",
            source_weight=3.0,
            summary="Folarin Balogun was cleared to play in the World Cup after a red card.",
        )

        self.assertFalse(is_market_relevant(article))

    def test_market_relevance_keeps_policy_market_impact(self):
        article = Article(
            title="Stocks fall as Trump tariff plan raises inflation concerns",
            url="https://example.com/tariffs",
            source="CNBC Top News",
            source_weight=3.0,
            summary="Investors worried tariffs could lift prices and pressure Fed rate policy.",
        )

        self.assertTrue(is_market_relevant(article))

    def test_llm_classifier_non_json_response_raises_runtime_error(self):
        body = {"output_text": "finance"}

        with self.assertRaises(RuntimeError):
            _parse_classifier_response(body)

    def test_llm_classifier_parses_fenced_json_response(self):
        body = {"output_text": '```json\n{"category": "finance", "confidence": 0.85}\n```'}

        parsed = _parse_classifier_response(body)

        self.assertEqual(parsed["category"], "finance")
        self.assertEqual(parsed["confidence"], 0.85)


if __name__ == "__main__":
    unittest.main()
