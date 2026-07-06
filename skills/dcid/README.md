# DCID - Daily CNBC Intelligence Digest

DCID fetches CNBC RSS news, filters for policy, fiscal, macro, company, and stock-market relevance, classifies articles into AI/Tech, Finance/Macro, and Policy/Market Impact, ranks the top five per category, and generates daily Markdown and HTML intelligence digests with Chinese reading support.

## Quick Start

```bash
cd dcid
python -m venv .venv
source .venv/bin/activate
pip install -e .
export OPENAI_API_KEY="sk-..."
dcid run --category all
```

Reports are written to `/Users/qiaowenwu/Desktop/新闻report/YYYY-MM-DD-dcid.md` and `/Users/qiaowenwu/Desktop/新闻report/YYYY-MM-DD-dcid.html` by default. Raw fetched articles are written to both `/Users/qiaowenwu/Desktop/新闻report/raw/YYYY-MM-DD.jsonl` and a reader-friendly `/Users/qiaowenwu/Desktop/新闻report/raw/YYYY-MM-DD.html`.

## Commands

```bash
dcid run
dcid run --category ai
dcid run --category finance
dcid run --category other
dcid run --category all --model gpt-4o
dcid run --category all --fetch-full-text
dcid run --offline-analysis
```

`--offline-analysis` keeps the pipeline runnable without an API key. It still fetches, deduplicates, classifies, ranks, and renders grounded article summaries, but it does not produce the full LLM sentence-by-sentence analysis.

Use `--fetch-full-text` with LLM analysis when you want the richer Chinese paragraph-by-paragraph reading notes; otherwise the model only receives RSS summary text.

## Configuration

Environment variables:

- `OPENAI_API_KEY`: required for LLM analysis.
- `DCID_OPENAI_MODEL`: defaults to `gpt-4o-mini`; set to `gpt-4o` for higher quality.
- `DCID_FETCH_FULL_TEXT`: set to `true` to fetch article page text in addition to RSS summaries.
- `DCID_INCLUDE_GOOGLE`: set to `true` to include Google News RSS fallback sources. Defaults to CNBC-only.
- `DCID_REPORTS_DIR` / `DCID_DATA_DIR`: override the default `/Users/qiaowenwu/Desktop/新闻report` output folder.

The default feed list is defined in `src/dcid/config.py`. CNBC feeds are used by default; Google News RSS is opt-in to avoid non-CNBC sources such as Yahoo.

## Selection Rules

DCID filters stale RSS items before ranking:

- Weekdays: keep articles published within the last 48 hours.
- Weekends: keep articles published within the last 72 hours.
- Articles with no RSS publication timestamp are kept to avoid dropping valid CNBC items with incomplete metadata.

## Output Format

```markdown
# Daily CNBC Intelligence Digest
Date: YYYY-MM-DD

---

# AI / Tech (Top 5)

[Article 1]
## Investment Lens
- Investment relevance: High / Medium / Low
- Likely direction: Bullish / Bearish / Mixed / Unclear
- Impact scope: Market / Sector / Single stock
- Related tickers / ETFs: ...
...

---

# Finance / Macro (Top 5)

...

---

# Policy / Market Impact (Top 5)

...

---

# Key Vocabulary Today

- 10-15 high-frequency financial terms

---

# Macro Summary Insight

1-2 paragraph synthesis of market narrative
```

## Scheduling

The included GitHub Actions workflow runs daily at `14:00 UTC`. Add `OPENAI_API_KEY` as a repository secret before enabling it.
