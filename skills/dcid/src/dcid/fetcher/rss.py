from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
import json
import re
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from dcid.config import AppConfig
from dcid.fetcher.content import fetch_page_text
from dcid.models import Article, Feed


def fetch_articles(config: AppConfig) -> list[Article]:
    articles: list[Article] = []
    for feed in config.feeds:
        try:
            if _is_cnbc_listing_page(feed.url):
                feed_articles = fetch_cnbc_listing_page(feed, config.request_timeout_seconds)
            else:
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


def fetch_cnbc_listing_page(feed: Feed, timeout_seconds: int) -> list[Article]:
    request = Request(feed.url, headers={"User-Agent": "DCID/0.1 (+https://github.com/)"})
    with urlopen(request, timeout=timeout_seconds) as response:
        html = response.read(2_000_000).decode("utf-8", errors="replace")
    return _parse_cnbc_listing_page(html, feed)


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


def _parse_cnbc_listing_page(html: str, feed: Feed) -> list[Article]:
    articles: list[Article] = []
    seen_urls: set[str] = set()
    for segment in _cnbc_story_segments(html):
        title_match = re.search(r'"title":"(?P<title>(?:\\.|[^"\\])*)"', segment)
        url_match = re.search(
            r'"url":"(?P<url>https:\\u002F\\u002Fwww\.cnbc\.com\\u002F20\d\d\\u002F(?:\\.|[^"\\])*?\.html)"',
            segment,
        )
        published_match = re.search(r'"datePublished":"(?P<published>(?:\\.|[^"\\])*)"', segment)
        title = _json_string(title_match.group("title")) if title_match else ""
        url = _json_string(url_match.group("url")) if url_match else ""
        published_at = (
            _parse_date(_json_string(published_match.group("published")))
            if published_match
            else None
        )
        if not title or not url or url in seen_urls:
            continue
        seen_urls.add(url)
        articles.append(
            Article(
                title=title,
                url=url,
                source=feed.source,
                source_weight=feed.source_weight,
                summary=title,
                content=title,
                published_at=published_at,
                category=feed.default_category,
            )
        )

    if articles:
        return articles

    link_pattern = re.compile(
        r'<a href="(?P<url>https://www\.cnbc\.com/20\d\d/[^"]+\.html)"[^>]*>.*?'
        r'<(?:h2|h3|div|span)[^>]*>(?P<title>[^<]+)</(?:h2|h3|div|span)>',
        re.DOTALL,
    )
    for match in link_pattern.finditer(html):
        title = _clean_summary(match.group("title"))
        url = unescape(match.group("url"))
        if title and url not in seen_urls:
            seen_urls.add(url)
            articles.append(
                Article(
                    title=title,
                    url=url,
                    source=feed.source,
                    source_weight=feed.source_weight,
                    summary=title,
                    content=title,
                    category=feed.default_category,
                )
            )
    return articles


def _cnbc_story_segments(html: str) -> list[str]:
    pattern = re.compile(
        r'\{"id":\d+.*?"type":"cnbcnewsstory".*?"__typename":"cnbcnewsstory"\}',
        re.DOTALL,
    )
    return [match.group(0) for match in pattern.finditer(html)]


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
            normalized = value.replace("Z", "+00:00")
            if re.search(r"[+-]\d{4}$", normalized):
                normalized = f"{normalized[:-2]}:{normalized[-2:]}"
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _json_string(value: str) -> str:
    try:
        return json.loads(f'"{value}"')
    except json.JSONDecodeError:
        return unescape(value.replace("\\u002F", "/"))


def _is_cnbc_listing_page(url: str) -> bool:
    return url.rstrip("/") in {"https://www.cnbc.com", "https://www.cnbc.com/latest"}
