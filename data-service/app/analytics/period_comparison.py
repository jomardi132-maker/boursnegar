from __future__ import annotations

from collections.abc import Callable

from fastapi import HTTPException

PERIOD_LABELS = ("۱۲ ماهه", "۹ ماهه", "۶ ماهه", "۳ ماهه")
UNAVAILABLE = "گزارش دوره هم‌طول قبلی دارای فایل اکسل پیدا نشد."
UNUSABLE = "فایل گزارش دوره هم‌طول قبلی قابل دریافت یا استخراج نبود."

ParseFirstUsable = Callable[[list[dict]], tuple[dict, str, dict]]


def period_label_from_title(title: str) -> str | None:
    return next((label for label in PERIOD_LABELS if label in title), None)


def build_period_comparison(
    candidate: dict,
    parsed: dict,
    previous_candidates: list[dict],
    parse_first_usable: ParseFirstUsable,
) -> tuple[dict | None, str | None]:
    """Compare the current statement to a same-length prior report.

    Failures here must not abort the primary analysis. `_parse_first_usable_report`
    converts download/parse misses into HTTPException, so that must be caught.
    """
    period_label = period_label_from_title(str(candidate.get("Title") or ""))
    if not period_label or not previous_candidates:
        return None, UNAVAILABLE
    try:
        previous, _previous_url, previous_parsed = parse_first_usable(previous_candidates)
        current_revenue = parsed["metrics"].get("revenue")
        previous_revenue = previous_parsed["metrics"].get("revenue")
        current_profit = parsed["metrics"].get("net_profit")
        previous_profit = previous_parsed["metrics"].get("net_profit")
        return {
            "period_label": period_label,
            "current_report": candidate.get("TracingNo"),
            "previous_report": previous.get("TracingNo"),
            "current_revenue": current_revenue,
            "previous_revenue": previous_revenue,
            "revenue_growth_percent": (
                ((current_revenue / previous_revenue) - 1) * 100
                if current_revenue is not None and previous_revenue not in (None, 0)
                else None
            ),
            "current_net_profit": current_profit,
            "previous_net_profit": previous_profit,
            "net_profit_growth_percent": (
                ((current_profit / previous_profit) - 1) * 100
                if current_profit is not None and previous_profit not in (None, 0)
                else None
            ),
            "source": "صورت‌های مالی رسمی کدال",
        }, None
    except HTTPException:
        return None, UNUSABLE
