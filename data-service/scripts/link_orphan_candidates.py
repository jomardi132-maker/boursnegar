#!/usr/bin/env python3
"""Link staged orphan facts to a unique captured Codal tracing number."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from app.services.codal_excel_parser import extract_period_end_jalali


def captured_excel_letters(folder: Path) -> dict[tuple[str, str], set[str]]:
    result: dict[tuple[str, str], set[str]] = {}
    for bundle in folder.glob('*.jsonl'):
        with bundle.open(encoding='utf-8', errors='replace') as handle:
            for line in handle:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                letter = row.get('letter') or {}
                symbol = row.get('symbol') or letter.get('Symbol')
                period = extract_period_end_jalali(str(letter.get('Title') or ''))
                tracing = str(letter.get('TracingNo') or '')
                has_excel = bool(letter.get('HasExcel') or letter.get('ExcelUrl'))
                if symbol and period and tracing and has_excel:
                    result.setdefault((str(symbol), period), set()).add(tracing)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', required=True)
    args = parser.parse_args()
    db = sqlite3.connect(args.db)
    for table in ('artifact_parse_results', 'orphan_fact_candidates'):
        columns = {row[1] for row in db.execute(f'PRAGMA table_info({table})')}
        for column in ('linked_tracing_no', 'linkage_evidence') if table == 'artifact_parse_results' else ('tracing_no', 'linkage_evidence'):
            if column not in columns:
                db.execute(f'ALTER TABLE {table} ADD COLUMN {column} TEXT')
    rows = db.execute("""SELECT path,inferred_symbol,selected_period FROM artifact_parse_results
        WHERE status='PARSED_WITH_FACTS' AND inferred_symbol IS NOT NULL AND selected_period IS NOT NULL""").fetchall()
    cache: dict[Path, dict[tuple[str, str], set[str]]] = {}
    linked = ambiguous = missing = 0
    for raw_path, symbol, period in rows:
        path = Path(raw_path)
        if not path.is_absolute():
            path = ROOT / path
        letters = cache.setdefault(path.parent, captured_excel_letters(path.parent))
        matches = sorted(letters.get((symbol, period), set()))
        evidence = json.dumps({'rule': 'unique_excel_letter_in_same_batch_symbol_period', 'matches': matches}, ensure_ascii=False)
        tracing = matches[0] if len(matches) == 1 else None
        if tracing:
            linked += 1
        elif matches:
            ambiguous += 1
        else:
            missing += 1
        db.execute('UPDATE artifact_parse_results SET linked_tracing_no=?,linkage_evidence=? WHERE path=?',
                   (tracing, evidence, raw_path))
        db.execute('UPDATE orphan_fact_candidates SET tracing_no=?,linkage_evidence=? WHERE path=?',
                   (tracing, evidence, raw_path))
    db.execute("""UPDATE orphan_fact_candidates SET status='READY_FOR_NORMALIZATION'
        WHERE status='READY_FOR_LINKAGE' AND tracing_no IS NOT NULL""")
    db.execute("""UPDATE orphan_fact_candidates SET status='READY_FOR_NORMALIZATION'
        WHERE status='READY_FOR_IMPORT' AND tracing_no IS NOT NULL""")
    db.commit()
    print(json.dumps({'files': len(rows), 'linked': linked, 'ambiguous': ambiguous, 'missing': missing}, ensure_ascii=False))


if __name__ == '__main__':
    main()
