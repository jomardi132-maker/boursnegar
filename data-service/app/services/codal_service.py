"""
سرویس دریافت اطلاعیه‌های کدال. برگرفته از مسیر تأییدشده در مرحله‌ی قبل
پروژه (endpoint واقعی search.codal.ir).

مثل tsetmc_service، اینجا هم هیچ داده‌ی ساختگی fallback نداریم.
"""
import time
import requests

from app.config import HTTP_USER_AGENT, CODAL_TIMEOUT_SECONDS, CODAL_RATE_LIMIT_SECONDS

BASE_URL = "https://search.codal.ir/api/search/v2/q"

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


def fetch_letters_page(symbol: str, page: int = 1) -> dict:
    params = dict(DEFAULT_PARAMS)
    params["Symbol"] = symbol
    params["PageNumber"] = str(page)

    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=CODAL_TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise CodalUnavailableError(f"خطا در اتصال به کدال: {e}") from e

    return resp.json()


def fetch_all_letters(symbol: str, max_pages: int = 3) -> list:
    """تمام اطلاعیه‌های یک نماد را صفحه‌به‌صفحه می‌گیرد (با رعایت rate limit)."""
    all_letters = []
    for page in range(1, max_pages + 1):
        data = fetch_letters_page(symbol, page)
        letters = data.get("Letters", [])
        if not letters:
            break
        all_letters.extend(letters)

        total_pages = data.get("Page", 1)
        if page >= total_pages:
            break
        time.sleep(CODAL_RATE_LIMIT_SECONDS)

    return all_letters
