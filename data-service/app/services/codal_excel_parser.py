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
import json
import re
from io import StringIO
import requests
import pandas as pd
from bs4 import BeautifulSoup

from app.config import HTTP_USER_AGENT

HEADERS = {"User-Agent": HTTP_USER_AGENT}

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_INDIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
ASCII_DIGITS = "0123456789"
_DIGIT_TRANS = str.maketrans(PERSIAN_DIGITS + ARABIC_INDIC_DIGITS, ASCII_DIGITS + ASCII_DIGITS)
JALALI_DATE_RE = re.compile(r"(?<!\d)(14\d{2})[\-/](\d{1,2})[\-/](\d{1,2})(?!\d)")
PERIOD_MONTHS_RE = re.compile(r"(?:دوره\s*)?([0-9۰-۹٠-٩]{1,2})\s*ماهه")
# Codal sometimes returns a parent issuer's notices together with separate
# financial statements filed for named subsidiaries.  The trailing entity
# qualifier is explicit evidence that the document is not the parent report.
CHILD_ENTITY_TITLE_RE = re.compile(r"\(\s*(?:شرکت|موسسه)\s+[^()]+\s*\)\s*$")

# قلم‌های هدف: کلید داخلی -> لیستی از برچسب‌های محتمل فارسی (بعد از نرمال‌سازی، بدون فاصله)
TARGET_ITEMS = {
    "revenue": [
        "درآمدهایعملیاتی",
        "درآمدعملیاتی",
        "جمعدرآمدهایعملیاتی",
        # Insurance statements use this exact total instead of the generic
        # operating-revenue label.
        "درآمدهایبیمه‌ای",
        "درآمدهایبیمه ای",
        "درآمدهایبیمهای",
    ],
    "cogs": ["بهایتمامشدهدرآمدهایعملیاتی"],
    "gross_profit": ["سود(زیان)ناخالص", "سودناخالص"],
    "operating_profit": ["سود(زیان)عملیاتی", "سودعملیاتی"],
    "net_profit": ["سود(زیان)خالص", "سودخالص"],
    "eps_basic": ["سود(زیان)پایههرسهم", "سودپایههرسهم", "سودهرسهم"],
    "total_assets": ["جمعدارایی‌ها", "جمعداراییها", "جمعکلدارایی‌ها"],
    "total_liabilities": ["جمعبدهی‌ها", "جمعبدهیها"],
    "total_equity": ["جمعحقوقصاحبانسهام", "جمعحقوقمالکانه"],
    # Fund net-asset statements publish this as a dedicated per-unit row.
    "nav_per_share": [
        "خالصداراییهایهرواحدسرمایهگذاری",
        "خالصداراییهرواحدسرمایهگذاری",
        # Fund financial statements often publish ending units and unit price
        # together; the second numeric cell is the official NAV per unit.
        "خالصداراییها(واحدهایسرمایهگذاری)پایاندوره",
    ],
    "operating_cash_flow": [
        "خالصجریانهایوجهنقدحاصلازفعالیتهایعملیاتی",
        "خالصجریانهاینقدیحاصلازفعالیتهایعملیاتی",
        "خالصجریانهایوجهنقدناشیازفعالیتهایعملیاتی",
        "خالصجریانهاینقدیناشیازفعالیتهایعملیاتی",
        "جریانخالصوجهنقدحاصلازفعالیت‌هایعملیاتی",
        "جریانخالصوجهنقدحاصلازفعالیتهایعملیاتی",
        "جریانخالصوجهنقدناشیازفعالیت‌هایعملیاتی",
        "جریانخالصوجهنقدناشیازفعالیتهایعملیاتی",
        "جریانخالصورود(خروج)نقدحاصلازفعالیتهایعملیاتی",
        "جریانخالصورود(خروج)نقدناشیازفعالیتهایعملیاتی",
    ],
    "capital_expenditure": [
        "خریدداراییهایثابت",
        "خریدداراییهایثابتومشهود",
        "پرداختبابتخریدداراییهایثابت",
        "خریدداراییهایثابتومشهود",
    ],
    "net_borrowing": [
        "دریافت(پرداخت)تسهیلات",
        "خالصدریافت(پرداخت)تسهیلات",
        "جریانخالصدریافت(پرداخت)تسهیلات",
        "خالصجریاننقدیازفعالیتهای تامینمالی",
    ],
    "units_outstanding": [
        "تعدادواحدهایدرپایاندوره",
        "تعدادواحدهایدرپایانعملکرد",
        "تعدادواحدهایدرپایانسالمالی",
        "تعدادواحدهایدرصندوق",
        "خالصداراییها(واحدهایسرمایهگذاری)پایاندوره",
    ],
}

