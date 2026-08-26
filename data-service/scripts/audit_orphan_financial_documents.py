#!/usr/bin/env python3
"""Parse unreferenced local financial documents without importing inferred facts."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from app.services.codal_excel_parser import parse_financial_statement


SCHEMA = """
CREATE TABLE IF NOT EXISTS artifact_parse_results(
  path TEXT PRIMARY KEY, checksum TEXT NOT NULL, inferred_symbol TEXT,
  symbol_evidence TEXT, period_candidates TEXT NOT NULL, found_items TEXT NOT NULL,
  tables_scanned INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL, error TEXT,
  parsed_at TEXT NOT NULL, selected_period TEXT, period_evidence TEXT, metrics_json TEXT,
  linked_tracing_no TEXT, linkage_evidence TEXT
);
CREATE TABLE IF NOT EXISTS orphan_fact_candidates(
  path TEXT NOT NULL, fact_key TEXT NOT NULL, checksum TEXT NOT NULL,
  inferred_symbol TEXT NOT NULL, period_end_jalali TEXT NOT NULL, value REAL NOT NULL,
  status TEXT NOT NULL DEFAULT 'READY_FOR_LINKAGE', evidence TEXT NOT NULL,
  tracing_no TEXT, linkage_evidence TEXT,
  PRIMARY KEY(path,fact_key)
);
"""
DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
DATE_RE = re.compile(r'(?<!\d)(14\d{2})[/.-](\d{1,2})[/.-](\d{1,2})(?!\d)')


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def batch_symbol(path: Path) -> tuple[str | None, str | None]:
    symbols: set[str] = set()
    for bundle in path.parent.glob('*.jsonl'):
        with bundle.open(encoding='utf-8', errors='replace') as handle:
            for line in handle:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                symbol = row.get('symbol') or (row.get('letter') or {}).get('Symbol')
                if symbol:
                    symbols.add(str(symbol))
    if len(symbols) == 1:
        return next(iter(symbols)), 'unique_symbol_in_sibling_capture'
    return None, 'ambiguous_sibling_capture' if symbols else None


def period_candidates(content: bytes) -> list[str]:
    text = content.decode('utf-8', errors='ignore').translate(DIGITS)
    dates = set()
    for year, month, day in DATE_RE.findall(text):
        y, m, d = int(year), int(month), int(day)
        if 1400 <= y <= 1499 and 1 <= m <= 12 and 1 <= d <= 31:
            dates.add(f'{y:04d}/{m:02d}/{d:02d}')
    return sorted(dates)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', required=True)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--only-with-facts', action='store_true')
    parser.add_argument('--only-ready-period', action='store_true')
    args = parser.parse_args()
    db = sqlite3.connect(args.db)
    db.executescript(SCHEMA)
    columns = {row[1] for row in db.execute('PRAGMA table_info(artifact_parse_results)')}
    for column in ('selected_period', 'period_evidence', 'metrics_json', 'linked_tracing_no', 'linkage_evidence'):
        if column not in columns:
            db.execute(f'ALTER TABLE artifact_parse_results ADD COLUMN {column} TEXT')
    candidate_columns = {row[1] for row in db.execute('PRAGMA table_info(orphan_fact_candidates)')}
    for column in ('tracing_no', 'linkage_evidence'):
        if column not in candidate_columns:
            db.execute(f'ALTER TABLE orphan_fact_candidates ADD COLUMN {column} TEXT')
    query = "SELECT path,actual_sha256 FROM artifact_files WHERE status='DISCOVERED' AND lower(path) LIKE '%.xls' ORDER BY path"
    if args.only_with_facts:
        query = """SELECT f.path,f.actual_sha256 FROM artifact_files f
            JOIN artifact_parse_results p ON p.path=f.path
            WHERE f.status='DISCOVERED' AND lower(f.path) LIKE '%.xls'
              AND p.status='PARSED_WITH_FACTS' ORDER BY f.path"""
    if args.only_ready_period:
        query = """SELECT f.path,f.actual_sha256 FROM artifact_files f
            JOIN artifact_parse_results p ON p.path=f.path
            WHERE f.status='DISCOVERED' AND lower(f.path) LIKE '%.xls'
              AND p.status='PARSED_WITH_FACTS' AND p.inferred_symbol IS NOT NULL
              AND p.selected_period IS NOT NULL ORDER BY f.path"""
    rows = db.execute(query).fetchall()
    if args.limit is not None:
        rows = rows[:args.limit]
    counts: dict[str, int] = {}
    now = datetime.now(timezone.utc).isoformat()
    for index, (raw_path, ledger_sha) in enumerate(rows, 1):
        path = Path(raw_path)
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        symbol, evidence = batch_symbol(path)
        content = path.read_bytes()
        checksum = sha256(path)
        dates = period_candidates(content)
        try:
            parsed = parse_financial_statement(content)
            found = parsed['found_items']
            status = 'PARSED_WITH_FACTS' if found else 'PARSED_NO_CORE_FACTS'
            error = None
            tables = int(parsed['tables_scanned'])
            source_periods = {key: value for key, value in parsed.get('source_periods', {}).items() if value}
            unique_periods = set(source_periods.values())
            selected_period = next(iter(unique_periods)) if len(unique_periods) == 1 else None
            period_evidence = json.dumps(source_periods, ensure_ascii=False)
            metrics_json = json.dumps(parsed['metrics'], ensure_ascii=False, sort_keys=True)
        except Exception as exc:
            found, tables, status, error = [], 0, 'PARSE_FAILED', str(exc)
            selected_period, period_evidence, metrics_json = None, None, None
        db.execute(
            '''INSERT OR REPLACE INTO artifact_parse_results
               (path,checksum,inferred_symbol,symbol_evidence,period_candidates,found_items,
                tables_scanned,status,error,parsed_at,selected_period,period_evidence,metrics_json)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (raw_path, checksum or ledger_sha, symbol, evidence,
             json.dumps(dates, ensure_ascii=False), json.dumps(found, ensure_ascii=False),
             tables, status, error, now, selected_period, period_evidence, metrics_json),
        )
        db.execute('DELETE FROM orphan_fact_candidates WHERE path=?', (raw_path,))
        if status == 'PARSED_WITH_FACTS' and symbol and selected_period:
            evidence_payload = json.dumps({
                'symbol': evidence, 'period': json.loads(period_evidence), 'document_sha256': checksum
            }, ensure_ascii=False, sort_keys=True)
            for fact_key in found:
                value = parsed['metrics'].get(fact_key)
                if value is not None:
                    db.execute(
                        '''INSERT INTO orphan_fact_candidates
                           (path,fact_key,checksum,inferred_symbol,period_end_jalali,value,status,evidence)
                           VALUES(?,?,?,?,?,?,?,?)''',
                        (raw_path, fact_key, checksum, symbol, selected_period, value,
                         'READY_FOR_LINKAGE', evidence_payload),
                    )
        counts[status] = counts.get(status, 0) + 1
        if index % 50 == 0:
            db.commit()
            print(json.dumps({'processed': index, 'total': len(rows), 'statuses': counts}, ensure_ascii=False), flush=True)
    db.execute("UPDATE orphan_fact_candidates SET status='READY_FOR_LINKAGE'")
    db.execute("""UPDATE orphan_fact_candidates AS c SET status='NEEDS_DISAMBIGUATION'
        WHERE EXISTS (SELECT 1 FROM facts f WHERE f.symbol=c.inferred_symbol
          AND f.period_end_jalali=c.period_end_jalali AND f.fact_key=c.fact_key
          AND CAST(f.value AS REAL)<>c.value)""")
    db.execute("""UPDATE orphan_fact_candidates AS c SET status='DUPLICATE_EXISTING'
        WHERE EXISTS (SELECT 1 FROM facts f WHERE f.symbol=c.inferred_symbol
          AND f.period_end_jalali=c.period_end_jalali AND f.fact_key=c.fact_key
          AND CAST(f.value AS REAL)=c.value)""")
    db.commit()
    print(json.dumps({'processed': len(rows), 'statuses': counts}, ensure_ascii=False))


if __name__ == '__main__':
    main()
