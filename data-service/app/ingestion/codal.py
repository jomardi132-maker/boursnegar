import hashlib, time
from dataclasses import dataclass
from typing import Callable, Iterator

@dataclass(frozen=True)
class DisclosureRef:
    tracing_no: str
    title: str
    published_at: str | None
    url: str | None
    revision_hint: bool

def discover_pages(fetch_page: Callable[[int], dict], start_page=1, checkpoint: Callable[[int], None] | None=None,
                   rate_seconds=0.0, max_pages: int | None=None) -> Iterator[DisclosureRef]:
    seen: set[str] = set(); page = start_page
    while True:
        payload = fetch_page(page); letters = payload.get("Letters") or []
        total = int(payload.get("Page") or page)
        for row in letters:
            key = str(row.get("TracingNo") or "")
            if not key or key in seen: continue
            seen.add(key); title = str(row.get("Title") or "")
            yield DisclosureRef(key, title, row.get("PublishDateTime"), row.get("Url"), "اصلاح" in title)
        if checkpoint: checkpoint(page)
        if not letters or page >= total or (max_pages is not None and page >= max_pages): break
        page += 1
        if rate_seconds: time.sleep(rate_seconds)

def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
