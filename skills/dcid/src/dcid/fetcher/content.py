from __future__ import annotations

from html.parser import HTMLParser
from urllib.request import Request, urlopen


class _ReadableTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "nav", "footer", "header", "aside"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "footer", "header", "aside"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = " ".join(data.split())
        if len(text) >= 40:
            self._chunks.append(text)

    def text(self) -> str:
        return "\n".join(self._chunks)


def fetch_page_text(url: str, timeout_seconds: int) -> str:
    request = Request(url, headers={"User-Agent": "DCID/0.1 (+https://github.com/)"})
    with urlopen(request, timeout=timeout_seconds) as response:
        content_type = response.headers.get("content-type", "")
        if "html" not in content_type:
            return ""
        html = response.read(1_500_000).decode("utf-8", errors="replace")
    parser = _ReadableTextParser()
    parser.feed(html)
    return parser.text()

