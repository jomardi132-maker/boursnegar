#!/usr/bin/env python3
"""Audit evidence gates needed by the fundamental valuation models."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlalchemy import text

from app.database import engine


SQL = text("""
WITH aliases AS (
  SELECT instrument_id, min(symbol) AS symbol FROM symbol_aliases
  WHERE valid_to IS NULL GROUP BY instrument_id
), latest_price AS (
  SELECT DISTINCT ON (instrument_id) instrument_id,
    shares_outstanding, trading_date
  FROM daily_prices WHERE quality_status='VALID' AND volume>0
  ORDER BY instrument_id,trading_date DESC,retrieved_at DESC
), period_keys AS (
  SELECT issuer_id,end_date,length_months,audited,scope,
    dense_rank() OVER (PARTITION BY issuer_id ORDER BY end_date DESC,audited DESC) rn
  FROM financial_periods
  GROUP BY issuer_id,end_date,length_months,audited,scope
), facts AS (
  SELECT pk.issuer_id,
    count(*) FILTER (WHERE pk.rn=1 AND ff.fact_key='operating_cash_flow' AND ff.quality_status='VALID' AND ff.normalized_value IS NOT NULL) ocf,
    count(*) FILTER (WHERE pk.rn=1 AND ff.fact_key='capital_expenditure' AND ff.quality_status='VALID' AND ff.normalized_value IS NOT NULL) capex,
    count(*) FILTER (WHERE pk.rn=1 AND ff.fact_key='net_borrowing' AND ff.quality_status='VALID' AND ff.normalized_value IS NOT NULL) net_borrowing,
    count(*) FILTER (WHERE pk.rn=1 AND ff.fact_key='total_equity' AND ff.quality_status='VALID' AND ff.normalized_value>0) equity,
    count(*) FILTER (WHERE pk.rn<=2 AND ff.fact_key='net_profit' AND ff.quality_status='VALID' AND ff.normalized_value>0) positive_profits,
    count(*) FILTER (WHERE pk.rn<=2 AND ff.fact_key='net_profit' AND ff.quality_status='VALID' AND ff.normalized_unit IS NOT NULL) profit_units,
    max(ff.normalized_unit) FILTER (WHERE pk.rn=1 AND ff.fact_key='eps_basic' AND ff.quality_status='VALID') eps_unit
  FROM period_keys pk
  LEFT JOIN financial_periods fp ON fp.issuer_id=pk.issuer_id AND fp.end_date=pk.end_date
    AND fp.length_months=pk.length_months AND fp.audited=pk.audited AND fp.scope=pk.scope
  LEFT JOIN financial_facts ff ON ff.period_id=fp.id
  WHERE pk.rn<=2 GROUP BY pk.issuer_id
), intrinsic_inputs AS (
  SELECT pk.issuer_id,
    count(*) FILTER (WHERE pk.rn=1 AND vi.input_key='cost_of_equity'
      AND vi.quality_status='VALID' AND vi.value>0) cost_of_equity,
    count(*) FILTER (WHERE pk.rn=1 AND vi.input_key='terminal_growth'
      AND vi.quality_status='VALID') terminal_growth
  FROM period_keys pk
  LEFT JOIN financial_periods fp ON fp.issuer_id=pk.issuer_id AND fp.end_date=pk.end_date
    AND fp.length_months=pk.length_months AND fp.audited=pk.audited
    AND fp.scope IS NOT DISTINCT FROM pk.scope
  LEFT JOIN valuation_inputs vi ON vi.period_id=fp.id
  WHERE pk.rn=1 GROUP BY pk.issuer_id
), actions AS (
  SELECT i.issuer_id,
    count(*) FILTER (WHERE ca.action_type ILIKE '%dividend%' OR ca.payload::text ILIKE '%dividend%' OR ca.payload::text LIKE '%تقسیم سود%') dividends,
    count(*) FILTER (WHERE ca.action_type ILIKE '%capital%' OR ca.payload::text ILIKE '%افزایش سرمایه%') capital_actions
  FROM corporate_actions ca JOIN instruments i ON i.id=ca.instrument_id GROUP BY i.issuer_id
), dividend_notices AS (
  SELECT issuer_id, count(*) AS disclosures
  FROM disclosures
  WHERE title ILIKE '%تقسیم سود%' OR title ILIKE '%تصمیمات مجمع%'
  GROUP BY issuer_id
)
SELECT a.symbol, coalesce(ind.model_family,'unclassified') model_family,
  (lp.shares_outstanding IS NOT NULL AND lp.shares_outstanding>0) shares_gate,
  coalesce(f.ocf,0)>0 ocf_gate,
  coalesce(f.capex,0)>0 capex_gate,
  coalesce(f.net_borrowing,0)>0 net_borrowing_gate,
  coalesce(ii.cost_of_equity,0)>0 cost_of_equity_gate,
  coalesce(ii.terminal_growth,0)>0 terminal_growth_gate,
  coalesce(f.equity,0)>0 equity_gate,
  coalesce(f.positive_profits,0)>=2 sustainable_profit_gate,
  coalesce(f.profit_units,0)>=2 unit_gate,
  (coalesce(ac.dividends,0)>0 OR coalesce(dn.disclosures,0)>0) dividend_evidence,
  coalesce(ac.capital_actions,0)>0 capital_action_evidence,
  lp.trading_date latest_price_date, f.eps_unit
