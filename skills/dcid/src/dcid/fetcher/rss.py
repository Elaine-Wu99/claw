from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from dcid.config import AppConfig
from dcid.fetcher.content import fetch_page_text
from dcid.models import Article, Feed


def fetch_articles(config: AppConfig) -> list[Article]:
    articles: list[Article] = []
    for feed in config.feeds:
        try:
            feed_articles = fetch_feed(feed, config.request_timeout_seconds)
        except Exception as exc:
            print(f"warning: failed to fetch {feed.source}: {exc}")
            continue
        for article in feed_articles[: config.max_articles_per_feed]:
            if not config.fetch_full_text:
                articles.append(article)
                continue
            try:
                article.content = fetch_page_text(article.url, config.request_timeout_seconds)
            except Exception:
                article.content = article.summary
            articles.append(article)
    return articles


def fetch_feed(feed: Feed, timeout_seconds: int) -> list[Article]:
    request = Request(feed.url, headers={"User-Agent": "DCID/0.1 (+https://github.com/)"})
    with urlopen(request, timeout=timeout_seconds) as response:
        raw_xml = response.read(2_000_000)
    root = ElementTree.fromstring(raw_xml)
    if root.tag.endswith("feed"):
        return _parse_atom(root, feed)
    return _parse_rss(root, feed)


def _parse_rss(root: ElementTree.Element, feed: Feed) -> list[Article]:
    items = root.findall(".//item")
    articles: list[Article] = []
    for item in items:
        title = _text(item, "title")
        url = _text(item, "link")
        if not title or not url:
            continue
        summary = _clean_summary(_text(item, "description"))
        published_at = _parse_date(_text(item, "pubDate"))
        articles.append(
            Article(
                title=title,
                url=url,
                source=feed.source,
                source_weight=feed.source_weight,
                summary=summary,
                content=summary,
                published_at=published_at,
                category=feed.default_category,
            )
        )
    return articles


def _parse_atom(root: ElementTree.Element, feed: Feed) -> list[Article]:
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns) or root.findall("entry")
    articles: list[Article] = []
    for entry in entries:
        title = _text(entry, "title") or _text(entry, "{http://www.w3.org/2005/Atom}title")
        url = ""
        for link in entry.findall("atom:link", ns) + entry.findall("link"):
            href = link.attrib.get("href")
            if href:
                url = href
                break
        summary = _clean_summary(
            _text(entry, "summary")
            or _text(entry, "{http://www.w3.org/2005/Atom}summary")
            or _text(entry, "content")
        )
        published_at = _parse_date(
            _text(entry, "updated") or _text(entry, "{http://www.w3.org/2005/Atom}updated")
        )
        if title and url:
            articles.append(
                Article(
                    title=title,
                    url=url,
                    source=feed.source,
                    source_weight=feed.source_weight,
                    summary=summary,
                    content=summary,
                    published_at=published_at,
                    category=feed.default_category,
                )
            )
    return articles


def _text(element: ElementTree.Element, tag: str) -> str:
    child = element.find(tag)
    if child is None or child.text is None:
        return ""
    return unescape(child.text.strip())


def _clean_summary(value: str) -> str:
    if not value:
        return ""
    parser_text = value.replace("<p>", "\n").replace("</p>", "\n").replace("<br>", "\n")
    result: list[str] = []
    in_tag = False
    for char in parser_text:
        if char == "<":
            in_tag = True
            continue
        if char == ">":
            in_tag = False
            continue
        if not in_tag:
            result.append(char)
    return " ".join("".join(result).split())


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

