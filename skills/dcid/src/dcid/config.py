from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dcid.models import CATEGORY_AI, CATEGORY_FINANCE, CATEGORY_OTHER, Feed


DEFAULT_OUTPUT_DIR = Path("/Users/qiaowenwu/Desktop/新闻report")


@dataclass(frozen=True)
class AppConfig:
    feeds: tuple[Feed, ...]
    data_dir: Path = DEFAULT_OUTPUT_DIR
    reports_dir: Path = DEFAULT_OUTPUT_DIR
    openai_model: str = "gpt-4o-mini"
    fetch_full_text: bool = False
    max_articles_per_feed: int = 40
    request_timeout_seconds: int = 20
    top_per_category: int = 5
    openai_api_key: str | None = field(default=None, repr=False)


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def default_feeds(include_google: bool = False) -> tuple[Feed, ...]:
    cnbc_feeds = (
        Feed(
            "https://www.cnbc.com/latest/",
            "CNBC Latest",
            3.2,
        ),
        Feed(
            "https://www.cnbc.com/",
            "CNBC Homepage",
            3.2,
        ),
        Feed(
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            "CNBC Top News",
            3.0,
        ),
        Feed(
            "https://www.cnbc.com/id/19854910/device/rss/rss.html",
            "CNBC Technology",
            3.0,
            CATEGORY_AI,
        ),
        Feed(
            "https://www.cnbc.com/id/10000664/device/rss/rss.html",
            "CNBC Finance",
            3.0,
            CATEGORY_FINANCE,
        ),
    )
    if not include_google:
        return cnbc_feeds
    return (
        *cnbc_feeds,
        Feed(
            "https://news.google.com/rss/search?q=AI%20OR%20Nvidia%20OR%20OpenAI%20when:1d&hl=en-US&gl=US&ceid=US:en",
            "Google News AI",
            2.0,
            CATEGORY_AI,
        ),
        Feed(
            "https://news.google.com/rss/search?q=Fed%20OR%20inflation%20OR%20markets%20OR%20yields%20when:1d&hl=en-US&gl=US&ceid=US:en",
            "Google News Finance",
            2.0,
            CATEGORY_FINANCE,
        ),
        Feed(
            "https://news.google.com/rss/topstories?hl=en-US&gl=US&ceid=US:en",
            "Google News Top Stories",
            2.0,
            CATEGORY_OTHER,
        ),
    )


def load_config() -> AppConfig:
    return AppConfig(
        feeds=default_feeds(include_google=_env_flag("DCID_INCLUDE_GOOGLE", False)),
        data_dir=Path(os.getenv("DCID_DATA_DIR", str(DEFAULT_OUTPUT_DIR))),
        reports_dir=Path(os.getenv("DCID_REPORTS_DIR", str(DEFAULT_OUTPUT_DIR))),
        openai_model=os.getenv("DCID_OPENAI_MODEL", "gpt-4o-mini"),
        fetch_full_text=_env_flag("DCID_FETCH_FULL_TEXT", False),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