FROM aliases a JOIN instruments ins ON ins.id=a.instrument_id
JOIN issuers iss ON iss.id=ins.issuer_id
LEFT JOIN industries ind ON ind.id=iss.industry_id
LEFT JOIN latest_price lp ON lp.instrument_id=ins.id
LEFT JOIN facts f ON f.issuer_id=iss.id
LEFT JOIN intrinsic_inputs ii ON ii.issuer_id=iss.id
LEFT JOIN actions ac ON ac.issuer_id=iss.id
LEFT JOIN dividend_notices dn ON dn.issuer_id=iss.id
WHERE ins.active AND (:symbol='' OR a.symbol=:symbol)
ORDER BY a.symbol
""")


CURRENT_PERIOD_KEYS_SQL = text("""
WITH aliases AS (
  SELECT instrument_id, min(symbol) AS symbol FROM symbol_aliases
  WHERE valid_to IS NULL GROUP BY instrument_id
), period_keys AS (
  SELECT issuer_id,end_date,end_date_jalali,length_months,audited,scope,
    dense_rank() OVER (PARTITION BY issuer_id ORDER BY end_date DESC,audited DESC) rn
  FROM financial_periods
  GROUP BY issuer_id,end_date,end_date_jalali,length_months,audited,scope
)
SELECT a.symbol,pk.issuer_id,pk.end_date,pk.end_date_jalali,
  pk.length_months,pk.audited,pk.scope
FROM aliases a
JOIN instruments ins ON ins.id=a.instrument_id
JOIN period_keys pk ON pk.issuer_id=ins.issuer_id AND pk.rn=1
WHERE ins.active AND (:symbol='' OR a.symbol=:symbol)
ORDER BY a.symbol,pk.end_date,pk.audited DESC,pk.scope
""")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--symbol', default='')
    args = parser.parse_args()
    with engine.begin() as connection:
        rows = [dict(row) for row in connection.execute(SQL, {'symbol': args.symbol}).mappings()]
        current_period_keys = [dict(row) for row in connection.execute(
            CURRENT_PERIOD_KEYS_SQL, {'symbol': args.symbol}
        ).mappings()]
    # PASS means that the explicit same-period FCFE path is evidence-ready.
    # OCF alone is not FCFE, and rates are never inferred from macro defaults.
    gates = (
        'shares_gate', 'ocf_gate', 'capex_gate', 'net_borrowing_gate',
        'cost_of_equity_gate', 'terminal_growth_gate', 'equity_gate',
        'sustainable_profit_gate', 'unit_gate',
    )
    for row in rows:
        passed = sum(bool(row[g]) for g in gates)
        row['status'] = 'PASS' if passed == len(gates) else 'REVIEW'
        row['passed_gates'] = passed
    result = {'method':'same_period_fcfe_input_gate_audit','gates':list(gates),
              'current_period_key_fields':['symbol','issuer_id','end_date','end_date_jalali',
                                           'length_months','audited','scope'],
              'current_period_keys':current_period_keys,
              'rows':rows,'summary':{'symbols':len(rows),
              'current_period_keys':len(current_period_keys),
              'pass':sum(r['status']=='PASS' for r in rows),
              'review':sum(r['status']=='REVIEW' for r in rows)}}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    print(json.dumps(result['summary'], ensure_ascii=False))


if __name__ == '__main__':
    main()
