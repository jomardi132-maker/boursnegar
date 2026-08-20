"""
سرویس دریافت داده‌ی زنده‌ی سهام - نسخه‌ی نهایی، از طریق BrsApi.ir

چرا نه اتصال مستقیم به cdn.tsetmc.com؟
چون از IP این سرور (هرچند داخل ایران) توسط تستمسی بلاک شده - تأیید شده
با traceroute/ping/curl در مرحله‌ی دیباگ پروژه. BrsApi.ir یک واسط رسمی و
مستند است که خودش این مشکل رو حل کرده.

مثل قبل: هیچ داده‌ی جایگزین/ساختگی fallback نداریم. اگه BrsApi جواب نده
یا نماد پیدا نشه، Exception روشن پرتاب می‌شه.

نکته‌ی مهم درباره‌ی rate limit: endpoint AllSymbols کل بازار رو یک‌جا
برمی‌گردونه (حجم پاسخ بزرگه). برای جلوگیری از درخواست مکرر و رسیدن به
سقف ۳۰۰ درخواست/۵ دقیقه، نتیجه رو به مدت چند ثانیه در حافظه کش می‌کنیم.
"""
import time
import threading
import requests

from app.config import HTTP_USER_AGENT, TSETMC_TIMEOUT_SECONDS, BRSAPI_KEY

ALL_SYMBOLS_URL = "https://Api.BrsApi.ir/Tsetmc/AllSymbols.php"

# BrsApi صراحتاً اعلام کرده User-Agent پیش‌فرض کتابخانه‌های HTTP (پایتون/گو و...)
# توسط فایروالشون بلاک می‌شه؛ باید User-Agent شبیه مرورگر واقعی بفرستیم.
HEADERS = {
    "User-Agent": HTTP_USER_AGENT,
    "Accept": "application/json, text/plain, */*",
}

# AllSymbols is a bulk response and BrsApi documents a rolling request limit.
# Keep it for several minutes so page loads and analysis requests share one
# provider call instead of consuming quota repeatedly.
CACHE_TTL_SECONDS = 300
_cache_lock = threading.Lock()
_cache = {"data": None, "fetched_at": 0.0}


class TsetmcNotFoundError(Exception):
    pass


class TsetmcUnavailableError(Exception):
    pass


class TsetmcConfigError(Exception):
    """وقتی BRSAPI_KEY در .env تنظیم نشده باشه."""
    pass


def _fetch_all_symbols_raw() -> list:
    """درخواست خام به BrsApi - بدون کش. معمولاً نباید مستقیم صداش بزنی."""
    if not BRSAPI_KEY:
        raise TsetmcConfigError("BRSAPI_KEY در فایل .env تنظیم نشده است.")

    params = {"key": BRSAPI_KEY}
    try:
        resp = requests.get(ALL_SYMBOLS_URL, params=params, headers=HEADERS, timeout=TSETMC_TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise TsetmcUnavailableError(f"خطا در اتصال به BrsApi: {e}") from e

    try:
        data = resp.json()
    except ValueError as e:
        raise TsetmcUnavailableError(f"پاسخ BrsApi قابل‌تفسیر به JSON نبود: {e}") from e

    if not isinstance(data, list):
        raise TsetmcUnavailableError(f"فرمت غیرمنتظره از BrsApi: {str(data)[:200]}")

    return data


def get_all_symbols(force_refresh: bool = False) -> list:
    """
    نسخه‌ی کش‌شده‌ی لیست کامل نمادها. اکثر درخواست‌ها باید از همین استفاده کنن
    تا به سقف rate limit نخوریم.
    """
    with _cache_lock:
        age = time.time() - _cache["fetched_at"]
        if force_refresh or _cache["data"] is None or age > CACHE_TTL_SECONDS:
            _cache["data"] = _fetch_all_symbols_raw()
            _cache["fetched_at"] = time.time()
        return _cache["data"]


def _map_symbol_record(rec: dict) -> dict:
    """تبدیل رکورد خام BrsApi به یک ساختار تمیزتر و مستندتر."""
    eps = rec.get("eps")
    pe = rec.get("pe")

    buy_i_count = rec.get("Buy_CountI") or 0
    sell_i_count = rec.get("Sell_CountI") or 0
    buy_i_volume = rec.get("Buy_I_Volume") or 0
    sell_i_volume = rec.get("Sell_I_Volume") or 0

    # قدرت خریدار حقیقی: میانگین حجم هر خرید حقیقی نسبت به میانگین حجم هر فروش حقیقی
    # (نسخه‌ی واقعی و محاسبه‌شده‌ی همون مفهومی که قبلاً در کد جعلی هاردکد شده بود)
    real_buyer_power = None
    if buy_i_count > 0 and sell_i_count > 0 and sell_i_volume > 0:
        avg_buy = buy_i_volume / buy_i_count
        avg_sell = sell_i_volume / sell_i_count
        if avg_sell > 0:
            real_buyer_power = round(avg_buy / avg_sell, 2)

    return {
        "symbol": rec.get("l18"),
        "full_name": rec.get("l30"),
        "isin": rec.get("isin"),
        "market_id": rec.get("id"),
        "market_category": rec.get("cs"),
        "eps": eps,
        "pe_ratio": pe,
        "market_cap": rec.get("mv"),
        "total_shares": rec.get("z"),
        "last_price": rec.get("pl"),
        "last_price_change": rec.get("plc"),
        "last_price_change_percent": rec.get("plp"),
        "closing_price": rec.get("pc"),
        "closing_price_change": rec.get("pcc"),
        "closing_price_change_percent": rec.get("pcp"),
        "yesterday_closing_price": rec.get("py"),
        "day_open": rec.get("pf"),
        "day_low": rec.get("pmin"),
        "day_high": rec.get("pmax"),
        "allowed_price_min": rec.get("tmin"),
        "allowed_price_max": rec.get("tmax"),
        "trade_count": rec.get("tno"),
        "trade_volume": rec.get("tvol"),
        "trade_value": rec.get("tval"),
        "real_buyer_count": buy_i_count,
        "real_seller_count": sell_i_count,
        "legal_buyer_count": rec.get("Buy_CountN"),
        "legal_seller_count": rec.get("Sell_CountN"),
        "real_buy_volume": buy_i_volume,
        "real_sell_volume": sell_i_volume,
        "legal_buy_volume": rec.get("Buy_N_Volume"),
        "legal_sell_volume": rec.get("Sell_N_Volume"),
        "real_buyer_power_ratio": real_buyer_power,
        "last_trade_time": rec.get("time"),
        "raw": rec,
    }


def fetch_live_snapshot(symbol: str) -> dict:
    """
    تابع اصلی: نماد فارسی رو می‌گیره و آخرین اطلاعات واقعی بازار رو برمی‌گردونه.
    """
    symbol = symbol.strip()
    all_symbols = get_all_symbols()

    match = next((rec for rec in all_symbols if rec.get("l18") == symbol), None)
    if not match:
        raise TsetmcNotFoundError(f"نماد «{symbol}» در داده‌ی لحظه‌ای بازار پیدا نشد.")

    return _map_symbol_record(match)
