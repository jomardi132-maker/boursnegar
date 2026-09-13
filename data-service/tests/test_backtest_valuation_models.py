from datetime import date, datetime, timezone

from scripts.backtest_valuation_models import summarize_horizon


def row(calculated_hour=1, entry_day=1):
    return {
        "symbol": "فولاد", "model_type": "normalized_pe",
        "entry_date": date(2026, 8, entry_day),
        "calculated_at": datetime(2026, 8, entry_day, calculated_hour, tzinfo=timezone.utc),
        "entry_price": 100, "value_gap_pct": 10,
        "exit_5_price": 110, "exit_10_price": 120, "exit_20_price": 130,
    }


def test_repeated_snapshots_share_one_independent_outcome():
    result = summarize_horizon([row(1), row(2)], 20)
    assert result["comparable_snapshots"] == 2
    assert result["independent_samples"] == 1
    assert result["by_model"]["normalized_pe"]["samples"] == 1
    assert result["statistical_gate"] == "INSUFFICIENT_SAMPLE"


def test_distinct_entry_sessions_are_independent():
    assert summarize_horizon([row(entry_day=1), row(entry_day=2)], 20)["independent_samples"] == 2
