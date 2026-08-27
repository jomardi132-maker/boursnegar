#!/usr/bin/env python3
"""Produce an evidence-only coverage and decision-risk audit by industry."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

from app.database import engine


INDUSTRY_SQL = text("""
WITH period_coverage AS (
  SELECT fp.issuer_id,
    count(DISTINCT (fp.end_date,fp.length_months,fp.scope))
      FILTER(WHERE ff.quality_status='VALID') periods,
    count(DISTINCT ff.fact_key) FILTER(WHERE ff.quality_status='VALID') facts
  FROM financial_periods fp LEFT JOIN financial_facts ff ON ff.period_id=fp.id
  GROUP BY fp.issuer_id
), disclosure_coverage AS (
  SELECT issuer_id,count(*) FILTER(WHERE letter_code IN ('ن-۳۰','ن-30')
    OR title LIKE '%گزارش فعالیت ماهانه%') monthly_disclosures
  FROM disclosures GROUP BY issuer_id
), action_coverage AS (
  SELECT instrument_id,count(*) corporate_actions FROM corporate_actions GROUP BY instrument_id
), symbol_coverage AS (
  SELECT sa.symbol,COALESCE(ind.title_fa,'نامشخص') industry,
    COALESCE(pc.periods,0) periods,COALESCE(pc.facts,0) facts,
    COALESCE(dc.monthly_disclosures,0) monthly_disclosures,
    COALESCE(ac.corporate_actions,0) corporate_actions
  FROM symbol_aliases sa
  JOIN instruments i ON i.id=sa.instrument_id
  JOIN issuers iss ON iss.id=i.issuer_id
  LEFT JOIN industries ind ON ind.id=iss.industry_id
  LEFT JOIN period_coverage pc ON pc.issuer_id=iss.id
  LEFT JOIN disclosure_coverage dc ON dc.issuer_id=iss.id
  LEFT JOIN action_coverage ac ON ac.instrument_id=i.id
  WHERE sa.valid_to IS NULL AND i.active
)
SELECT industry,count(*) symbols,
  count(*) FILTER(WHERE periods>=2) comparable_symbols,
  count(*) FILTER(WHERE facts>=7) core_fact_symbols,
  count(*) FILTER(WHERE monthly_disclosures>0) monthly_notice_symbols,
  count(*) FILTER(WHERE corporate_actions>0) corporate_action_symbols,
  round(avg(periods),2) average_periods
FROM symbol_coverage GROUP BY industry ORDER BY symbols DESC,industry
""")

GLOBAL_SQL = text("""
SELECT
 (SELECT count(*) FROM instruments WHERE active) active_instruments,
 (SELECT count(DISTINCT issuer_id) FROM financial_periods) issuers_with_periods,
 (SELECT count(*) FROM financial_periods) financial_periods,
 (SELECT count(*) FROM financial_facts) financial_facts,
 (SELECT count(*) FROM financial_facts WHERE quality_status='VALID') valid_facts,
 (SELECT count(*) FROM daily_prices WHERE quality_status='VALID') valid_prices,
 (SELECT count(*) FROM codalpy_records) raw_codal_records,
 (SELECT count(*) FROM codalpy_records WHERE symbol IS NOT NULL) linked_codal_records,
 (SELECT count(*) FROM codalpy_records WHERE symbol IS NULL) unlinked_codal_records,
 (SELECT count(*) FROM codalpy_records WHERE output_type='monthly_activity') monthly_records,
 (SELECT count(*) FROM codalpy_records WHERE output_type='monthly_activity' AND symbol IS NOT NULL) linked_monthly_records,
 (SELECT count(DISTINCT symbol) FROM codalpy_records WHERE output_type='income_statement' AND symbol IS NOT NULL) income_statement_symbols,
 (SELECT count(DISTINCT symbol) FROM codalpy_records WHERE output_type='balance_sheet' AND symbol IS NOT NULL) balance_sheet_symbols,
 (SELECT count(DISTINCT symbol) FROM codalpy_records WHERE output_type='monthly_activity' AND symbol IS NOT NULL) monthly_activity_symbols
