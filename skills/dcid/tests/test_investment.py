import unittest

from dcid.investment import evaluate_investment_lens
from dcid.models import Article


class InvestmentTests(unittest.TestCase):
    def test_high_relevance_policy_market_story_gets_tickers(self):
        article = Article(
            title="Stocks fall as Trump tariff plan raises inflation concerns",
            url="https://example.com/tariffs",
            source="CNBC Top News",
            source_weight=3.0,
            summary="Investors worried tariffs could lift prices and pressure Fed rate policy.",
        )

        lens = evaluate_investment_lens(article)

        self.assertEqual(lens.relevance, "High")
        self.assertIn("SPY", lens.tickers)
        self.assertEqual(lens.scope, "Market")

    def test_low_signal_story_is_marked_low_relevance(self):
        article = Article(
            title="Restaurant adds new brunch menu",
            url="https://example.com/brunch",
            source="CNBC Top News",
            source_weight=3.0,
        )

        lens = evaluate_investment_lens(article)

        self.assertEqual(lens.relevance, "Low")


if __name__ == "__main__":
    unittest.main()
