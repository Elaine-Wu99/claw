from __future__ import annotations

import argparse

from dcid.config import load_config
from dcid.models import CATEGORIES
from dcid.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dcid", description="Daily CNBC Intelligence Digest")
    subparsers = parser.add_subparsers(dest="command")
    run = subparsers.add_parser("run", help="Generate the daily digest")
    run.add_argument(
        "--category",
        choices=("all", *CATEGORIES),
        default="all",
        help="Limit output to a category while preserving report sections.",
    )
    run.add_argument("--model", help="Override the OpenAI model for this run")
    run.add_argument(
        "--offline-analysis",
        action="store_true",
        help="Skip OpenAI analysis and render grounded feed summaries.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        args.command = "run"
        args.category = "all"
        args.model = None
        args.offline_analysis = False

    if args.command != "run":
        parser.error(f"unknown command: {args.command}")

    config = load_config()
    if args.model:
        config = config.__class__(**{**config.__dict__, "openai_model": args.model})

    result = run_pipeline(config, category=args.category, offline_analysis=args.offline_analysis)
    print(f"report: {result.report_path}")
    print(f"raw articles: {result.raw_articles_path}")
    print(f"fetched: {result.fetched_count}")
    print(f"unique: {result.unique_count}")
    print(f"analyzed: {result.analyzed_count}")
    return 0

