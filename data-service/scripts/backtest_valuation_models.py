#!/usr/bin/env python3
"""Evidence-only forward validation for persisted valuation snapshots.

This is deliberately not an investment-performance claim: it reports how
often a model's value gap and the following 20 valid sessions can be compared.
Rows without a valid future price remain explicitly unevaluable.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlalchemy import text

from app.database import engine


SQL = text("""
WITH aliases AS (
  SELECT instrument_id, min(symbol) AS symbol
  FROM symbol_aliases WHERE valid_to IS NULL GROUP BY instrument_id
), snapshots AS (
  SELECT s.id, s.instrument_id, s.calculated_at, s.coverage, s.confidence,
         vr.model_type, vr.model_version, vr.fair_value_base,
         vr.assumptions->>'basisSource' AS basis_source
  FROM analytical_snapshots s
  JOIN valuation_results vr ON vr.snapshot_id=s.id
  WHERE vr.fair_value_base > 0
), priced AS (
  SELECT sn.*, a.symbol,
         p0.adjusted_close AS entry_price,
         p0.trading_date AS entry_date,
         p5.adjusted_close AS exit_5_price, p5.trading_date AS exit_5_date,
         p10.adjusted_close AS exit_10_price, p10.trading_date AS exit_10_date,
         p20.adjusted_close AS exit_20_price, p20.trading_date AS exit_20_date
  FROM snapshots sn
  JOIN aliases a ON a.instrument_id=sn.instrument_id
  JOIN LATERAL (
    SELECT coalesce(p.adjusted_close,p.close) AS adjusted_close,p.trading_date
    FROM daily_prices p
    WHERE p.instrument_id=sn.instrument_id
      AND p.quality_status='VALID' AND p.volume>0
      AND p.trading_date::timestamptz >= sn.calculated_at
    ORDER BY p.trading_date ASC LIMIT 1
  ) p0 ON true
  LEFT JOIN LATERAL (
    SELECT coalesce(p.adjusted_close,p.close) AS adjusted_close,p.trading_date
    FROM daily_prices p
    WHERE p.instrument_id=sn.instrument_id
      AND p.quality_status='VALID' AND p.volume>0
      AND p.trading_date > p0.trading_date
    ORDER BY p.trading_date ASC LIMIT 1 OFFSET 4
  ) p5 ON true
  LEFT JOIN LATERAL (
    SELECT coalesce(p.adjusted_close,p.close) AS adjusted_close,p.trading_date
    FROM daily_prices p
    WHERE p.instrument_id=sn.instrument_id
      AND p.quality_status='VALID' AND p.volume>0
      AND p.trading_date > p0.trading_date
    ORDER BY p.trading_date ASC LIMIT 1 OFFSET 9
  ) p10 ON true
  LEFT JOIN LATERAL (
    SELECT coalesce(p.adjusted_close,p.close) AS adjusted_close,p.trading_date
    FROM daily_prices p
    WHERE p.instrument_id=sn.instrument_id
      AND p.quality_status='VALID' AND p.volume>0
      AND p.trading_date > p0.trading_date
    ORDER BY p.trading_date ASC LIMIT 1 OFFSET 19
  ) p20 ON true
)
SELECT symbol, model_type, model_version, basis_source, calculated_at,
       coverage, confidence, entry_date, entry_price,
       fair_value_base,
       round(((fair_value_base / nullif(entry_price,0))-1)*100,2) AS value_gap_pct,
       exit_5_price, exit_5_date, exit_10_price, exit_10_date,
       exit_20_price, exit_20_date
FROM priced
WHERE (:symbol = '' OR symbol=:symbol)
ORDER BY calculated_at, symbol
""")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--symbol", default="")
    args = parser.parse_args()
    with engine.begin() as connection:
        rows = [dict(row) for row in connection.execute(SQL, {"symbol": args.symbol}).mappings()]
    horizons = {}
    for horizon in (5, 10, 20):
        comparable = [row for row in rows if row[f"exit_{horizon}_price"] is not None]
        by_model = {}
        for row in comparable:
            key = row["model_type"]
            bucket = by_model.setdefault(key, {"snapshots": 0, "mean_value_gap_pct": None,
                                               "mean_forward_return_pct": None})
            bucket["snapshots"] += 1
            bucket.setdefault("_gaps", []).append(float(row["value_gap_pct"]))
            bucket.setdefault("_returns", []).append(round((float(row[f"exit_{horizon}_price"]) / float(row["entry_price"]) - 1) * 100, 2))
        for bucket in by_model.values():
            bucket["mean_value_gap_pct"] = round(sum(bucket.pop("_gaps")) / bucket["snapshots"], 2)
            bucket["mean_forward_return_pct"] = round(sum(bucket.pop("_returns")) / bucket["snapshots"], 2)
        horizons[str(horizon)] = {
            "comparable_snapshots": len(comparable),
            "statistical_gate": "READY" if len(comparable) >= 30 else "INSUFFICIENT_SAMPLE",
            "minimum_required": 30,
            "by_model": by_model,
        }
    result = {
        "method": "forward_valid_sessions",
        "source_gate": "quality_status=VALID AND volume>0",
        "total_model_snapshots": len(rows),
        "horizons": horizons,
        "rows": rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("method", "total_model_snapshots", "horizons")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
