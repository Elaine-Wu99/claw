# DCID - Daily CNBC Intelligence Digest

DCID fetches CNBC-first RSS news, falls back to Google News RSS, deduplicates articles, classifies them into AI/Tech, Finance/Macro, and Other, ranks the top five per category, and generates a daily Markdown intelligence digest with Chinese reading support.

## Quick Start

```bash
cd dcid
python -m venv .venv
source .venv/bin/activate
pip install -e .
export OPENAI_API_KEY="sk-..."
dcid run --category all
```

Reports are written to `reports/YYYY-MM-DD-dcid.md` by default.

## Commands

```bash
dcid run
dcid run --category ai
dcid run --category finance
dcid run --category other
dcid run --category all --model gpt-4o
dcid run --offline-analysis
```

`--offline-analysis` keeps the pipeline runnable without an API key. It still fetches, deduplicates, classifies, ranks, and renders grounded article summaries, but it does not produce the full LLM sentence-by-sentence analysis.

## Configuration

Environment variables:

- `OPENAI_API_KEY`: required for LLM analysis.
- `DCID_OPENAI_MODEL`: defaults to `gpt-4o-mini`; set to `gpt-4o` for higher quality.
- `DCID_FETCH_FULL_TEXT`: set to `true` to fetch article page text in addition to RSS summaries.

The default feed list is defined in `src/dcid/config.py`. CNBC feeds are weighted highest, and Google News RSS is used as a secondary source.

## Output Format

```markdown
# Daily CNBC Intelligence Digest
Date: YYYY-MM-DD

---

# AI / Tech (Top 5)

[Article 1]
...

---

# Finance / Macro (Top 5)

...

---

# Other News (Top 5)

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

