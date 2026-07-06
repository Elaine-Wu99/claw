from __future__ import annotations

from dcid.models import Article


SYSTEM_PROMPT = """You are a senior CNBC editor and financial English teacher.
Use only the provided article text, title, source, and URL.
If the article text does not support a claim, say the information is not available.
Write in clear, natural Simplified Chinese for a Chinese-speaking finance reader.
Explain CNBC-style market English patiently, like a paragraph-by-paragraph reading note.
Focus on policy, politics, fiscal conditions, macro data, company fundamentals, and likely stock-market implications."""


def article_analysis_prompt(article: Article) -> str:
    return f"""Analyze this CNBC-style finance article for a Chinese learner.

Use this style:
- Start with "这篇是在说：" and summarize the article's market logic in one or two natural Chinese sentences.
- Then walk through the article paragraph by paragraph using headings such as "第一段：为什么这件事重要？".
- For each important English sentence, quote the sentence, give a natural Chinese translation, and explain key expressions underneath.
- Explain vocabulary in context, for example "on hold", "pare positions", "intraday", "respectively", or article-specific terms.
- Explain the market or macro logic only when supported by the provided text.
- Connect policy, political, fiscal, macro, or company news to stock-market implications when the text supports it.
- Include a cautious investment-read section: relevance, direction, scope, related tickers/ETFs, and what to verify before making a decision.
- If the article includes a quote, translate it naturally and explain what the speaker is implying.
- End with "整篇新闻的市场逻辑" and list the causal chain in short Chinese lines.
- Do not invent facts that are not in the article text.

Return exactly this structure:

# {article.title}

Source: {article.source}
URL: {article.url}
Score: {article.score:.2f}

## 这篇是在说
这篇是在说：...

## 逐段精读
### 第一段：...
English sentence

自然翻译：
...

关键词：
- term = explanation

市场逻辑：
...

## 整篇新闻的市场逻辑
- ...

## Investment Decision View (投资决策视角)
- Investment relevance (投资相关度): High / Medium / Low (高 / 中 / 低)
- News tilt, not trading advice (新闻倾向，不是买卖建议): Bullish / Bearish / Mixed / Unclear (偏正面 / 偏负面 / 正负混合 / 传导不明确)
- Impact scope (影响范围): Single stock / Sector / Market (个股 / 板块 / 大盘)
- Related tickers / ETFs (相关股票 / ETF): ...
- What to verify before buying (买股票前还要确认): ...

Article text:
{article.text_for_analysis}
"""
