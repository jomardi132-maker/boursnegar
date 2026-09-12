from scripts.audit_industry_policy_calibration import evaluate_row


def test_calibration_requires_enough_point_in_time_evidence():
    row = evaluate_row({
        "model_family": "metals", "observations": 199, "instruments": 30,
        "days": 20, "q25": 5, "median": 6, "q75": 8,
    })
    assert row["status"] == "INSUFFICIENT_EVIDENCE"
    assert "INSUFFICIENT_OBSERVATIONS" in row["gate_reasons"]
    assert row["proposal"] is None


def test_calibration_proposal_is_review_only_after_all_gates_pass():
    row = evaluate_row({
        "model_family": "metals", "observations": 200, "instruments": 30,
        "days": 20, "q25": 5.123, "median": 6.456, "q75": 8.789,
    })
    assert row["status"] == "READY_FOR_REVIEW"
    assert row["proposal"] == {
        "bear_multiple": 5.12, "base_multiple": 6.46,
        "bull_multiple": 8.79, "status": "REVIEW_ONLY",
    }


def test_price_to_book_families_never_reuse_pe_calibration():
    row = evaluate_row({
        "model_family": "bank", "observations": 500, "instruments": 50,
        "days": 50, "q25": 3, "median": 4, "q75": 5,
    })
    assert row["status"] == "INSUFFICIENT_EVIDENCE"
    assert "METHOD_REQUIRES_SEPARATE_POINT_IN_TIME_METRIC" in row["gate_reasons"]
    assert row["proposal"] is None
