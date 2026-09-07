#!/usr/bin/env python3
"""Audit promoted and raw NAV records without changing the database."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlalchemy import text

from app.database import engine


SQL = text("""
WITH latest_alias AS (
  SELECT DISTINCT ON (instrument_id) instrument_id, symbol
  FROM symbol_aliases
  ORDER BY instrument_id, created_at DESC
), promoted AS (
  SELECT vi.id, la.symbol, fp.end_date_jalali, vi.value, vi.normalized_unit,
         vi.source_disclosure_id, vi.quality_status
  FROM valuation_inputs vi
  JOIN issuers iss ON iss.id=vi.issuer_id
  JOIN financial_periods fp ON fp.id=vi.period_id
  JOIN instruments ins ON ins.issuer_id=iss.id
  JOIN latest_alias la ON la.instrument_id=ins.id
  WHERE vi.input_key='nav_per_share'
), raw AS (
  SELECT symbol, period_end_jalali, value, unit, source_action_id,
         payload->>'document_sha256' AS document_sha256
  FROM codalpy_records
  WHERE fact_key='nav_per_share'
), matched AS (
  SELECT DISTINCT r.source_action_id, p.id AS promoted_id,
         r.symbol, r.period_end_jalali, r.value, r.unit,
         p.normalized_unit, p.source_disclosure_id
  FROM raw r
  JOIN promoted p ON p.symbol=r.symbol
     AND p.end_date_jalali=r.period_end_jalali
     AND p.value=r.value
)
SELECT
  (SELECT count(*) FROM promoted) AS promoted_total,
  (SELECT count(*) FROM promoted WHERE normalized_unit<>'IRR') AS non_irr_promotions,
  (SELECT count(*) FROM raw) AS raw_total,
  (SELECT count(DISTINCT symbol) FROM raw) AS raw_symbols,
  (SELECT count(*) FROM raw WHERE unit<>'IRR') AS raw_non_per_share_units,
  (SELECT count(DISTINCT source_action_id) FROM matched) AS identity_period_value_matches,
  (SELECT count(DISTINCT source_action_id) FROM matched
     WHERE normalized_unit=unit) AS identity_value_unit_matches,
  (SELECT count(DISTINCT source_action_id) FROM matched
     WHERE normalized_unit=unit
       AND source_disclosure_id=source_action_id) AS exact_source_matches
""")


FUND_READINESS_SQL = text("""
WITH latest_alias AS (
  SELECT DISTINCT ON (instrument_id) instrument_id,symbol
  FROM symbol_aliases WHERE valid_to IS NULL
  ORDER BY instrument_id,created_at DESC
), funds AS (
  SELECT DISTINCT iss.id AS issuer_id,la.symbol
  FROM issuers iss
  JOIN industries ind ON ind.id=iss.industry_id
  JOIN instruments ins ON ins.issuer_id=iss.id AND ins.active
  JOIN latest_alias la ON la.instrument_id=ins.id
  WHERE ind.model_family='fund'
), period_evidence AS (
  SELECT f.issuer_id,f.symbol,fp.end_date_jalali,d.source_disclosure_id,
    bool_or(ff.fact_key='nav_per_share' AND ff.quality_status='VALID'
      AND ff.normalized_unit='IRR' AND ff.normalized_value>0) AS has_nav,
    bool_or(ff.fact_key='units_outstanding' AND ff.quality_status='VALID'
      AND ff.normalized_unit='units' AND ff.normalized_value>0) AS has_units
  FROM funds f
  LEFT JOIN financial_periods fp ON fp.issuer_id=f.issuer_id
  LEFT JOIN disclosure_versions dv ON dv.id=fp.disclosure_version_id
  LEFT JOIN disclosures d ON d.id=dv.disclosure_id
  LEFT JOIN financial_facts ff ON ff.period_id=fp.id
    AND ff.fact_key IN ('nav_per_share','units_outstanding')
  GROUP BY f.issuer_id,f.symbol,fp.id,fp.end_date_jalali,d.source_disclosure_id
), per_fund AS (
  SELECT issuer_id,symbol,coalesce(bool_or(has_nav),false) AS any_nav,
    coalesce(bool_or(has_units),false) AS any_units,
    coalesce(bool_or(has_nav AND has_units),false) AS same_period_nav_units
  FROM period_evidence GROUP BY issuer_id,symbol
)
SELECT pf.*,
  (SELECT json_build_object(
      'period_end_jalali',pe.end_date_jalali,
      'source_disclosure_id',pe.source_disclosure_id)
   FROM period_evidence pe
   WHERE pe.issuer_id=pf.issuer_id AND pe.has_nav AND NOT pe.has_units
   ORDER BY pe.end_date_jalali DESC,pe.source_disclosure_id DESC LIMIT 1
  ) AS latest_nav_without_units
FROM per_fund pf ORDER BY pf.symbol
""")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with engine.begin() as connection:
        summary = dict(connection.execute(SQL).mappings().one())
        funds = [dict(row) for row in connection.execute(FUND_READINESS_SQL).mappings()]
    nav_only = [row for row in funds if row["any_nav"] and not row["same_period_nav_units"]]
    summary["fund_readiness"] = {
        "active_funds": len(funds),
        "funds_with_nav": sum(row["any_nav"] for row in funds),
        "funds_with_units": sum(row["any_units"] for row in funds),
        "funds_with_same_period_nav_units": sum(row["same_period_nav_units"] for row in funds),
        "funds_without_valid_nav": sum(not row["any_nav"] for row in funds),
        "nav_without_same_period_units": [
            {"symbol": row["symbol"], **(row["latest_nav_without_units"] or {})}
            for row in nav_only
        ],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
