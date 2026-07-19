import unittest

from dcid.fetcher.rss import _parse_cnbc_listing_page, _parse_date
from dcid.models import Feed


class FetcherTests(unittest.TestCase):
    def test_parse_cnbc_listing_page_extracts_published_at(self):
        html = (
            '{"id":108,"title":"Latest market story","type":"cnbcnewsstory",'
            '"url":"https:\\u002F\\u002Fwww.cnbc.com\\u002F2026\\u002F07\\u002F18\\u002Flatest-market-story.html",'
            '"datePublished":"2026-07-18T23:01:01+0000",'
            '"__typename":"cnbcnewsstory"}'
        )
        feed = Feed("https://www.cnbc.com/latest/", "CNBC Latest", 3.2)

        articles = _parse_cnbc_listing_page(html, feed)

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, "Latest market story")
        self.assertEqual(
            articles[0].url,
            "https://www.cnbc.com/2026/07/18/latest-market-story.html",
        )
        self.assertEqual(articles[0].published_at.isoformat(), "2026-07-18T23:01:01+00:00")

    def test_parse_date_accepts_compact_timezone_offset(self):
        parsed = _parse_date("2026-07-18T23:01:01+0000")

        self.assertEqual(parsed.isoformat(), "2026-07-18T23:01:01+00:00")


if __name__ == "__main__":
    unittest.main()
