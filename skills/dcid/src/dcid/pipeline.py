from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from dcid.classifier import classify_article
from dcid.classifier.llm import OpenAIClassifier
from dcid.config import AppConfig
from dcid.fetcher import fetch_articles
from dcid.llm import OpenAIAnalyzer
from dcid.models import CATEGORY_AI, CATEGORY_FINANCE, CATEGORY_OTHER, Article
from dcid.ranker import rank_articles, select_top_by_category
from dcid.reporter import render_report
from dcid.storage import deduplicate_articles, store_raw_articles, write_report


@dataclass(frozen=True)
class PipelineResult:
    report_path: str
    raw_articles_path: str
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
    fetched = fetch_articles(config)
    unique = deduplicate_articles(fetched)
    raw_path = store_raw_articles(unique, config.data_dir, current_date)

    llm_classifier = None
    if config.openai_api_key and not offline_analysis:
        llm_classifier = OpenAIClassifier(
            config.openai_api_key,
            config.openai_model,
            timeout_seconds=config.request_timeout_seconds,
        )

    for article in unique:
        classification = classify_article(article)
        if (
            classification.category == CATEGORY_OTHER
            and classification.confidence < 0.75
            and llm_classifier is not None
        ):
            try:
                classification = llm_classifier.classify(article)
            except RuntimeError as exc:
                print(f"warning: LLM classifier failed for {article.url}: {exc}")
        article.category = classification.category
        article.classification_confidence = classification.confidence

    ranked = rank_articles(unique)
    selected = select_top_by_category(ranked, config.top_per_category, category)

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
    for article in _selected_articles(selected):
        if analyzer is None:
            continue
        article.analysis = analyzer.analyze(article)
        analyzed_count += 1

    macro_summary = _macro_summary(selected, offline_analysis)
    markdown = render_report(current_date, selected, macro_summary)
    report_path = write_report(markdown, config.reports_dir, current_date)
    return PipelineResult(
        report_path=str(report_path),
        raw_articles_path=str(raw_path),
        fetched_count=len(fetched),
        unique_count=len(unique),
        analyzed_count=analyzed_count,
    )


def _selected_articles(selected: dict[str, list[Article]]) -> list[Article]:
    return [article for articles in selected.values() for article in articles]


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
