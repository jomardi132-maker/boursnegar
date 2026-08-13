from dataclasses import dataclass
from typing import Literal

Decision = Literal["BUY", "HOLD", "SELL", "INSUFFICIENT_DATA"]

@dataclass(frozen=True)
class Policy:
    version: str = "recommendation-v1.0.0"
    model_version: str = "fundamental-engine-v1.0.0"
    minimum_coverage: float = 70.0
    minimum_confidence: float = 65.0
    cash_quality_threshold: float = 80.0
    buy_margin_of_safety: float = 0.20
    sell_overvaluation: float = 0.15

def ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0): return None
    return numerator / denominator

def core_questions(*, ttm_eps=None, price=None, pe=None, bank_rate=None,
                   operating_cash_flow=None, net_profit=None,
                   nominal_growth=None, matched_inflation=None, policy=Policy()):
    earnings_yield = ratio(ttm_eps, price)
    if earnings_yield is not None: earnings_yield *= 100
    elif pe is not None and pe > 0: earnings_yield = 100 / pe
    cash_quality = ratio(operating_cash_flow, net_profit)
    if cash_quality is not None: cash_quality *= 100
    real_growth = None if nominal_growth is None or matched_inflation is None else nominal_growth - matched_inflation
    return {
        "earnings_vs_bank": {"value": earnings_yield, "benchmark": bank_rate,
          "status": "INSUFFICIENT_DATA" if earnings_yield is None or bank_rate is None else ("PASS" if earnings_yield > bank_rate else "FAIL")},
        "cash_quality": {"value": cash_quality, "benchmark": policy.cash_quality_threshold,
          "status": "INSUFFICIENT_DATA" if cash_quality is None or net_profit is None or net_profit <= 0 else ("PASS" if cash_quality >= policy.cash_quality_threshold else "FAIL")},
        "real_growth": {"value": real_growth, "benchmark": 0,
          "status": "INSUFFICIENT_DATA" if real_growth is None else ("PASS" if real_growth > 0 else "FAIL")},
    }

def decide(*, health_score, coverage, confidence, current_price=None,
           fair_value_low=None, fair_value_base=None, fair_value_high=None,
           critical_warning=False, industry_model_ready=False, policy=Policy()) -> Decision:
    if coverage < policy.minimum_coverage or confidence < policy.minimum_confidence or not industry_model_ready:
        return "INSUFFICIENT_DATA"
    if None in (health_score, current_price, fair_value_low, fair_value_base, fair_value_high):
        return "INSUFFICIENT_DATA"
    if not (fair_value_low <= fair_value_base <= fair_value_high) or current_price <= 0: return "INSUFFICIENT_DATA"
    if critical_warning or health_score < 40 or current_price > fair_value_high * (1 + policy.sell_overvaluation): return "SELL"
    if health_score >= 70 and current_price <= fair_value_base * (1 - policy.buy_margin_of_safety): return "BUY"
    return "HOLD"