""")

SYMBOL_SQL = text("""
WITH current_alias AS (
  SELECT instrument_id, min(symbol) AS symbol
  FROM symbol_aliases WHERE valid_to IS NULL GROUP BY instrument_id
), period_coverage AS (
  SELECT fp.issuer_id,
    count(DISTINCT (fp.end_date,fp.length_months,fp.scope))
      FILTER(WHERE ff.quality_status='VALID') valid_periods,
    count(DISTINCT ff.fact_key) FILTER(WHERE ff.quality_status='VALID') valid_fact_keys,
    count(ff.id) raw_fact_rows,
    count(ff.id) FILTER(WHERE ff.quality_status='VALID') valid_fact_rows
  FROM financial_periods fp LEFT JOIN financial_facts ff ON ff.period_id=fp.id
  GROUP BY fp.issuer_id
), disclosure_coverage AS (
  SELECT issuer_id,count(*) disclosures,
    count(*) FILTER(WHERE letter_code IN ('ن-۳۰','ن-30')
      OR title LIKE '%گزارش فعالیت ماهانه%') monthly_disclosures
  FROM disclosures GROUP BY issuer_id
), action_coverage AS (
  SELECT instrument_id,count(*) corporate_actions FROM corporate_actions GROUP BY instrument_id
), latest_snapshots AS (
  SELECT DISTINCT ON (s.instrument_id) s.instrument_id,s.coverage,s.confidence,
    s.calculated_at,r.decision
  FROM analytical_snapshots s
  JOIN recommendation_results r ON r.snapshot_id=s.id
  ORDER BY s.instrument_id,s.calculated_at DESC
)
SELECT
  COALESCE(ca.symbol,'NO_CURRENT_ALIAS:' || i.id::text) symbol,
  (ca.symbol IS NULL) missing_current_alias,
  i.id::text instrument_id,
  iss.legal_name,
  COALESCE(ind.title_fa,'نامشخص') industry,
  COALESCE(ind.model_family,'') model_family,
  COALESCE(pc.valid_periods,0) valid_periods,
  COALESCE(pc.valid_fact_keys,0) valid_fact_keys,
  COALESCE(pc.raw_fact_rows,0) raw_fact_rows,
  COALESCE(pc.valid_fact_rows,0) valid_fact_rows,
  COALESCE(dc.disclosures,0) disclosures,
  COALESCE(dc.monthly_disclosures,0) monthly_disclosures,
  COALESCE(ac.corporate_actions,0) corporate_actions,
  ls.decision latest_decision,
  ls.coverage latest_coverage,
  ls.confidence latest_confidence,
  ls.calculated_at latest_calculated_at,
  CASE
    WHEN ca.symbol IS NULL THEN 'NO_CURRENT_ALIAS'
    WHEN COALESCE(pc.valid_periods,0) < 2 THEN 'MISSING_COMPARABLE_PERIODS'
    WHEN COALESCE(pc.valid_fact_keys,0) < 7 THEN 'MISSING_CORE_FACTS'
    ELSE 'CORE_READY'
  END coverage_tier
FROM instruments i
JOIN issuers iss ON iss.id=i.issuer_id
LEFT JOIN industries ind ON ind.id=iss.industry_id
LEFT JOIN current_alias ca ON ca.instrument_id=i.id
LEFT JOIN period_coverage pc ON pc.issuer_id=iss.id
LEFT JOIN disclosure_coverage dc ON dc.issuer_id=iss.id
LEFT JOIN action_coverage ac ON ac.instrument_id=i.id
LEFT JOIN latest_snapshots ls ON ls.instrument_id=i.id
WHERE i.active
ORDER BY coverage_tier,industry,symbol
""")


def _json_ready(row: dict) -> dict:
    for key, value in list(row.items()):
        if hasattr(value, "as_tuple"):
            row[key] = float(value)
        elif hasattr(value, "isoformat"):
            row[key] = value.isoformat()
    return row


def _counts(rows: list[dict], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key) or "NO_SNAPSHOT")
        counts[value] = counts.get(value, 0) + 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--symbols-output", help="Write active-instrument symbol-level coverage CSV.")
    args = parser.parse_args()
    with engine.connect() as connection:
        global_row = dict(connection.execute(GLOBAL_SQL).mappings().one())
        industries = [dict(row) for row in connection.execute(INDUSTRY_SQL).mappings()]
        symbols = [dict(row) for row in connection.execute(SYMBOL_SQL).mappings()]
    global_row = _json_ready(global_row)
    industries = [_json_ready(row) for row in industries]
    symbols = [_json_ready(row) for row in symbols]
    coverage_tiers = _counts(symbols, "coverage_tier")
    latest_decisions = _counts(symbols, "latest_decision")
    if args.symbols_output:
        output = Path(args.symbols_output)
        with output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(symbols[0].keys()) if symbols else [])
            writer.writeheader()
            writer.writerows(symbols)
    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "scope": "all active instruments grouped by authoritative industry mapping",
        "global": global_row,
        "symbolCoverageTiers": coverage_tiers,
        "latestDecisions": latest_decisions,
        "industries": industries,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
