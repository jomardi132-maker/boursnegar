#!/usr/bin/env python3
"""Produce an evidence-only coverage and decision-risk audit by industry."""
from __future__ import annotations

import argparse
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    with engine.connect() as connection:
        global_row = dict(connection.execute(GLOBAL_SQL).mappings().one())
        industries = [dict(row) for row in connection.execute(INDUSTRY_SQL).mappings()]
    for key, value in list(global_row.items()):
        if hasattr(value, "as_tuple"):
            global_row[key] = float(value)
    for row in industries:
        for key, value in list(row.items()):
            if hasattr(value, "as_tuple"):
                row[key] = float(value)
    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "scope": "all active instruments grouped by authoritative industry mapping",
        "global": global_row,
        "industries": industries,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
