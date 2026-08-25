import hashlib
import json
from datetime import datetime, timedelta, timezone

from app.analytics.engine import Policy, core_questions, decide
from app.analytics.industry_valuation import health_score, value_company
from app.ingestion.market_history import model_family


REQUIRED_METRICS = (
    "revenue",
    "net_profit",
    "operating_cash_flow",
    "total_assets",
    "total_liabilities",
    "total_equity",
    "eps_basic",
)


def build_snapshot_payload(raw: dict, report_mode: str, policy: Policy = Policy()) -> dict:
    metrics = raw.get("financial_metrics") or {}
    ratios = raw.get("ratios") or {}
    live = raw.get("live_price") or {}
    present = sum(metrics.get(key) is not None for key in REQUIRED_METRICS)
    coverage = round(present / len(REQUIRED_METRICS) * 100, 2)
    missing_metrics = [key for key in REQUIRED_METRICS if metrics.get(key) is None]
    data_status = "READY" if not missing_metrics else "PARTIAL_DATA"

    report = raw.get("report_used") or {}
    title = str(report.get("title") or "")
    audited = "حسابرسی شده" in title and "حسابرسی نشده" not in title
    confidence = 70.0 if audited else 55.0
    if raw.get("live_price_error"):
        confidence -= 10
    if raw.get("financial_metrics_missing"):
        confidence -= min(20, len(raw["financial_metrics_missing"]) * 3)
    confidence = max(0.0, round(confidence, 2))

    references = raw.get("references") or {}
    bank_rate = references.get("bankDepositRate")
    inflation = references.get("inflationRate")
    context = raw.get("analysis_context") or {}
    comparison = raw.get("period_comparison") or {}
    family = model_family(live.get("market_category"))
    periods_available = int(context.get("financial_periods") or 0)
    return_90d = context.get("price_return_90d_percent")
    return_365d = context.get("price_return_365d_percent")
    # In a high-inflation market, a 50% annual nominal move is not exceptional.
    # Reserve the guard for genuinely abrupt moves: 50% in 90 days or 100%
    # over a year. Thresholds are explicit policy, never inferred per symbol.
    strong_price_momentum = bool(
        (return_90d is not None and return_90d >= 50)
        or (return_365d is not None and return_365d >= 100)
    )
    incomplete_trend_data = bool(context) and periods_available < 2
    unmodeled_monthly_activity = bool(
        context.get("monthly_disclosures") and not context.get("monthly_signals_available")
    )
    market_fundamental_divergence = strong_price_momentum and (
        incomplete_trend_data or unmodeled_monthly_activity
    )
    current_profit = comparison.get("current_net_profit")
    previous_profit = comparison.get("previous_net_profit")
    revenue_growth = comparison.get("revenue_growth_percent")
    profit_growth = comparison.get("net_profit_growth_percent")
    monthly_activity = raw.get("monthly_activity") or {}
    monthly_growth = (monthly_activity.get("monthlySales") or {}).get("growthPercent")
    if monthly_growth is None:
        monthly_growth = (monthly_activity.get("ytdSales") or {}).get("growthPercent")
    operating_margin = ratios.get("operating_margin_percent")
    net_margin = ratios.get("net_margin_percent")
    weak_profitability = bool(
        (operating_margin is not None and operating_margin < 5)
        or (net_margin is not None and net_margin < 5)
    )
    operating_company = family not in {"bank", "real_estate", "unclassified"}
    turnaround_candidate = bool(
        (current_profit is not None and current_profit > 0 and previous_profit is not None and previous_profit <= 0)
        or (operating_company and revenue_growth is not None and inflation is not None and revenue_growth > inflation
            and profit_growth is not None and profit_growth > 0)
        or (operating_company and weak_profitability and monthly_growth is not None
            and inflation is not None and monthly_growth > inflation)
    )
    capital_action_data_gap = bool(context.get("capital_action_data_gap"))
    if market_fundamental_divergence:
        confidence = min(confidence, 60.0)
    valuation = value_company(raw)
    valuation_family = valuation.get("family") if valuation else family
    score, dimensions = health_score(
        metrics,
        ratios,
        valuation_family,
        inflation,
        (raw.get("period_comparison") or {}).get("revenue_growth_percent"),
    )
    has_net_loss = bool(metrics.get("net_profit") is not None and metrics.get("net_profit") <= 0)
    has_nonpositive_equity = bool(metrics.get("total_equity") is not None and metrics.get("total_equity") <= 0)
    has_operating_loss = bool(metrics.get("operating_profit") is not None and metrics.get("operating_profit") <= 0)
    critical_warning = has_net_loss or has_nonpositive_equity or has_operating_loss
    # A normalized score based only on available positive dimensions can look
    # deceptively healthy while the latest statement contains a critical loss.
    # Keep the dimensions auditable, but cap the headline score consistently
    # with the mandatory SELL warning.
    if score is not None and critical_warning:
        score = min(score, 39.0)

    questions = core_questions(
        ttm_eps=metrics.get("eps_basic"),
        price=live.get("last_price") or live.get("closing_price"),
        pe=ratios.get("pe_ratio"),
        operating_cash_flow=metrics.get("operating_cash_flow"),
        net_profit=metrics.get("net_profit"),
        nominal_growth=(raw.get("period_comparison") or {}).get(
            "revenue_growth_percent"
        ),
        # Official, period-matched observations are intentionally not inferred.
        bank_rate=bank_rate,
        matched_inflation=inflation,
        policy=policy,
    )
    decision = decide(
        health_score=score,
        coverage=coverage,
        confidence=confidence,
        current_price=live.get("last_price") or live.get("closing_price"),
        fair_value_low=valuation.get("fairValueLow") if valuation else None,
        fair_value_base=valuation.get("fairValueBase") if valuation else None,
        fair_value_high=valuation.get("fairValueHigh") if valuation else None,
        critical_warning=critical_warning,
        industry_model_ready=valuation is not None,
        report_mode=report_mode,
        policy=policy,
    )
    if (market_fundamental_divergence or turnaround_candidate or capital_action_data_gap) and not critical_warning:
        decision = "INSUFFICIENT_DATA"
    analysis_state = (
        "CAPITAL_ACTION_DATA_GAP" if capital_action_data_gap else
        "MARKET_FUNDAMENTAL_DIVERGENCE" if market_fundamental_divergence else
        "TURNAROUND_CANDIDATE" if turnaround_candidate else
        "STANDARD"
    )
    now = datetime.now(timezone.utc)
    payload = {
        "symbol": raw.get("symbol"),
        "companyName": raw.get("company_name"),
        "reportMode": report_mode,
        "decision": decision,
        "healthScore": score,
        "healthDimensions": dimensions,
        "dataCoverage": coverage,
        "dataStatus": data_status,
        "missingMetrics": missing_metrics,
        "confidence": confidence,
        "valuation": valuation,
        "analysisState": analysis_state,
        "analysisContext": context,
        "monthlyActivity": monthly_activity,
        "references": {
            "bankDepositRate": bank_rate,
            "inflationRate": inflation,
        },
        "keyMetrics": {
            "eps": metrics.get("eps_basic"),
            "pe": ratios.get("pe_ratio"),
            "roe": ratios.get("roe_percent"),
            "roa": ratios.get("roa_percent"),
            "grossMargin": ratios.get("gross_margin_percent"),
            "operatingMargin": ratios.get("operating_margin_percent"),
            "netMargin": ratios.get("net_margin_percent"),
            "debtRatio": ratios.get("debt_ratio_percent"),
            "cashToProfit": ratios.get("cash_to_profit_ratio_percent"),
            "revenueGrowth": (raw.get("period_comparison") or {}).get("revenue_growth_percent"),
            "netProfitGrowth": (raw.get("period_comparison") or {}).get("net_profit_growth_percent"),
        },
        "report": {
            "title": report.get("title"),
            "publishedAt": report.get("publish_datetime"),
            "periodEnd": report.get("period_end"),
            "periodLengthMonths": report.get("period_length_months"),
            "audited": audited,
            "basisNote": (
                "این تحلیل بر اساس آخرین صورت مالی موجود و قابل‌استخراج تهیه شده است؛ اطلاعیه‌های جدیدترِ غیرمالی جایگزین صورت مالی نمی‌شوند. گزارش حسابرسی‌نشده است و با انتشار صورت مالی بعدی باید بازبینی شود."
                if not audited else
                "این تحلیل بر اساس آخرین صورت مالی حسابرسی‌شده موجود و قابل‌استخراج تهیه شده است؛ اطلاعیه‌های جدیدترِ غیرمالی جایگزین صورت مالی نمی‌شوند."
            ),
            "relatedDisclosures": raw.get("related_codal_disclosures") or [],
        },
        "coreQuestions": questions,
        "reasons": [
            f"امتیاز سلامت بنیادی {score} از ۱۰۰ است." if score is not None else "امتیاز سلامت به‌دلیل کمبود داده محاسبه نشد.",
            f"ارزش منصفانه پایه با مدل سناریویی {valuation['method']} و فرض‌های نمایش‌داده‌شده محاسبه شد." if valuation else "برای این صنعت هنوز مدل سناریویی پشتیبانی‌شده یا داده لازم موجود نیست.",
            "رشد هم‌دوره برای محاسبه رشد واقعی در دسترس نیست؛ نرخ تورم مرجع مستقل نمایش داده می‌شود."
            if (raw.get("period_comparison") or {}).get("revenue_growth_percent") is None else
            f"رشد واقعی با نرخ تورم مرجع {inflation} درصد محاسبه شده است.",
            "جریان نقد عملیاتی این دوره موجود نیست؛ پوشش نقدی سود قابل محاسبه نیست."
            if metrics.get("operating_cash_flow") is None else
            "پوشش نقدی سود از تقسیم جریان نقد عملیاتی بر سود خالص محاسبه شده است.",
        ] + ([
            "قیمت بیش از ۵۰ درصد رشد کرده، اما کمتر از دو دوره بنیادی معتبر برای سنجش چرخش سودآوری موجود است؛ نتیجه قطعی خرید یا فروش صادر نمی‌شود."
        ] if market_fundamental_divergence else []) + ([
            "رشد واقعی درآمد یا عبور سود خالص از زیان به سود، احتمال چرخش سودآوری را نشان می‌دهد؛ برای تأیید به تداوم در دوره بعد نیاز است."
        ] if turnaround_candidate else []) + ([
            f"رشد مبلغ فروش ماهانه هم‌دوره {monthly_growth:.1f} درصد است و از تورم مرجع عبور کرده، اما برای تأیید چرخش به تداوم نیاز دارد."
        ] if turnaround_candidate and monthly_growth is not None and inflation is not None and monthly_growth > inflation else []) + ([
            "تغییر تعداد سهام در تاریخچه بازار دیده شده، اما اطلاعیه اقدام شرکتی متناظر هنوز به داده ساختاریافته متصل نشده است."
        ] if capital_action_data_gap else []) + (["سود عملیاتی آخرین صورت مالی نامثبت است."] if has_operating_loss else []),
        "risks": [
            "ارزش‌گذاری سناریویی است و به کیفیت آخرین صورت مالی وابسته است.",
            "تغییر نرخ ارز، قیمت جهانی کالا و مقررات می‌تواند نتیجه را تغییر دهد.",
        ] + (["برای این گزارش اطلاعیه توضیحی یا اصلاحیه مرتبط وجود دارد؛ متن آن باید پیش از تصمیم نهایی بررسی شود."] if raw.get("related_codal_disclosures") else []),
        "criticalWarning": (
            "تعداد سهام در تاریخچه قیمت تغییر کرده، اما اقدام شرکتی متناظر ثبت نشده است؛ تا تطبیق افزایش سرمایه، قیمت و EPS قابل مقایسه قطعی نیستند."
            if capital_action_data_gap and not critical_warning
            else "رشد شدید قیمت با تاریخچه بنیادی ناکامل هم‌زمان شده است؛ این وضعیت می‌تواند نشانه چرخش سودآوری یا رفتار هیجانی باشد و نتیجه قطعی صادر نمی‌شود."
            if market_fundamental_divergence and not critical_warning
            else "در آخرین صورت مالی، زیان عملیاتی مشاهده شد."
            if has_operating_loss and not has_net_loss
            else "زیان خالص یا حقوق صاحبان سهام نامثبت مشاهده شد."
            if critical_warning
            else "داده برای تصمیم کافی نیست."
            if decision == "INSUFFICIENT_DATA"
            else None
        ),
        "policyVersion": policy.version,
        "modelVersion": policy.model_version,
        "dataAsOf": report.get("publish_datetime"),
        "calculatedAt": now.isoformat(),
        "staleAfter": (now + timedelta(hours=24)).isoformat(),
        "sourceLineage": {
            "codalTracingNo": report.get("tracing_no"),
            "codalDocument": report.get("excel_url"),
            "marketSource": (
                "BrsApi (آخرین داده ذخیره‌شده)"
                if live.get("_fallback")
                else "BrsApi"
                if live
                else None
            ),
        },
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload["payloadChecksum"] = hashlib.sha256(canonical.encode()).hexdigest()
    return payload
