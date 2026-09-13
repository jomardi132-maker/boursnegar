from pathlib import Path

from scripts.audit_valuation_input_gates import classify_readiness


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


def test_fcfe_audit_distinguishes_reported_facts_from_rate_policy():
    row = {
        "shares_gate": True, "ocf_gate": True, "capex_gate": True,
        "net_borrowing_gate": True, "equity_gate": True,
        "sustainable_profit_gate": True, "unit_gate": True,
        "cost_of_equity_gate": False, "terminal_growth_gate": False,
    }
    assert classify_readiness(row) == "CASH_FLOW_READY_RATE_POLICY_MISSING"
    row["cost_of_equity_gate"] = row["terminal_growth_gate"] = True
    assert classify_readiness(row) == "INTRINSIC_READY"
