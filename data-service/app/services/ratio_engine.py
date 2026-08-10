"""
موتور محاسبه‌ی نسبت‌های مالی.

برخلاف کد اولیه‌ی سایت (financialEngine.ts) که همه‌چیز رو هاردکد می‌کرد،
اینجا هر نسبت واقعاً از روی اعداد پارس‌شده از صورت مالی محاسبه می‌شه.
اگه قلم لازم برای یه نسبت موجود نباشه، همون نسبت None می‌مونه - به‌جای
اینکه یه عدد ساختگی جایگزینش کنیم.

واحدها: صورت مالی کدال معمولاً به میلیون ریال گزارش می‌شه. برای نسبت‌های
داخلی (ROE، ROA، حاشیه سود، نسبت بدهی) چون همه از خود صورت مالی میان،
مشکلی با واحد نیست (صورت‌کسر و مخرج هر دو میلیون ریال‌اند و خنثی می‌شن).
"""


def _safe_div(numerator, denominator):
    if numerator is None or denominator is None:
        return None
    if denominator == 0:
        return None
    return numerator / denominator


def _pct(ratio):
    if ratio is None:
        return None
    return round(ratio * 100, 2)


def compute_ratios(financial_metrics: dict, live_pe_ratio: float | None = None) -> dict:
    """
    ورودی:
      financial_metrics: خروجی metrics از codal_excel_parser (revenue, cogs,
        gross_profit, operating_profit, net_profit, total_assets,
        total_liabilities, total_equity, operating_cash_flow, eps_basic)
      live_pe_ratio: نسبت P/E لحظه‌ای از تستمسی/BrsApi (اختیاری)

    خروجی: دیکشنری نسبت‌های محاسبه‌شده. هر نسبتی که به‌خاطر نبود داده
    قابل‌محاسبه نباشه، None می‌مونه (نه یه عدد جعلی).
    """
    m = financial_metrics

    revenue = m.get("revenue")
    gross_profit = m.get("gross_profit")
    operating_profit = m.get("operating_profit")
    net_profit = m.get("net_profit")
    total_assets = m.get("total_assets")
    total_liabilities = m.get("total_liabilities")
    total_equity = m.get("total_equity")
    operating_cash_flow = m.get("operating_cash_flow")

    gross_margin = _pct(_safe_div(gross_profit, revenue))
    operating_margin = _pct(_safe_div(operating_profit, revenue))
    net_margin = _pct(_safe_div(net_profit, revenue))

    roe = _pct(_safe_div(net_profit, total_equity))
    roa = _pct(_safe_div(net_profit, total_assets))

    debt_ratio = _pct(_safe_div(total_liabilities, total_assets))
    debt_to_equity = _safe_div(total_liabilities, total_equity)
    if debt_to_equity is not None:
        debt_to_equity = round(debt_to_equity, 2)

    cash_to_profit_ratio = _pct(_safe_div(operating_cash_flow, net_profit))

    earnings_yield = None
    if live_pe_ratio and live_pe_ratio > 0:
        earnings_yield = round(100 / live_pe_ratio, 2)

    return {
        "gross_margin_percent": gross_margin,
        "operating_margin_percent": operating_margin,
        "net_margin_percent": net_margin,
        "roe_percent": roe,
        "roa_percent": roa,
        "debt_ratio_percent": debt_ratio,
        "debt_to_equity": debt_to_equity,
        "cash_to_profit_ratio_percent": cash_to_profit_ratio,
        "pe_ratio": live_pe_ratio,
        "earnings_yield_percent": earnings_yield,
    }