# FCFE components must be built only from explicit rows in one cash-flow
# table.  In Codal's current template, capital purchases are split between
# tangible and intangible assets, while borrowing is split between proceeds
# and principal repayments.  Interest and loans granted to third parties are
# deliberately excluded.
CAPEX_TANGIBLE_LABELS = {
    "پرداختهاینقدیبرایخریدداراییهایثابتمشهود",
    "پرداختهاینقدیبابتخریدداراییهایثابتمشهود",
    "وجوهپرداختیبابتتحصیلداراییهایثابتمشهود",
}
CAPEX_INTANGIBLE_LABELS = {
    "پرداختهاینقدیبرایخریدداراییهاینامشهود",
    "پرداختهاینقدیبرایخریدداراییهایثابتنامشهود",
    "پرداختهاینقدیبابتخریدداراییهاینامشهود",
    "پرداختهاینقدیبابتخریدداراییهایثابتنامشهود",
    "وجوهپرداختیبابتتحصیلداراییهاینامشهود",
    "وجوهپرداختیبابتتحصیلداراییهایثابتنامشهود",
}
BORROWING_PROCEEDS_LABELS = {
    "دریافتهاینقدیحاصلازتسهیلات",
    "دریافتهاینقدیحاصلازتسهیلات(غیرعملیاتی)",
}
BORROWING_PRINCIPAL_LABELS = {
    "پرداختهاینقدیبابتاصلتسهیلات",
    "پرداختهاینقدیبابتاصلتسهیلات(غیرعملیاتی)",
}


class CodalExcelDownloadError(Exception):
    pass


class CodalExcelParseError(Exception):
    pass


def extract_period_end_jalali(title: str | None) -> str | None:
    """Return an explicit Persian report end date; never infer a date from the publish date."""
    if not title:
        return None
    normalized = str(title).translate(_DIGIT_TRANS)
    match = JALALI_DATE_RE.search(normalized)
    if not match:
        return None
    year, month, day = (int(part) for part in match.groups())
    if not (1400 <= year <= 1499 and 1 <= month <= 12 and 1 <= day <= 31):
        return None
    return f"{year:04d}/{month:02d}/{day:02d}"


def extract_period_length_months(title: str | None) -> int | None:
    """Extract the report's stated period length, independent of search dates."""
    if not title:
        return None
    normalized = str(title).translate(_DIGIT_TRANS)
    match = PERIOD_MONTHS_RE.search(normalized)
    if match:
        months = int(match.group(1))
        if 1 <= months <= 60:
            return months
    if "سال مالی" in normalized or "سالانه" in normalized:
        return 12
    return None


def has_child_entity_qualifier(title: str | None) -> bool:
    """Return whether a financial-statement title names a child entity."""
    if not title:
        return False
    normalized = str(title).replace("\u200c", " ").strip()
    return bool(CHILD_ENTITY_TITLE_RE.search(normalized))


def derive_period_start_jalali(period_end: str | None, length_months: int | None) -> str | None:
    """Derive the accounting-period start from the official end and length."""
    if not period_end or not length_months or length_months < 1:
        return None
    try:
        year, month, _day = (int(part) for part in period_end.split('/'))
    except (AttributeError, TypeError, ValueError):
        return None
    if not (1400 <= year <= 1499 and 1 <= month <= 12):
        return None
    start_index = year * 12 + (month - 1) - int(length_months) + 1
    start_year, start_month_zero = divmod(start_index, 12)
    return f"{start_year:04d}/{start_month_zero + 1:02d}/01"


