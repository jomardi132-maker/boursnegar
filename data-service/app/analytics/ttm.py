from __future__ import annotations


FLOW_FACT_KEYS = (
    "revenue",
    "cogs",
    "gross_profit",
    "operating_profit",
    "net_profit",
    "operating_cash_flow",
)


def build_ttm_metrics(
    current: dict,
    latest_annual: dict,
    prior_comparable: dict,
) -> dict:
    """Build trailing-twelve-month flows from compatible cumulative periods.

    TTM = latest annual + current YTD - prior-year comparable YTD. Missing
    components stay missing; they are never replaced by an older value.
    """
    metrics: dict[str, float | None] = {}
    for key in FLOW_FACT_KEYS:
        values = (latest_annual.get(key), current.get(key), prior_comparable.get(key))
        metrics[key] = (
            float(values[0]) + float(values[1]) - float(values[2])
            if all(value is not None for value in values)
            else None
        )
    return metrics
