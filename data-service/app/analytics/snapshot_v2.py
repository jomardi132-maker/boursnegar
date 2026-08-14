import hashlib
import json
from datetime import datetime, timedelta, timezone

from app.analytics.engine import Policy, core_questions, decide


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
        bank_rate=None,
        matched_inflation=None,
        policy=policy,
    )
    decision = decide(
        health_score=None,
        coverage=coverage,
        confidence=confidence,
        current_price=live.get("last_price") or live.get("closing_price"),
        fair_value_low=None,
        fair_value_base=None,
        fair_value_high=None,
        industry_model_ready=False,
        policy=policy,
    )
    now = datetime.now(timezone.utc)
    payload = {
        "symbol": raw.get("symbol"),
        "companyName": raw.get("company_name"),
        "reportMode": report_mode,
        "decision": decision,
        "healthScore": None,
        "dataCoverage": coverage,
        "confidence": confidence,
        "valuation": None,
        "coreQuestions": questions,
        "reasons": [],
        "risks": [
            "مدل ارزش‌گذاری تخصصی صنعت هنوز آماده نیست.",
            "نرخ‌های رسمی و تاریخ‌دار بانکی/تورم برای دوره متناظر ثبت نشده‌اند.",
        ],
        "criticalWarning": "داده برای توصیه خرید یا فروش کافی نیست.",
        "policyVersion": policy.version,
        "modelVersion": policy.model_version,
        "dataAsOf": report.get("publish_datetime"),
        "calculatedAt": now.isoformat(),
        "staleAfter": (now + timedelta(hours=24)).isoformat(),
        "sourceLineage": {
            "codalTracingNo": report.get("tracing_no"),
            "codalDocument": report.get("excel_url"),
            "marketSource": "BrsApi" if live else None,
        },
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload["payloadChecksum"] = hashlib.sha256(canonical.encode()).hexdigest()
    return payload