def _normalize_label(value) -> str:
    """حذف نویسه‌های نیم‌فاصله/جهت‌دهی، نرمال‌سازی حروف عربی->فارسی، و فاصله‌ها."""
    if value is None:
        return ""
    s = str(value)
    s = s.replace("\u200c", "").replace("\u200f", "").replace("\u200e", "").replace("\u00ad", "")
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
        # Some Codal statements render two sub-statements side by side. In
        # those tables the label/value pair can begin at any cell, not only
        # at columns 0/1. Scan adjacent cells while keeping the exact-label
        # match and the first numeric value policy.
        for index in range(max(0, len(row) - 1)):
            label_norm = _normalize_label(row.iloc[index])
            if not label_norm:
                continue
            for key in keys:
                if key in local:
                    continue
                if label_norm in TARGET_ITEMS[key]:
                    value_index = index + 1
                    if key == "nav_per_share" and label_norm == "خالصداراییها(واحدهایسرمایهگذاری)پایاندوره":
                        value_index = index + 2
                    if value_index >= len(row):
                        continue
                    value = parse_persian_number(row.iloc[value_index])
                    if key == "nav_per_share" and value == 0:
                        # A zero NAV is not a usable fund unit price. Some
                        # statements contain an unrelated zero row with the
                        # same normalized label before the ending NAV table.
                        continue
                    if value is not None:
                        local[key] = value
    return local


def _extract_fcfe_components_from_table(df) -> dict:
    """Extract complete FCFE components from explicit rows of one table."""
    tangible = {}
    intangible = {}
    proceeds = {}
    principal = {}
    for _, row in df.iterrows():
        for index in range(max(0, len(row) - 1)):
            label = _normalize_label(row.iloc[index])
            if not label:
                continue
            value = parse_persian_number(row.iloc[index + 1])
            if value is None:
                continue
            if label in CAPEX_TANGIBLE_LABELS:
                tangible[label] = value
            elif label in CAPEX_INTANGIBLE_LABELS:
                intangible[label] = value
            elif label in BORROWING_PROCEEDS_LABELS:
                proceeds[label] = value
            elif label in BORROWING_PRINCIPAL_LABELS:
                principal[label] = value

    result = {}
    # Requiring both asset classes prevents an omitted row from being silently
    # treated as zero.  Explicit zero cells remain valid evidence.
    if tangible and intangible:
        result["capital_expenditure"] = sum(tangible.values()) + sum(intangible.values())
    # Net borrowing excludes interest and lending to third parties.  Both
    # proceeds and principal repayment rows must be present, including zeros.
    if proceeds and principal:
        result["net_borrowing"] = sum(proceeds.values()) + sum(principal.values())
    return result


def _value_column_period(df) -> str | None:
    """Extract the explicit period attached to the first numeric value column."""
    if df.shape[1] < 2:
        return None
    column = df.columns[1]
    text = ' '.join(str(part) for part in column) if isinstance(column, tuple) else str(column)
    return extract_period_end_jalali(text)


def _read_html_tables_resilient(source):
    """Read usable Codal tables even when one legacy table is malformed."""
    try:
        return pd.read_html(source)
    except (ValueError, ImportError, IndexError):
        if isinstance(source, StringIO):
            html = source.getvalue()
        elif isinstance(source, (bytes, bytearray)):
            html = source.decode("utf-8", errors="replace")
        else:
            html = str(source)
        tables = []
        for table in BeautifulSoup(html, "html.parser").find_all("table"):
            try:
                tables.extend(pd.read_html(StringIO(str(table))))
            except (ValueError, ImportError, IndexError):
                continue
        if tables:
            return tables
        raise


