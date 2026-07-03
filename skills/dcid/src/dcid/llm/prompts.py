from __future__ import annotations

from dcid.models import Article


SYSTEM_PROMPT = """You are a senior CNBC editor and financial English teacher.
Use only the provided article text, title, source, and URL.
If the article text does not support a claim, say the information is not available.
Keep the analysis grounded, concise, and useful for a Chinese-speaking finance reader."""


def article_analysis_prompt(article: Article) -> str:
    return f"""For this article:

1. Translate into natural Chinese, not literal translation.
2. Break down important sentences one by one.
3. Explain financial vocabulary.
4. Explain macro or market context that is directly supported by the article text.
5. Explain why CNBC or a financial newsroom would use this phrasing.
6. Highlight market implications if directly supported.

Return exactly this structure:

# {article.title}

## Chinese Translation
...

## Sentence-by-Sentence Breakdown
- Sentence 1:
- Sentence 2:

## Key Vocabulary
- term: explanation

## Macro Context
...

## CNBC Writing Style Insight
...

Article:
{article.text_for_analysis}
"""

