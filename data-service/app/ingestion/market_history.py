from __future__ import annotations

from datetime import date
from typing import Iterable


PILOT_INDUSTRIES = {
    "فلزات اساسی": "metals",
    "استخراج کانه های فلزی": "metals",
    "محصولات شیمیایی": "petrochemical",
    "فرآورده های نفتی، کک و سوخت هسته ای": "refinery",
    "فرآورده‌های نفتی، کک و سوخت هسته‌ای": "refinery",
    "بانک‌ها و موسسات اعتباری": "bank",
    "بانک ها و موسسات اعتباری": "bank",
    "سیمان، آهک و گچ": "cement",
    "مواد و محصولات دارویی": "pharmaceutical",
    "انبوه سازی، املاک و مستغلات": "real_estate",
    "کاشی و سرامیک": "ceramics",
    "محصولات غذایی و آشامیدنی به جز قند و شکر": "food",
    "شرکت های چند رشته ای صنعتی": "holding",
}

# These are authoritative operating-industry labels for which the valuation
# layer has an explicit conservative policy scenario (`general-v1`). Keep the
# list finite: an unknown or malformed label must remain unclassified.
GENERAL_INDUSTRIES = {
    "خودرو و ساخت قطعات",
    "قند و شکر",
    "زراعت و خدمات وابسته",
    "رایانه و فعالیت های وابسته به آن",
    "حمل و نقل، انبارداری و ارتباطات",
    "ماشین آلات و دستگاه های برقی",
    "ماشین آلات و تجهیزات",
    "عرضه برق، گاز، بخار و آب گرم",
    "ساخت محصولات فلزی",
    "محصولات کاغذی",
    "منسوجات",
    "سایر محصولات کانی غیرفلزی",
    "اطلاعات و ارتباطات",
    "تجارت عمده فروشی به جز وسایل نقلیه موتوری",
    "تولید محصولات کامپیوتری الکترونیکی و نوری",
    "حمل و نقل آبی",
    "خدمات فنی و مهندسی",
    "خرده فروشی، به استثنای وسایل نقلیه موتوری",
    "دباغی، پرداخت چرم و ساخت انواع پاپوش",
    "ساخت دستگاه ها و وسایل ارتباطی",
    "فعالیت مهندسی، تجزیه، تحلیل و آزمایش فنی",
    "فعالیت های فرهنگی و ورزشی",
    "فعالیت های هنری، سرگرمی و خلاقانه",
    "محصولات چوبی",
    "مخابرات",
    "هتل و رستوران",
    "پیمانکاری صنعتی",
}

ETF_INDUSTRY_MARKER = "صندوق سرمایه گذاری قابل معامله"


def normalize_persian(value: str | None) -> str:
    return " ".join(
        (value or "")
        .replace("ي", "ی")
        .replace("ك", "ک")
        .replace("ۀ", "ه")
        .replace("ة", "ه")
        .replace("\u200c", " ")
        .split()
    )


def model_family(industry: str | None) -> str:
    normalized = normalize_persian(industry)
    mapped = PILOT_INDUSTRIES.get(normalized)
    if mapped:
        return mapped
    if ETF_INDUSTRY_MARKER in normalized:
        return "fund"
    if not normalized:
        return "unclassified"
    if any(token in normalized for token in ("بانک", "اعتباری", "بیمه", "سرمایه گذاری", "واسطه گری", "نهادهای مالی واسط")):
        return "financial"
    if normalized == "استخراج سایر معادن":
        return "metals"
    if any(token in normalized for token in ("املاک", "انبوه سازی", "ساختمان")):
        return "real_estate"
    if any(token in normalized for token in ("نفت", "گاز", "پتروشیمی", "شیمیایی", "کک", "پلاستیک", "لاستیک")):
        return "petrochemical"
    if any(token in normalized for token in ("فلز", "کانه", "معدن", "زغال", "سیمان", "کانی", "سرامیک", "کاشی")):
        return "metals"
    if normalized in GENERAL_INDUSTRIES:
        return "general"
    # Do not manufacture a valuation model for an industry that has not been
    # explicitly mapped. Callers must surface INSUFFICIENT_DATA instead.
    return "unclassified"


def is_pilot_industry(industry: str | None) -> bool:
    return model_family(industry) != "unclassified"


def gregorian_to_jalali(value: date) -> tuple[int, int, int]:
    gy, gm, gd = value.year, value.month, value.day
    g_days = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = (
        355666
        + 365 * gy
        + (gy2 + 3) // 4
        - (gy2 + 99) // 100
        + (gy2 + 399) // 400
        + gd
        + g_days[gm - 1]
    )
    jy = -1595 + 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm, jd = 1 + days // 31, 1 + days % 31
    else:
        jm, jd = 7 + (days - 186) // 30, 1 + (days - 186) % 30
    return jy, jm, jd


def jalali_iso(value: date) -> str:
    jy, jm, jd = gregorian_to_jalali(value)
    return f"{jy:04d}-{jm:02d}-{jd:02d}"


def jalali_to_gregorian(jy: int, jm: int, jd: int) -> date:
    jy += 1595
    days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
    days += (jm - 1) * 31 if jm < 7 else ((jm - 7) * 30) + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        gy += 100 * ((days - 1) // 36524)
        days = (days - 1) % 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0)
    month_days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    for length in month_days:
        if gd <= length:
            break
        gd -= length
        gm += 1
    return date(gy, gm, gd)


def filter_history(rows: Iterable[dict], start: date) -> list[dict]:
    floor = int(start.strftime("%Y%m%d"))
    return [row for row in rows if int(row.get("dEven") or 0) >= floor]
