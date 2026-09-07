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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with engine.begin() as connection:
        summary = dict(connection.execute(SQL).mappings().one())
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
