from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256


CATEGORY_AI = "ai"
CATEGORY_FINANCE = "finance"
CATEGORY_OTHER = "other"
CATEGORIES = (CATEGORY_AI, CATEGORY_FINANCE, CATEGORY_OTHER)

CATEGORY_TITLES = {
    CATEGORY_AI: "AI / Tech",
    CATEGORY_FINANCE: "Finance / Macro",
    CATEGORY_OTHER: "Other News",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


@dataclass(frozen=True)
class Feed:
    url: str
    source: str
    source_weight: float
    default_category: str | None = None


@dataclass
class Article:
    title: str
    url: str
    source: str
    source_weight: float
    summary: str = ""
    content: str = ""
    published_at: datetime | None = None
    fetched_at: datetime = field(default_factory=utc_now)
    category: str | None = None
    classification_confidence: float = 0.0
    score: float = 0.0
    analysis: str = ""

    @property
    def id(self) -> str:
        base = normalize_text(self.url or self.title)
        return sha256(base.encode("utf-8")).hexdigest()[:16]

    @property
    def title_hash(self) -> str:
        return sha256(normalize_text(self.title).encode("utf-8")).hexdigest()[:16]

    @property
    def text_for_analysis(self) -> str:
        body = self.content or self.summary
        return f"Title: {self.title}\nURL: {self.url}\nSource: {self.source}\n\n{body}".strip()

    def to_jsonable(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "source_weight": self.source_weight,
            "summary": self.summary,
            "content": self.content,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "fetched_at": self.fetched_at.isoformat(),
            "category": self.category,
            "classification_confidence": self.classification_confidence,
            "score": self.score,
        }


@dataclass(frozen=True)
class Classification:
    category: str
    confidence: float
    reason: str

