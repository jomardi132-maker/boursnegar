"""
پارسر صورت مالی کدال.

نکته‌ی کلیدی: فایلی که کدال به اسم "اکسل" می‌ده در واقع HTML است (فرمت
قدیمی Excel Workbook Frameset)، نه xlsx واقعی. برای همین با
pandas.read_html پردازش می‌شه، نه openpyxl.

استراتژی: به‌جای فرض کردن شماره‌ی ثابت جدول برای هر قلم (که بین شرکت‌های
مختلف فرق می‌کنه)، تمام جدول‌های موجود در فایل رو می‌گردیم و دنبال
ردیف‌هایی با برچسب استاندارد حسابداری فارسی می‌گردیم. این روش در برابر
تفاوت ساختار بین شرکت‌های مختلف مقاوم‌تره.

هیچ عدد جایگزین/پیش‌فرضی نداریم - اگه قلمی پیدا نشه، مقدارش None
می‌مونه و صادقانه گزارش می‌شه، نه یه عدد ساختگی.
"""
import re
import requests
import pandas as pd

from app.config import HTTP_USER_AGENT

HEADERS = {"User-Agent": HTTP_USER_AGENT}

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_INDIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
ASCII_DIGITS = "0123456789"
_DIGIT_TRANS = str.maketrans(PERSIAN_DIGITS + ARABIC_INDIC_DIGITS, ASCII_DIGITS + ASCII_DIGITS)

# قلم‌های هدف: کلید داخلی -> لیستی از برچسب‌های محتمل فارسی (بعد از نرمال‌سازی، بدون فاصله)
TARGET_ITEMS = {
    "revenue": ["درآمدهایعملیاتی", "درآمدعملیاتی"],
    "cogs": ["بهایتمامشدهدرآمدهایعملیاتی"],
    "gross_profit": ["سود(زیان)ناخالص", "سودناخالص"],
    "operating_profit": ["سود(زیان)عملیاتی", "سودعملیاتی"],
    "net_profit": ["سود(زیان)خالص", "سودخالص"],
    "eps_basic": ["سود(زیان)پایههرسهم", "سودپایههرسهم", "سودهرسهم"],
    "total_assets": ["جمعدارایی‌ها", "جمعداراییها", "جمعکلدارایی‌ها"],
    "total_liabilities": ["جمعبدهی‌ها", "جمعبدهیها"],
    "total_equity": ["جمعحقوقصاحبانسهام", "جمعحقوقمالکانه"],
    "operating_cash_flow": [
        "جریانخالصوجهنقدحاصلازفعالیت‌هایعملیاتی",
        "جریانخالصوجهنقدحاصلازفعالیتهایعملیاتی",
        "جریانخالصوجهنقدناشیازفعالیت‌هایعملیاتی",
        "جریانخالصوجهنقدناشیازفعالیتهایعملیاتی",
    ],
}


class CodalExcelDownloadError(Exception):
    pass


class CodalExcelParseError(Exception):
    pass


def _normalize_label(value) -> str:
    """حذف نویسه‌های نیم‌فاصله/جهت‌دهی، نرمال‌سازی حروف عربی->فارسی، و فاصله‌ها."""
    if value is None:
        return ""
    s = str(value)
    s = s.replace("\u200c", "").replace("\u200f", "").replace("\u200e", "")
    # کدال از حروف عربی «ي»، «ى» و «ك» استفاده می‌کنه، نه معادل فارسی «ی» و «ک».
    # چشم این‌ها رو یکی می‌بینه ولی کدشون فرق داره - باید نرمالایز بشن.
    s = s.replace("\u064a", "\u06cc")  # ي عربی -> ی فارسی
    s = s.replace("\u0649", "\u06cc")  # ى الف مقصوره -> ی فارسی
    s = s.replace("\u0643", "\u06a9")  # ك عربی -> ک فارسی
    s = re.sub(r"\s+", "", s)
    return s.strip()


