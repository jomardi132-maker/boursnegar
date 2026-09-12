#!/usr/bin/env python3
"""Read-only, evidence-gated calibration audit for industry multiples.

This tool never updates policy. It emits a proposal only when the stored,
point-in-time snapshot history has enough instruments, days and observations.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlalchemy import text

from app.analytics.industry_valuation import MODEL_SPECS
from app.database import engine


MIN_OBSERVATIONS = 200
MIN_INSTRUMENTS = 30
MIN_DAYS = 20

PE_SQL = text("""
WITH observations AS (
  SELECT ind.model_family, a.instrument_id, a.calculated_at::date AS observed_on,
    (a.quality_summary->'keyMetrics'->>'pe')::numeric AS multiple,
    row_number() OVER (
      PARTITION BY a.instrument_id,a.calculated_at::date
      ORDER BY a.calculated_at DESC
    ) AS rn
  FROM analytical_snapshots a
  JOIN instruments ins ON ins.id=a.instrument_id AND ins.active
  JOIN issuers iss ON iss.id=ins.issuer_id
  JOIN industries ind ON ind.id=iss.industry_id
  WHERE coalesce(a.quality_summary->>'ratioQuality','VALID')='VALID'
    AND coalesce(a.quality_summary->>'analysisState','STANDARD')='STANDARD'
    AND a.coverage>=70
    AND a.quality_summary->'keyMetrics'->>'pe' IS NOT NULL
), clean AS (
  SELECT * FROM observations
  WHERE rn=1 AND multiple>0 AND multiple<100
)
SELECT model_family, count(*) observations,
  count(DISTINCT instrument_id) instruments,
  count(DISTINCT observed_on) days,
  percentile_cont(.25) WITHIN GROUP (ORDER BY multiple) q25,
  percentile_cont(.5) WITHIN GROUP (ORDER BY multiple) median,
  percentile_cont(.75) WITHIN GROUP (ORDER BY multiple) q75
FROM clean GROUP BY model_family ORDER BY model_family
""")


def evaluate_row(row: dict) -> dict:
    family = str(row["model_family"])
    spec = MODEL_SPECS.get(family)
    method = spec.method if spec else None
    reasons = []
    if method != "normalized_pe":
        reasons.append("METHOD_REQUIRES_SEPARATE_POINT_IN_TIME_METRIC")
    if int(row["observations"]) < MIN_OBSERVATIONS:
        reasons.append("INSUFFICIENT_OBSERVATIONS")
    if int(row["instruments"]) < MIN_INSTRUMENTS:
        reasons.append("INSUFFICIENT_INSTRUMENTS")
    if int(row["days"]) < MIN_DAYS:
        reasons.append("INSUFFICIENT_DAYS")
    ready = not reasons
    result = {
        **row,
        "current_method": method,
        "current_multiple": spec.multiple if spec else None,
        "status": "READY_FOR_REVIEW" if ready else "INSUFFICIENT_EVIDENCE",
        "gate_reasons": reasons,
        "proposal": None,
    }
    if ready:
        result["proposal"] = {
            "bear_multiple": round(float(row["q25"]), 2),
            "base_multiple": round(float(row["median"]), 2),
            "bull_multiple": round(float(row["q75"]), 2),
            "status": "REVIEW_ONLY",
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with engine.connect() as connection:
        raw_rows = [dict(row) for row in connection.execute(PE_SQL).mappings()]
    rows = [evaluate_row(row) for row in raw_rows]
    observed = {row["model_family"] for row in rows}
    for family, spec in sorted(MODEL_SPECS.items()):
        if family not in observed:
            rows.append(evaluate_row({
                "model_family": family, "observations": 0, "instruments": 0,
                "days": 0, "q25": None, "median": None, "q75": None,
            }))
    result = {
        "method": "point_in_time_industry_multiple_calibration_audit_v1",
        "writes_policy": False,
        "thresholds": {
            "minimum_observations": MIN_OBSERVATIONS,
            "minimum_instruments": MIN_INSTRUMENTS,
            "minimum_days": MIN_DAYS,
        },
        "summary": {
            "families": len(rows),
            "ready_for_review": sum(row["status"] == "READY_FOR_REVIEW" for row in rows),
            "insufficient_evidence": sum(row["status"] != "READY_FOR_REVIEW" for row in rows),
        },
        "rows": sorted(rows, key=lambda row: row["model_family"]),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