def _read_embedded_datasource_tables(html_bytes: bytes) -> list:
    """Read hidden Codal statement sheets embedded in the HTML datasource JSON."""
    if not isinstance(html_bytes, (bytes, bytearray)):
        return []
    html = html_bytes.decode("utf-8", errors="replace")
    marker = "var datasource ="
    start = html.find(marker)
    if start < 0:
        return []
    payload = html[start + len(marker):].lstrip()
    try:
        datasource, _ = json.JSONDecoder().raw_decode(payload)
    except json.JSONDecodeError:
        return []

    tables = []
    for sheet in datasource.get("sheets", []):
        sheet_title = _normalize_label(sheet.get("title_Fa"))
        for table in sheet.get("tables", []):
            rows = {}
            for cell in table.get("cells", []):
                if not cell.get("isVisible", True):
                    continue
                row = cell.get("rowSequence")
                column = cell.get("columnSequence")
                if row is None or column is None:
                    continue
                rows.setdefault(row, {})[column] = cell.get("value")
            if not rows:
                continue
            width = max(max(values) for values in rows.values())
            frame = pd.DataFrame(
                [[values.get(column) for column in range(1, width + 1)] for _, values in sorted(rows.items())]
            )
            # Keep the originating sheet visible to the caller through the
            # table metadata used by the normal statement selectors.
            frame.attrs["codal_sheet_title"] = sheet_title
            frame.attrs["codal_table_title"] = _normalize_label(table.get("title_Fa"))
            tables.append(frame)
    return tables


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
        # Some Codal HTML reports are UTF-8, but pandas may interpret raw
        # bytes using a legacy encoding and turn Persian labels into mojibake.
        # Decode explicitly when possible; the bytes fallback keeps support
        # for older/non-UTF-8 Excel framesets.
        source = html_bytes
        if isinstance(html_bytes, (bytes, bytearray)):
            try:
                source = StringIO(html_bytes.decode("utf-8"))
            except UnicodeDecodeError:
                source = html_bytes
        tables = _read_embedded_datasource_tables(html_bytes)
        # Legacy Excel-compatible files have no datasource JSON; retain the
        # resilient table reader as the fallback for those documents.
        if not tables:
            tables = _read_html_tables_resilient(source)
    except (ValueError, ImportError, IndexError) as e:
        raise CodalExcelParseError(f"هیچ جدولی در فایل پیدا نشد: {e}") from e

    result = {key: None for key in TARGET_ITEMS}
    found_items = set()
    source_tables = {}
    source_periods = {}

    bs_values, bs_table_idx = _find_consistent_balance_sheet(tables)
    for key, value in bs_values.items():
        result[key] = value
        found_items.add(key)
    if bs_table_idx is not None:
        source_tables["balance_sheet_table_index"] = bs_table_idx
        source_periods["balance_sheet"] = _value_column_period(tables[bs_table_idx])

    is_values, is_table_idx = _find_consistent_income_statement(tables)
    for key, value in is_values.items():
        result[key] = value
        found_items.add(key)
    if is_table_idx is not None:
        source_tables["income_statement_table_index"] = is_table_idx
        source_periods["income_statement"] = _value_column_period(tables[is_table_idx])

    # Preserve the existing first-cash-flow-table policy and derive FCFE
    # components only from that same table.  This avoids mixing consolidated,
    # separate, current-period, or comparative statements.
    for i, df in enumerate(tables):
        if df.shape[1] < 2:
            continue
        operating = _extract_keys_from_table(df, ["operating_cash_flow"])
        if "operating_cash_flow" not in operating:
            continue
        result["operating_cash_flow"] = operating["operating_cash_flow"]
        found_items.add("operating_cash_flow")
        for key, value in _extract_fcfe_components_from_table(df).items():
            result[key] = value
            found_items.add(key)
        source_tables["cash_flow_table_index"] = i
        source_periods["cash_flow"] = _value_column_period(df)
        break

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
        "source_periods": source_periods,
    }


def fetch_and_parse(excel_url: str) -> dict:
    """تابع سطح‌بالا: دانلود + پارس در یک مرحله."""
    content = download_codal_excel(excel_url)
    return parse_financial_statement(content)