def parse_persian_number(raw) -> float | None:
    """
    تبدیل رشته‌ی عدد فارسی/عربی (با کاما، پرانتز برای منفی) به float.
    مقدار خالی یا غیرقابل‌تفسیر -> None (نه صفر، تا با «واقعاً صفر» اشتباه نشه).
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s or s.lower() == "nan":
        return None

    s = s.translate(_DIGIT_TRANS)

    negative = False
    if s.startswith("(") and s.endswith(")"):
        negative = True
        s = s[1:-1]

    s = s.replace(",", "").replace("٬", "").replace(" ", "")
    if s in ("", "-", "−", "ـ"):
        return None

    try:
        value = float(s)
    except ValueError:
        return None

    return -value if negative else value


def download_codal_excel(excel_url: str) -> bytes:
    try:
        resp = requests.get(excel_url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise CodalExcelDownloadError(f"خطا در دانلود فایل صورت مالی: {e}") from e
    return resp.content


BALANCE_SHEET_KEYS = ["total_assets", "total_liabilities", "total_equity"]
INCOME_STATEMENT_KEYS = ["revenue", "cogs", "gross_profit", "operating_profit", "net_profit", "eps_basic"]


def _extract_keys_from_table(df, keys) -> dict:
    """
    استخراج مقادیر یک دسته‌ی مشخص از قلم‌ها، فقط از داخل یک جدول واحد.

    نکته‌ی مهم: تطابق باید *دقیق و کامل* باشه، نه فقط شامل‌بودن (substring).
    مثلاً «جمع دارایی‌ها» نباید با «جمع دارایی‌های غیرجاری» (که یه
    زیرمجموعه است، نه جمع کل) قاطی بشه؛ substring matching این دو رو
    اشتباهی یکی می‌گرفت.
    """
    local = {}
    for _, row in df.iterrows():
        label_norm = _normalize_label(row.iloc[0])
        if not label_norm:
            continue
        for key in keys:
            if key in local:
                continue
            for pattern in TARGET_ITEMS[key]:
                if label_norm == pattern:
                    value = parse_persian_number(row.iloc[1])
                    if value is not None:
                        local[key] = value
                    break
    return local


def _find_consistent_balance_sheet(tables) -> tuple[dict, int | None]:
    """
    صورت مالی کدال معمولاً هم نسخه‌ی تلفیقی و هم نسخه‌ی شرکت اصلی رو
    توی یک فایل داره - نباید ردیف‌هاشون رو قاطی کرد. این تابع هر جدول
    رو جدا بررسی می‌کنه و فقط جدولی رو قبول می‌کنه که در اون
    «دارایی‌ها = بدهی‌ها + حقوق صاحبان سهام» (اتحاد حسابداری) برقرار باشه.
    اولین جدول معتبر (که معمولاً نسخه‌ی تلفیقی/کل گروه است) انتخاب می‌شه.
    """
    for i, df in enumerate(tables):
        if df.shape[1] < 2:
            continue
        local = _extract_keys_from_table(df, BALANCE_SHEET_KEYS)
        if len(local) == 3:
            assets = local["total_assets"]
            liabilities = local["total_liabilities"]
            equity = local["total_equity"]
            if assets == 0:
                continue
            diff_ratio = abs(assets - (liabilities + equity)) / abs(assets)
            if diff_ratio <= 0.01:  # ۱٪ تلورانس برای رند شدن
                return local, i
    return {}, None


def _find_consistent_income_statement(tables) -> tuple[dict, int | None]:
    """
    مشابه ترازنامه: سود ناخالص باید تقریباً برابر با درآمد + بهای تمام‌شده
    باشه (بهای تمام‌شده به‌صورت منفی ذخیره شده). اولین جدولی که این اتحاد
    توش برقراره رو انتخاب می‌کنیم تا مطمئن بشیم همه‌ی اقلام از یک صورت
    سود‌وزیان واحد میان (نه قاطی تلفیقی/اصلی).
    """
    for i, df in enumerate(tables):
        if df.shape[1] < 2:
            continue
        local = _extract_keys_from_table(df, INCOME_STATEMENT_KEYS)
        if "revenue" in local and "cogs" in local and "gross_profit" in local:
            expected_gross = local["revenue"] + local["cogs"]  # cogs منفیه
            actual_gross = local["gross_profit"]
            if actual_gross == 0:
                continue
            diff_ratio = abs(expected_gross - actual_gross) / abs(actual_gross)
            if diff_ratio <= 0.01:
                return local, i
    return {}, None


def parse_financial_statement(html_bytes: bytes) -> dict:
    """
    ورودی: محتوای خام فایل (که واقعاً HTML است).
    خروجی: دیکشنری قلم‌های مالی که پیدا شدن (مقادیر پیدانشده None می‌مونن)
    + یه فیلد 'found_items' برای شفافیت این‌که کدوم قلم‌ها واقعاً استخراج شدن.

    نکته‌ی مهم: ترازنامه و صورت سود‌وزیان هرکدوم از یک جدول *واحد و
    درونی-سازگار* استخراج می‌شن (نه با گشتن آزاد در کل فایل)، چون فایل
    کدال معمولاً چند نسخه (تلفیقی/شرکت اصلی) از هر صورت مالی داره و
    قاطی کردن ردیف‌هاشون عدد غلط می‌ده.
    """
    try:
        tables = pd.read_html(html_bytes)
    except (ValueError, ImportError) as e:
        raise CodalExcelParseError(f"هیچ جدولی در فایل پیدا نشد: {e}") from e

    result = {key: None for key in TARGET_ITEMS}
    found_items = set()
    source_tables = {}

    bs_values, bs_table_idx = _find_consistent_balance_sheet(tables)
    for key, value in bs_values.items():
        result[key] = value
        found_items.add(key)
    if bs_table_idx is not None:
        source_tables["balance_sheet_table_index"] = bs_table_idx

    is_values, is_table_idx = _find_consistent_income_statement(tables)
    for key, value in is_values.items():
        result[key] = value
        found_items.add(key)
    if is_table_idx is not None:
        source_tables["income_statement_table_index"] = is_table_idx

    # اقلامی که هنوز پیدا نشدن (مثل جریان نقد عملیاتی) رو با جست‌وجوی
    # سراسری (بدون چک اتحاد حسابداری، چون تنها یک قلمه) امتحان می‌کنیم
    remaining_keys = [k for k in TARGET_ITEMS if k not in found_items]
    for df in tables:
        if not remaining_keys:
            break
        if df.shape[1] < 2:
            continue
        local = _extract_keys_from_table(df, remaining_keys)
        for key, value in local.items():
            result[key] = value
            found_items.add(key)
            remaining_keys.remove(key)

    return {
        "metrics": result,
        "found_items": sorted(found_items),
        "missing_items": sorted(set(TARGET_ITEMS.keys()) - found_items),
        "tables_scanned": len(tables),
        "source_tables": source_tables,
    }


def fetch_and_parse(excel_url: str) -> dict:
    """تابع سطح‌بالا: دانلود + پارس در یک مرحله."""
    content = download_codal_excel(excel_url)
    return parse_financial_statement(content)
