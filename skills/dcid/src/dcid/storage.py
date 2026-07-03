from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from dcid.models import Article


def deduplicate_articles(articles: list[Article]) -> list[Article]:
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    unique: list[Article] = []
    for article in articles:
        url_key = article.url.strip().lower()
        title_key = article.title_hash
        if url_key in seen_urls or title_key in seen_titles:
            continue
        seen_urls.add(url_key)
        seen_titles.add(title_key)
        unique.append(article)
    return unique


def store_raw_articles(articles: list[Article], data_dir: Path, report_date: date) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "raw" / f"{report_date.isoformat()}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for article in articles:
            handle.write(json.dumps(article.to_jsonable(), ensure_ascii=False) + "\n")
    return path


def write_report(markdown: str, reports_dir: Path, report_date: date) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"{report_date.isoformat()}-dcid.md"
    path.write_text(markdown, encoding="utf-8")
    return path

