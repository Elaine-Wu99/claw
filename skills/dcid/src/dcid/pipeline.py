from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
import sys

from dcid.classifier import classify_article
from dcid.classifier.rules import is_market_relevant
from dcid.classifier.llm import OpenAIClassifier
from dcid.config import AppConfig
from dcid.fetcher import fetch_articles
from dcid.fetcher.content import fetch_page_text
from dcid.investment import evaluate_investment_lens
from dcid.llm import OpenAIAnalyzer
from dcid.models import CATEGORY_AI, CATEGORY_FINANCE, CATEGORY_OTHER, Article
from dcid.ranker import rank_articles, select_top_by_category
from dcid.reporter import render_html_report, render_raw_articles_html, render_report
from dcid.storage import (
    deduplicate_articles,
    store_raw_articles,
    store_raw_articles_html,
    write_html_report,
    write_report,
)


@dataclass(frozen=True)
class PipelineResult:
    report_path: str
    html_report_path: str
    raw_articles_path: str
    raw_articles_html_path: str
    fetched_count: int
    unique_count: int
    analyzed_count: int


def run_pipeline(
    config: AppConfig,
    category: str = "all",
    offline_analysis: bool = False,
    report_date: date | None = None,
) -> PipelineResult:
    current_date = report_date or date.today()
    fetch_config = config
    if config.fetch_full_text:
        fetch_config = config.__class__(**{**config.__dict__, "fetch_full_text": False})
    _log_progress("fetching CNBC RSS feeds")
    fetched = fetch_articles(fetch_config)
    unique = deduplicate_articles(fetched)
    _log_progress(f"fetched {len(fetched)} articles; {len(unique)} unique")
    current_datetime = datetime.combine(current_date, time.max, tzinfo=timezone.utc)
    recent = _filter_recent_articles(unique, current_datetime)
    _log_progress(
        f"kept {len(recent)} recent articles within {_recency_cutoff_hours(current_date)} hours"
    )
    raw_path = store_raw_articles(unique, config.data_dir, current_date)

    llm_classifier = None
    if config.openai_api_key and not offline_analysis:
        llm_classifier = OpenAIClassifier(
            config.openai_api_key,
            config.openai_model,
            timeout_seconds=config.request_timeout_seconds,
        )

    _log_progress("classifying articles")
    for index, article in enumerate(recent, start=1):
        classification = classify_article(article)
        if (
            classification.category == CATEGORY_OTHER
            and classification.confidence < 0.75
            and llm_classifier is not None
        ):
            _log_progress(f"classifying with LLM {index}/{len(recent)}: {_article_label(article)}")
            try:
                classification = llm_classifier.classify(article)
            except RuntimeError as exc:
                print(f"warning: LLM classifier failed for {article.url}: {exc}")
                if "insufficient_quota" in str(exc) or "Too Many Requests" in str(exc):
                    llm_classifier = None
        article.category = classification.category
        article.classification_confidence = classification.confidence

    market_relevant = [article for article in recent if is_market_relevant(article)]
    _log_progress(f"kept {len(market_relevant)} market-relevant articles")
    ranked = rank_articles(market_relevant)
    selected = select_top_by_category(ranked, config.top_per_category, category)
    selected_articles = _selected_articles(selected)
    for article in selected_articles:
        article.investment_lens = evaluate_investment_lens(article)
    _log_progress(f"selected {len(selected_articles)} articles for report")
    if config.fetch_full_text:
        _fetch_selected_full_text(selected, config.request_timeout_seconds)

    analyzer = None
    if not offline_analysis:
        if not config.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required unless --offline-analysis is used")
        analyzer = OpenAIAnalyzer(
            config.openai_api_key,
            config.openai_model,
            timeout_seconds=max(60, config.request_timeout_seconds),
        )

    analyzed_count = 0
    for index, article in enumerate(selected_articles, start=1):
        if analyzer is None:
            continue
        _log_progress(f"analyzing {index}/{len(selected_articles)}: {_article_label(article)}")
        try:
            article.analysis = analyzer.analyze(article)
        except RuntimeError as exc:
            print(f"warning: LLM analyzer failed for {article.url}: {exc}")
            if "insufficient_quota" in str(exc) or "Too Many Requests" in str(exc):
                analyzer = None
            continue
        analyzed_count += 1

    macro_summary = _macro_summary(selected, offline_analysis)
    markdown = render_report(current_date, selected, macro_summary)
    html = render_html_report(current_date, selected, macro_summary)
    raw_html = render_raw_articles_html(current_date, unique)
    report_path = write_report(markdown, config.reports_dir, current_date)
    html_report_path = write_html_report(html, config.reports_dir, current_date)
    raw_html_path = store_raw_articles_html(raw_html, config.data_dir, current_date)
    return PipelineResult(
        report_path=str(report_path),
        html_report_path=str(html_report_path),
        raw_articles_path=str(raw_path),
        raw_articles_html_path=str(raw_html_path),
        fetched_count=len(fetched),
        unique_count=len(unique),
        analyzed_count=analyzed_count,
    )


def _selected_articles(selected: dict[str, list[Article]]) -> list[Article]:
    return [article for articles in selected.values() for article in articles]


def _filter_recent_articles(articles: list[Article], now: datetime) -> list[Article]:
    cutoff_hours = _recency_cutoff_hours(now.date())
    recent: list[Article] = []
    for article in articles:
        if article.published_at is None:
            recent.append(article)
            continue
        published_at = article.published_at
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        age_hours = (now - published_at).total_seconds() / 3600
        if age_hours <= cutoff_hours:
            recent.append(article)
    return recent


def _recency_cutoff_hours(report_date: date) -> int:
    if report_date.weekday() >= 5:
        return 72
    return 48


def _fetch_selected_full_text(
    selected: dict[str, list[Article]],
    timeout_seconds: int,
) -> None:
    articles = _selected_articles(selected)
    for index, article in enumerate(articles, start=1):
        _log_progress(f"fetching full text {index}/{len(articles)}: {_article_label(article)}")
        try:
            article.content = fetch_page_text(article.url, timeout_seconds)
        except Exception as exc:
            print(f"warning: failed to fetch full text for {article.url}: {exc}")
            article.content = article.summary


def _log_progress(message: str) -> None:
    print(f"progress: {message}", file=sys.stderr, flush=True)


def _article_label(article: Article) -> str:
    return article.title[:100]


def _macro_summary(selected: dict[str, list[Article]], offline_analysis: bool) -> str:
    finance_titles = [article.title for article in selected.get(CATEGORY_FINANCE, [])]
    ai_titles = [article.title for article in selected.get(CATEGORY_AI, [])]
    if offline_analysis:
        return (
            "Offline analysis mode selected the highest-scoring articles by source weight, "
            "recency, and keyword relevance. Run with `OPENAI_API_KEY` to generate the full "
            "1-2 paragraph market narrative grounded in the article text."
        )
    finance_line = "; ".join(finance_titles[:3]) or "No finance articles were selected."
    ai_line = "; ".join(ai_titles[:3]) or "No AI or technology articles were selected."
    return (
        "The selected finance and macro stories center on: "
        f"{finance_line}\n\n"
        "The selected AI and technology stories center on: "
        f"{ai_line}"
    )
