#!/usr/bin/env python3
"""Recalculate local symbol coverage tiers from the local SQLite mirror.

This script is local-only. It never connects to Production and never invents
financial values; it only counts distinct local fact keys and periods.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="artifacts/local-ingestion.sqlite3")
    args = parser.parse_args()
    path = Path(args.db).resolve()
    db = sqlite3.connect(path)
    rows = db.execute(
        """
        SELECT s.symbol,
               COUNT(DISTINCT CASE WHEN f.fact_key <> '' THEN f.fact_key END),
               COUNT(DISTINCT CASE WHEN f.period_end_jalali <> '' THEN f.period_end_jalali END)
        FROM symbols s LEFT JOIN facts f ON f.symbol=s.symbol
        GROUP BY s.symbol
        """
    ).fetchall()
    for symbol, fact_count, period_count in rows:
        status = "complete" if fact_count >= 7 and period_count >= 2 else (
            "comparable" if period_count >= 2 else "incomplete"
        )
        db.execute(
            "UPDATE symbols SET standard_count=?, period_count=?, status=? WHERE symbol=?",
            (fact_count, period_count, status, symbol),
        )
    db.commit()
    counts = dict(db.execute("SELECT status, COUNT(*) FROM symbols GROUP BY status").fetchall())
    print(json.dumps({"db": str(path), "symbols": len(rows), "tiers": counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
