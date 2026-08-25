from __future__ import annotations

from dataclasses import dataclass

from app.ingestion.market_history import model_family


@dataclass(frozen=True)
class ModelSpec:
    method: str
    multiple: float
    downside: float = 0.20
    upside: float = 0.20


MODEL_SPECS = {
    "metals": ModelSpec("normalized_pe", 6.0),
    "petrochemical": ModelSpec("normalized_pe", 6.5),
    "refinery": ModelSpec("normalized_pe", 5.5, 0.25, 0.25),
    "cement": ModelSpec("normalized_pe", 7.0),
    "pharmaceutical": ModelSpec("normalized_pe", 7.0),
    "bank": ModelSpec("price_to_book", 1.0, 0.20, 0.15),
    # Conservative accounting book-value proxy. This is not an NAV model;
    # the payload must make that limitation explicit until sourced NAV data is
    # available.
    "real_estate": ModelSpec("price_to_book", 1.0, 0.25, 0.25),
    "ceramics": ModelSpec("normalized_pe", 7.0),
}


def _number(value):
    try:
        result = float(value)
        return result if result == result else None
    except (TypeError, ValueError):
        return None


def health_score(metrics: dict, ratios: dict, family: str, inflation: float | None,
                 nominal_growth: float | None) -> tuple[float | None, dict]:
    dimensions = {}
    roe = _number(ratios.get("roe_percent"))
    cash = _number(ratios.get("cash_to_profit_ratio_percent"))
    margin = _number(ratios.get("operating_margin_percent"))
    if margin is None:
        margin = _number(ratios.get("net_margin_percent"))
    debt = _number(ratios.get("debt_ratio_percent"))
    roa = _number(ratios.get("roa_percent"))
    if roe is not None:
        dimensions["profitability"] = min(30, max(0, roe / 20 * 30))
    if cash is not None:
        dimensions["cash_quality"] = min(25, max(0, cash / 100 * 25))
    if margin is not None and family != "bank":
        dimensions["margin"] = min(15, max(0, margin / 20 * 15))
    if family == "bank" and roa is not None:
        dimensions["asset_efficiency"] = min(20, max(0, roa / 1.5 * 20))
    elif debt is not None:
        dimensions["leverage"] = max(0, min(20, (80 - debt) / 50 * 20))
    if nominal_growth is not None and inflation is not None:
        real = ((1 + nominal_growth / 100) / (1 + inflation / 100) - 1) * 100
        dimensions["real_growth"] = min(10, max(0, 5 + real / 5))
    weights = {"profitability": 30, "cash_quality": 25, "margin": 15,
               "asset_efficiency": 20, "leverage": 20, "real_growth": 10}
    available = sum(weights[key] for key in dimensions)
    if available < 55:
        return None, dimensions
    score = sum(dimensions.values()) / available * 100
    return round(min(100, max(0, score)), 2), {key: round(value, 2) for key, value in dimensions.items()}


def value_company(raw: dict) -> dict | None:
    live = raw.get("live_price") or {}
    metrics = raw.get("financial_metrics") or {}
    category = live.get("market_category")
    family = model_family(category)
    spec = MODEL_SPECS.get(family)
    shares = _number(live.get("total_shares"))
    if not spec:
        return None
    if spec.method == "price_to_book":
        equity_million_rial = _number(metrics.get("total_equity"))
        if not equity_million_rial or equity_million_rial <= 0 or not shares or shares <= 0:
            return None
        per_share_basis = equity_million_rial * 1_000_000 / shares
    else:
        per_share_basis = _number(live.get("eps")) or _number(metrics.get("eps_basic"))
        if (not per_share_basis or per_share_basis <= 0) and shares and shares > 0:
            profit = _number(metrics.get("net_profit"))
            if profit and profit > 0:
                per_share_basis = profit * 1_000_000 / shares
        if not per_share_basis or per_share_basis <= 0:
            return None
    base = per_share_basis * spec.multiple
    low, high = base * (1 - spec.downside), base * (1 + spec.upside)
    return {
        "family": family,
        "method": spec.method,
        "modelVersion": f"{family}-v1.0.0",
        "fairValueLow": round(low),
        "fairValueBase": round(base),
        "fairValueHigh": round(high),
        "basisPerShare": round(per_share_basis, 2),
        "assumptions": {
            "industry": category,
            "multiple": spec.multiple,
            "scenarioDownside": spec.downside,
            "scenarioUpside": spec.upside,
            "currency": "IRR_PER_SHARE",
            "basisSource": (
                "book_value_proxy"
                if spec.method == "price_to_book"
                else "market_ttm_eps" if _number(live.get("eps")) else "audited_report_eps"
            ),
        },
        "scenarios": {"bear": round(low), "base": round(base), "bull": round(high)},
    }
