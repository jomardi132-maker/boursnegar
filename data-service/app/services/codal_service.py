"""
سرویس دریافت اطلاعیه‌های کدال. برگرفته از مسیر تأییدشده در مرحله‌ی قبل
پروژه (endpoint واقعی search.codal.ir).

مثل tsetmc_service، اینجا هم هیچ داده‌ی ساختگی fallback نداریم.
"""
import time
import requests

from app.config import HTTP_USER_AGENT, CODAL_TIMEOUT_SECONDS, CODAL_RATE_LIMIT_SECONDS, BRSAPI_KEY

BASE_URL = "https://search.codal.ir/api/search/v2/q"
BRSAPI_BASE_URL = "https://Api.BrsApi.ir/Codal/Announcement.php"

HEADERS = {
    "User-Agent": HTTP_USER_AGENT,
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://codal.ir/",
}

DEFAULT_PARAMS = {
    "Audited": "true",
    "AuditorRef": "-1",
    "Category": "-1",
    "Childs": "false",
    "CompanyState": "-1",
    "CompanyType": "-1",
    "Consolidatable": "true",
    "IsNotAudited": "false",
    "Length": "-1",
    "LetterType": "-1",
    "Mains": "true",
    "NotAudited": "true",
    "NotConsolidatable": "true",
    "Publisher": "false",
    "TracingNo": "-1",
    "search": "true",
}


class CodalUnavailableError(Exception):
    pass


_letters_cache: dict[tuple[str, int], tuple[float, list]] = {}
_LETTERS_CACHE_TTL_SECONDS = 15 * 60


def fetch_letters_page(
    symbol: str | None,
    page: int = 1,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict:
    params = dict(DEFAULT_PARAMS)
    if symbol:
        params["Symbol"] = symbol
    if from_date:
        params["FromDate"] = from_date
    if to_date:
        params["ToDate"] = to_date
    params["PageNumber"] = str(page)

    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=CODAL_TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Direct Codal may reject the server by rate limit or close the
        # connection. BrsApi is the configured provider fallback for both.
        if BRSAPI_KEY:
            return _fetch_brsapi_letters_page(symbol, page)
        raise CodalUnavailableError(f"خطا در اتصال به کدال: {e}") from e

    return resp.json()


def _fetch_brsapi_letters_page(symbol: str | None, page: int = 1) -> dict:
    """Use BrsApi's official Codal adapter when direct Codal search is rate-limited."""
    if not BRSAPI_KEY:
        raise CodalUnavailableError(
            "کدال موقتاً محدودیت درخواست اعمال کرده است (429) و BRSAPI_KEY برای مسیر پشتیبان تنظیم نشده است."
        )
    params = {
        "key": BRSAPI_KEY,
        # Category 1 keeps the fallback focused on financial statements,
        # instead of spending the small provider page budget on disclosures.
        "category": 1,
        "audited": "true",
        "unaudited": "true",
        "only_main_company": "true",
        "only_subsidiaries": "false",
        "page": page,
    }
    if symbol:
        params["l18"] = symbol
    provider_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/106.0.0.0",
        "Accept": "application/json, text/plain, */*",
    }
    try:
        resp = requests.get(BRSAPI_BASE_URL, params=params, headers=provider_headers, timeout=CODAL_TIMEOUT_SECONDS)
        resp.raise_for_status()
        payload = resp.json()
    except requests.exceptions.RequestException as e:
        status = e.response.status_code if isinstance(e, requests.exceptions.HTTPError) and e.response is not None else None
        suffix = f" (HTTP {status})" if status else ""
        raise CodalUnavailableError(f"خطا در مسیر پشتیبان Codal از BrsApi{suffix}.") from e
    if not isinstance(payload, dict) or not isinstance(payload.get("announcement"), list):
        raise CodalUnavailableError("پاسخ مسیر پشتیبان Codal از BrsApi قابل‌تفسیر نیست.")
    announcements = []
    for item in payload["announcement"]:
        publish_date = str(item.get("date_publish") or "").strip()
        publish_time = str(item.get("time_publish") or "").strip()
        announcements.append({
            "Symbol": item.get("l18") or symbol,
            "CompanyName": item.get("l30"),
            "Title": item.get("title"),
            "LetterCode": item.get("code"),
            "TracingNo": item.get("link") or f"brsapi:{item.get('l18')}:{item.get('date_publish')}:{item.get('title')}",
            "PublishDateTime": f"{publish_date} {publish_time}".strip(),
            "ExcelUrl": item.get("link_excel"),
            "HasExcel": bool(item.get("link_excel")),
            "Url": item.get("link"),
            "PdfUrl": item.get("link_pdf"),
        })
    return {"Letters": announcements, "Page": payload.get("count_page", page)}


def fetch_all_letters(symbol: str, max_pages: int = 3) -> list:
    """تمام اطلاعیه‌های یک نماد را صفحه‌به‌صفحه می‌گیرد (با رعایت rate limit)."""
    cache_key = (symbol, max_pages)
    cached = _letters_cache.get(cache_key)
    if cached and time.time() - cached[0] < _LETTERS_CACHE_TTL_SECONDS:
        return cached[1]
    all_letters = []
    for page in range(1, max_pages + 1):
        try:
            data = fetch_letters_page(symbol, page)
        except CodalUnavailableError:
            # A provider may allow the first page but reject later pages by
            # quota/plan. A complete first page is still useful and should
            # be parsed instead of turning the whole analysis into a 5xx.
            if all_letters:
                break
            raise
        letters = data.get("Letters", [])
        if not letters:
            break
        all_letters.extend(letters)

        total_pages = data.get("Page", 1)
        if page >= total_pages:
            break
        time.sleep(CODAL_RATE_LIMIT_SECONDS)

    _letters_cache[cache_key] = (time.time(), all_letters)
    return all_letters
