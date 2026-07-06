from __future__ import annotations

import json
from json import JSONDecodeError
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from dcid.models import CATEGORIES, CATEGORY_OTHER, Article, Classification


CLASSIFIER_SYSTEM_PROMPT = """Classify the article into exactly one category:
ai, finance, or other.
Return JSON only with keys category and confidence.
Use ai for AI, chips, cloud, software, semiconductors, and major technology platforms.
Use finance for Fed, inflation, rates, yields, markets, oil, earnings, jobs, and macro data."""


class OpenAIClassifier:
    def __init__(self, api_key: str, model: str, timeout_seconds: int = 30) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    def classify(self, article: Article) -> Classification:
        payload = {
            "model": self.model,
            "input": [
                {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Title: {article.title}\n"
                        f"Source: {article.source}\n"
                        f"Summary: {article.summary or article.content}"
                    ),
                },
            ],
        }
        request = Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI classifier error {exc.code}: {detail}") from exc

        parsed = _parse_classifier_response(body)
        category = parsed.get("category", CATEGORY_OTHER)
        confidence = float(parsed.get("confidence", 0.5))
        if category not in CATEGORIES:
            category = CATEGORY_OTHER
        return Classification(category, max(0.0, min(confidence, 1.0)), "llm fallback")


def _parse_classifier_response(body: dict[str, object]) -> dict[str, object]:
    text = ""
    if isinstance(body.get("output_text"), str):
        text = str(body["output_text"])
    else:
        output = body.get("output")
        if isinstance(output, list):
            for item in output:
                if not isinstance(item, dict):
                    continue
                content = item.get("content")
                if not isinstance(content, list):
                    continue
                for part in content:
                    if isinstance(part, dict) and isinstance(part.get("text"), str):
                        text += part["text"]
    cleaned = _strip_json_fence(text.strip())
    if not cleaned:
        raise RuntimeError("OpenAI classifier response did not include text output")
    try:
        return json.loads(cleaned)
    except JSONDecodeError as exc:
        raise RuntimeError(f"OpenAI classifier returned non-JSON output: {cleaned[:200]}") from exc


def _strip_json_fence(text: str) -> str:
    if text.startswith("```json") and text.endswith("```"):
        return text.removeprefix("```json").removesuffix("```").strip()
    if text.startswith("```") and text.endswith("```"):
        return text.removeprefix("```").removesuffix("```").strip()
    return text
