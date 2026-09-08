#!/usr/bin/env python3
"""Recover a moved artifact archive into the canonical local database."""
from __future__ import annotations
import argparse, json, sqlite3, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable
DEFAULT_ARCHIVE = Path('/home/king/Boursnegar-artifacts-archive-20260906')

def integrity(path: Path) -> str:
    connection = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
    try: return str(connection.execute('PRAGMA integrity_check').fetchone()[0])
    finally: connection.close()

def merge_archive_database(current: Path, archive: Path) -> dict:
    connection = sqlite3.connect(current, timeout=120)
    tables = ('notices', 'notice_events', 'facts')
    before = {table: connection.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] for table in tables}
    try:
        connection.execute('ATTACH DATABASE ? AS archive_db', (str(archive),))
        connection.execute('BEGIN IMMEDIATE')
        for table in tables:
            columns = [row[1] for row in connection.execute(f'PRAGMA main.table_info({table})')]
            archive_columns = {row[1] for row in connection.execute(f'PRAGMA archive_db.table_info({table})')}
            shared = [column for column in columns if column in archive_columns]
            names = ','.join(shared)
            connection.execute(f'INSERT OR IGNORE INTO main.{table}({names}) SELECT {names} FROM archive_db.{table}')
        connection.commit()
    finally:
        try: connection.execute('DETACH DATABASE archive_db')
        except sqlite3.Error: pass
    after = {table: connection.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] for table in tables}
    check = connection.execute('PRAGMA integrity_check').fetchone()[0]
    connection.close()
    return {'before': before, 'after': after,
            'inserted': {table: after[table] - before[table] for table in tables},
            'integrity_check': check}

def run(command: list[str]) -> dict:
    print(json.dumps({'step': ' '.join(command)}, ensure_ascii=False), flush=True)
    completed = subprocess.run(command, cwd=ROOT, check=True, timeout=7200,
                               text=True, capture_output=True, encoding='utf-8', errors='replace')
    if completed.stdout: print(completed.stdout.rstrip(), flush=True)
    return {'command': command, 'stdout': completed.stdout.strip()}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', default='data-service/artifacts/local-ingestion.sqlite3')
    parser.add_argument('--archive', default=str(DEFAULT_ARCHIVE))
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--skip-document-audit', action='store_true')
    args = parser.parse_args()
    db = Path(args.db).resolve()
    archive_root = Path(args.archive).resolve()
    archive_db = archive_root / 'local-ingestion.sqlite3'
    if not archive_db.is_file(): raise SystemExit(f'archive database not found: {archive_db}')
    checks = {'current': integrity(db), 'archive': integrity(archive_db)}
    if any(value != 'ok' for value in checks.values()):
        raise SystemExit(f'SQLite integrity gate failed: {checks}')
    report = {'schema': 'boursnegar-local-archive-recovery-v1',
              'started_at': datetime.now(timezone.utc).isoformat(),
              'archive': str(archive_root), 'integrity': checks,
              'mode': 'apply' if args.apply else 'plan'}
    if not args.apply:
        print(json.dumps(report, ensure_ascii=False)); return
    sys.path.insert(0, str(ROOT / 'data-service'))
    from scripts.auto_local_to_production import backup_local_sqlite
    report['backup'] = backup_local_sqlite(db)
    report['database_merge'] = merge_archive_database(db, archive_db)
    steps = [run([PYTHON, str(ROOT/'data-service/scripts/reconcile_local_artifacts.py'),
                  '--db', str(db), '--root', str(archive_root)])]
    if not args.skip_document_audit:
        steps.append(run([PYTHON, str(ROOT/'data-service/scripts/audit_orphan_financial_documents.py'), '--db', str(db)]))
        steps.append(run([PYTHON, str(ROOT/'data-service/scripts/link_orphan_candidates.py'), '--db', str(db)]))
        steps.append(run([PYTHON, str(ROOT/'data-service/scripts/promote_local_candidates.py'), '--db', str(db)]))
        steps.append(run([PYTHON, str(ROOT/'data-service/scripts/promote_local_candidates.py'), '--db', str(db), '--apply']))
    steps.append(run([PYTHON, str(ROOT/'data-service/scripts/recalculate_local_coverage.py'),
                      '--db', str(db), '--export', str(ROOT/'data-service/artifacts/local-coverage-latest.csv')]))
    report['steps'] = steps
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    report['final_integrity'] = integrity(db)
    destination = ROOT/'data-service/artifacts/archive-recovery-latest.json'
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': 'completed', 'report': str(destination),
                      'integrity': report['final_integrity']}, ensure_ascii=False))

if __name__ == '__main__': main()
