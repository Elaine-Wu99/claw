---
name: dcid
description: Generate the Daily CNBC Intelligence Digest from the local DCID Python pipeline. Use when the user explicitly invokes $dcid, asks to run DCID, requests a daily CNBC intelligence digest, or wants top AI/tech, finance/macro, and other news translated and analyzed in the DCID format.
---

# DCID

## Overview

Run the repository's DCID engine from `skills/dcid` and return the generated Markdown report path plus a short execution summary. DCID fetches CNBC-first RSS news, deduplicates, classifies, ranks, and renders a daily Chinese-friendly market intelligence digest.

## Workflow

1. Work from the repository root that contains `skills/dcid`.
2. Use `skills/dcid` as the working directory for commands.
3. If the user asks for full LLM analysis, require `OPENAI_API_KEY`; otherwise run `--offline-analysis`.
4. Prefer the existing local source tree over global installs:

```bash
PYTHONPATH=src python -m dcid run --offline-analysis
```

5. For full analysis, run:

```bash
PYTHONPATH=src python -m dcid run --category all
```

6. For category-specific runs, pass `--category ai`, `--category finance`, or `--category other`.
7. After the run, report the generated file from `reports/YYYY-MM-DD-dcid.md`.

## Output

Summarize:

- Report path
- Raw articles path
- Fetched count
- Unique count
- Analyzed count
- Any warnings, especially feed, network, or API failures

Do not paste entire generated reports unless the user asks. Provide the path and a brief preview instead.