def evaluate_health_status(ratios: dict, industry_category: str | None = None) -> dict:
    """
    یه ارزیابی ساده و شفاف بر پایه‌ی نسبت‌های واقعی - نه امتیاز رمزآلود
    بلکه یه سری علامت (flag) با توضیح روشن برای هرکدوم، تا کاربر بفهمه
    ارزیابی از کجا اومده.

    نکته‌ی مهم: آستانه‌ها بین شرکت‌های مالی (بانک/بیمه/واسطه‌گری مالی) و
    شرکت‌های عادی (تولیدی/خدماتی) خیلی فرق می‌کنه. مثلاً نسبت بدهی ۸۸٪
    برای یه بانک کاملاً طبیعیه (چون سپرده‌ی مشتریان جزو بدهی حساب می‌شه)
    ولی برای یه شرکت تولیدی نشونه‌ی ریسک بالاست. اگه این تفاوت رو در نظر
    نگیریم، ارزیابی برای شرکت‌های مالی گمراه‌کننده می‌شه.

    این تابع توصیه‌ی خرید/فروش نمی‌ده - فقط وضعیت نسبت‌ها رو نسبت به
    آستانه‌های عمومی و شناخته‌شده‌ی تحلیل بنیادی توصیف می‌کنه.
    """
    FINANCIAL_CATEGORIES = {
        "بانک‌ها و موسسات اعتباری",
        "بیمه و صندوق بازنشستگی به جز تامین اجتماعی",
        "سایر واسطه‌گری‌های مالی",
        "فعالیت‌های کمکی به نهادهای مالی واسط",
    }
    is_financial = (industry_category or "").strip() in FINANCIAL_CATEGORIES

    flags = []

    # --- ROE: آستانه‌ها برای بانک/بیمه و شرکت‌های عادی مشترکه (ROE بالا همیشه خوبه) ---
    roe = ratios.get("roe_percent")
    if roe is not None:
        if roe >= 20:
            flags.append({"key": "roe", "label": "بازده حقوق صاحبان سهام", "value": f"{roe}%", "note": "بالا"})
        elif roe >= 10:
            flags.append({"key": "roe", "label": "بازده حقوق صاحبان سهام", "value": f"{roe}%", "note": "متوسط"})
        else:
            flags.append({"key": "roe", "label": "بازده حقوق صاحبان سهام", "value": f"{roe}%", "note": "پایین"})

    # --- ROA: برای شرکت‌های مالی چون دارایی‌ها خیلی بزرگ‌اند (سپرده‌ها)، آستانه پایین‌تره ---
    roa = ratios.get("roa_percent")
    if roa is not None:
        if is_financial:
            if roa >= 1.5:
                note = "خوب (برای یک نهاد مالی)"
            elif roa >= 0.5:
                note = "متوسط (برای یک نهاد مالی)"
            else:
                note = "پایین (برای یک نهاد مالی)"
        else:
            if roa >= 10:
                note = "خوب"
            elif roa >= 5:
                note = "متوسط"
            else:
                note = "پایین"
        flags.append({"key": "roa", "label": "بازده دارایی‌ها", "value": f"{roa}%", "note": note})

    # --- نسبت بدهی: تفاوت اصلی بین شرکت مالی و غیرمالی همینجاست ---
    debt_ratio = ratios.get("debt_ratio_percent")
    if debt_ratio is not None:
        if is_financial:
            # بانک/بیمه ذاتاً بدهی خیلی بالا دارن (سپرده = بدهی)؛ آستانه‌ها بر همین اساس
            if debt_ratio <= 92:
                note = "طبیعی برای یک نهاد مالی"
            elif debt_ratio <= 96:
                note = "کمی بالاتر از میانگین صنعت مالی"
            else:
                note = "بالا حتی برای استاندارد صنعت مالی"
        else:
            if debt_ratio <= 40:
                note = "کم‌ریسک"
            elif debt_ratio <= 65:
                note = "متوسط"
            else:
                note = "بالا/پرریسک"
        flags.append({"key": "debt", "label": "نسبت بدهی", "value": f"{debt_ratio}%", "note": note})

    cash_ratio = ratios.get("cash_to_profit_ratio_percent")
    if cash_ratio is not None:
        if cash_ratio >= 80:
            flags.append({"key": "cash_quality", "label": "کیفیت نقدینگی سود", "value": f"{cash_ratio}%", "note": "خوب"})
        elif cash_ratio >= 40:
            flags.append({"key": "cash_quality", "label": "کیفیت نقدینگی سود", "value": f"{cash_ratio}%", "note": "متوسط"})
        else:
            flags.append({"key": "cash_quality", "label": "کیفیت نقدینگی سود", "value": f"{cash_ratio}%", "note": "نیازمند بررسی بیشتر"})

    return {"flags": flags, "industry_classified_as": "مالی (بانک/بیمه/واسطه‌گری)" if is_financial else "عادی (تولیدی/خدماتی/سایر)"}
