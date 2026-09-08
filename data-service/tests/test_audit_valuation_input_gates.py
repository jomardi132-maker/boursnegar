from pathlib import Path


SOURCE = (Path(__file__).parents[1] / "scripts" / "audit_valuation_input_gates.py").read_text(
    encoding="utf-8"
)


def test_fcfe_audit_requires_all_explicit_components():
    for gate in (
        "ocf_gate",
        "capex_gate",
        "net_borrowing_gate",
        "cost_of_equity_gate",
        "terminal_growth_gate",
    ):
        assert gate in SOURCE


def test_fcfe_audit_uses_valid_period_linked_rates():
    assert "LEFT JOIN valuation_inputs vi ON vi.period_id=fp.id" in SOURCE
    assert "vi.quality_status='VALID'" in SOURCE
    assert "same_period_fcfe_input_gate_audit" in SOURCE


def test_fcfe_audit_exports_exact_current_period_identity():
    assert "CURRENT_PERIOD_KEYS_SQL" in SOURCE
    assert "current_period_keys" in SOURCE
    for field in ("issuer_id", "end_date_jalali", "length_months", "audited", "scope"):
        assert field in SOURCE
