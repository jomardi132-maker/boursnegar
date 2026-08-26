#!/usr/bin/env python3
"""Promote only fully linked, scoped orphan candidates into local facts."""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone


OUTPUT_TYPES = {
    'total_assets': 'balance_sheet', 'total_liabilities': 'balance_sheet',
    'total_equity': 'balance_sheet',
    'revenue': 'income_statement', 'cogs': 'income_statement',
    'gross_profit': 'income_statement', 'operating_profit': 'income_statement',
    'net_profit': 'income_statement', 'eps_basic': 'income_statement',
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    db = sqlite3.connect(args.db)
    rows = db.execute("""SELECT path,fact_key,checksum,inferred_symbol,period_end_jalali,value,
        tracing_no,report_scope,evidence FROM orphan_fact_candidates
        WHERE status='READY_FOR_NORMALIZATION' AND report_scope IS NOT NULL
          AND tracing_no IS NOT NULL ORDER BY path,fact_key""").fetchall()
    eligible = inserted = skipped = 0
    for path, key, checksum, symbol, period, value, tracing, scope, evidence in rows:
        eligible += 1
        output_type = OUTPUT_TYPES.get(key)
        if not output_type:
            skipped += 1
            continue
        if not args.apply:
            continue
        payload = json.dumps({
            'source': 'orphan_excel_candidate', 'document_path': path,
            'document_sha256': checksum, 'report_scope': scope,
            'linkage_evidence': evidence,
        }, ensure_ascii=False, sort_keys=True)
        inserted += db.execute('''INSERT OR IGNORE INTO facts
            (symbol,tracing_no,output_type,period_end_jalali,fact_key,value,source_label,payload,checksum)
            VALUES(?,?,?,?,?,?,?,?,?)''',
            (symbol, str(tracing), output_type, period, key, str(value),
             key, payload, checksum)).rowcount
    if args.apply:
        db.execute("""UPDATE orphan_fact_candidates SET status='PROMOTED_LOCAL'
            WHERE status='READY_FOR_NORMALIZATION' AND report_scope IS NOT NULL
              AND tracing_no IS NOT NULL""")
        db.commit()
    print(json.dumps({
        'eligible': eligible, 'inserted': inserted, 'skipped': skipped,
        'mode': 'apply' if args.apply else 'dry-run',
        'completed_at': datetime.now(timezone.utc).isoformat(),
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
