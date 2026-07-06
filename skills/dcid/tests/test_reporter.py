import unittest
from datetime import date

from dcid.llm.prompts import article_analysis_prompt
from dcid.models import CATEGORY_AI, CATEGORY_FINANCE, CATEGORY_OTHER, Article
from dcid.reporter import render_html_report, render_report


class ReporterTests(unittest.TestCase):
    def test_render_report_contains_required_sections(self):
        selected = {
            CATEGORY_AI: [Article("AI story", "https://example.com/ai", "CNBC", 3.0)],
            CATEGORY_FINANCE: [],
            CATEGORY_OTHER: [],
        }

        report = render_report(date(2026, 1, 1), selected, "Macro summary")

        self.assertIn("# Daily CNBC Intelligence Digest", report)
        self.assertIn("# AI / Tech (Top 5)", report)
        self.assertIn("# Finance / Macro (Top 5)", report)
        self.assertIn("# Policy / Market Impact (Top 5)", report)
        self.assertIn("# Key Vocabulary Today", report)
        self.assertIn("# Macro Summary Insight", report)
        self.assertIn("## Investment Lens", report)

    def test_render_html_report_contains_reader_sections(self):
        selected = {
            CATEGORY_AI: [Article("AI story", "https://example.com/ai", "CNBC", 3.0)],
            CATEGORY_FINANCE: [],
            CATEGORY_OTHER: [],
        }

        html = render_html_report(date(2026, 1, 1), selected, "Macro summary")

        self.assertIn("<!doctype html>", html)
        self.assertIn("Investment", html)
        self.assertIn("AI story", html)

    def test_article_prompt_uses_chinese_reading_note_format(self):
        article = Article("Market story", "https://example.com/story", "CNBC", 3.0)
        article.score = 7.4

        prompt = article_analysis_prompt(article)

        self.assertIn("这篇是在说", prompt)
        self.assertIn("逐段精读", prompt)
        self.assertIn("整篇新闻的市场逻辑", prompt)
        self.assertIn("Source: CNBC", prompt)
        self.assertIn("Score: 7.40", prompt)


if __name__ == "__main__":
    unittest.main()
