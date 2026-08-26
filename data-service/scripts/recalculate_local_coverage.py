#!/usr/bin/env python3
"""Recalculate local symbol coverage tiers from the local SQLite mirror.

This script is local-only. It never connects to Production and never invents
financial values; it only counts distinct local fact keys and periods.
"""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="artifacts/local-ingestion.sqlite3")
    parser.add_argument("--export", default="")
    args = parser.parse_args()
    path = Path(args.db).resolve()
    db = sqlite3.connect(path)
    try:
        db.execute("ALTER TABLE symbols ADD COLUMN gap_summary TEXT NOT NULL DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        db.execute("ALTER TABLE symbols ADD COLUMN last_error TEXT")
    except sqlite3.OperationalError:
        pass
    rows = db.execute(
        """
        SELECT s.symbol,
               COUNT(DISTINCT CASE WHEN f.fact_key <> '' THEN f.fact_key END),
               COUNT(DISTINCT CASE WHEN f.period_end_jalali <> '' THEN f.period_end_jalali END),
               COUNT(DISTINCT CASE WHEN f.output_type='income_statement' THEN f.fact_key END),
               COUNT(DISTINCT CASE WHEN f.output_type='balance_sheet' THEN f.fact_key END),
               COUNT(DISTINCT n.tracing_no)
        FROM symbols s LEFT JOIN facts f ON f.symbol=s.symbol
        LEFT JOIN notices n ON n.symbol=s.symbol
        GROUP BY s.symbol
        """
    ).fetchall()
    for symbol, fact_count, period_count, income_count, balance_count, notice_count in rows:
        status = "complete" if fact_count >= 7 and period_count >= 2 else (
            "comparable" if period_count >= 2 else "incomplete"
        )
        gaps=[]
        if income_count == 0: gaps.append('صورت سود و زیان')
        if balance_count == 0: gaps.append('ترازنامه')
        if period_count < 2: gaps.append('دوره مقایسه‌ای')
        if notice_count == 0: gaps.append('اطلاعیه')
        if fact_count < 7: gaps.append('factهای هسته‌ای')
        db.execute(
            "UPDATE symbols SET standard_count=?, period_count=?, status=?, gap_summary=? WHERE symbol=?",
            (fact_count, period_count, status, '، '.join(gaps) if gaps else 'بدون کمبود شناخته‌شده', symbol),
        )
    db.commit()
    counts = dict(db.execute("SELECT status, COUNT(*) FROM symbols GROUP BY status").fetchall())
    if args.export:
        export_path = Path(args.export).resolve()
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with export_path.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow(("نماد", "صنعت", "وضعیت", "fact", "دوره", "کمبودها", "خطا"))
            writer.writerows(db.execute("SELECT symbol,industry,status,standard_count,period_count,gap_summary,last_error FROM symbols ORDER BY symbol"))
    print(json.dumps({"db": str(path), "symbols": len(rows), "tiers": counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
