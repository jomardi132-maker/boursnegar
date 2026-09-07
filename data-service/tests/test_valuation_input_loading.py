from app.analytics.valuation_inputs import validated_valuation_inputs
from pathlib import Path


def _row(key, value, unit, **overrides):
    row = {
        "input_key": key,
        "value": value,
        "normalized_unit": unit,
        "source": "official-source",
        "source_disclosure_id": "source-record-1",
        "content_checksum": "a" * 64,
    }
    row.update(overrides)
    return row


def test_accepts_unique_canonical_fully_sourced_inputs():
    values, lineage = validated_valuation_inputs([
        _row("fcfe", 120, "IRR_million"),
        _row("cost_of_equity", 25, "percent"),
        _row("terminal_growth", 5, "percent"),
    ])
    assert values == {"fcfe": 120.0, "cost_of_equity": 25.0, "terminal_growth": 5.0}
    assert [item["inputKey"] for item in lineage] == [
        "cost_of_equity", "fcfe", "terminal_growth"
    ]


def test_rejects_wrong_units_missing_provenance_and_conflicts():
    values, lineage = validated_valuation_inputs([
        _row("nav_per_share", 1000, "IRR_million"),
        _row("wacc", 20, "percent", content_checksum=None),
        _row("fcff", 100, "IRR_million", source_disclosure_id="a"),
        _row("fcff", 100, "IRR_million", source_disclosure_id="b"),
    ])
    assert values == {}
    assert lineage == []


def test_rejects_nonpositive_discount_rate():
    values, _ = validated_valuation_inputs([_row("cost_of_equity", 0, "percent")])
    assert values == {}


def test_loader_matches_complete_period_identity_across_disclosures():
    source = (Path(__file__).parents[1] / "app" / "main.py").read_text(encoding="utf-8")
    assert "s.issuer_id=fp.issuer_id AND s.end_date=fp.end_date" in source
    assert "s.length_months=fp.length_months AND s.audited=fp.audited" in source
    assert "s.scope IS NOT DISTINCT FROM fp.scope" in source
