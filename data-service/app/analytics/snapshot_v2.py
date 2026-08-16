import hashlib
import json
from datetime import datetime, timedelta, timezone

from app.analytics.engine import Policy, core_questions, decide
from app.analytics.industry_valuation import health_score, value_company


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
    valuation = value_company(raw)
    family = valuation.get("family") if valuation else "unclassified"
    score, dimensions = health_score(
        metrics,
        ratios,
        family,
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
        policy=policy,
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
        "confidence": confidence,
        "valuation": valuation,
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
            "audited": audited,
        },
        "coreQuestions": questions,
        "reasons": [
            f"امتیاز سلامت بنیادی {score} از ۱۰۰ است." if score is not None else "امتیاز سلامت به‌دلیل کمبود داده محاسبه نشد.",
            f"ارزش منصفانه پایه با مدل {valuation['method']} محاسبه شد." if valuation else "مدل تخصصی معتبر برای این صنعت یا داده موجود نیست.",
        ] + (["سود عملیاتی آخرین صورت مالی نامثبت است."] if has_operating_loss else []),
        "risks": [
            "ارزش‌گذاری سناریویی است و به کیفیت آخرین صورت مالی وابسته است.",
            "تغییر نرخ ارز، قیمت جهانی کالا و مقررات می‌تواند نتیجه را تغییر دهد.",
        ],
        "criticalWarning": (
            "در آخرین صورت مالی، زیان عملیاتی مشاهده شد."
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
