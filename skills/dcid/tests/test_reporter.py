import unittest
from datetime import date

from dcid.models import CATEGORY_AI, CATEGORY_FINANCE, CATEGORY_OTHER, Article
from dcid.reporter import render_report


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
        self.assertIn("# Other News (Top 5)", report)
        self.assertIn("# Key Vocabulary Today", report)
        self.assertIn("# Macro Summary Insight", report)


if __name__ == "__main__":
    unittest.main()

