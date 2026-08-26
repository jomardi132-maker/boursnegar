#!/usr/bin/env python3
"""Inventory and reconcile existing local artifacts without downloading anything."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


LEDGER_SCHEMA = """
CREATE TABLE IF NOT EXISTS artifact_manifests(
  path TEXT PRIMARY KEY, schema_name TEXT, source TEXT, declared_files INTEGER NOT NULL,
  declared_records INTEGER NOT NULL, error_count INTEGER NOT NULL, status TEXT NOT NULL,
  scanned_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS artifact_files(
  path TEXT PRIMARY KEY, root_name TEXT NOT NULL, role TEXT NOT NULL, manifest_path TEXT,
  size_bytes INTEGER NOT NULL, expected_sha256 TEXT, actual_sha256 TEXT NOT NULL,
  declared_records INTEGER, json_records INTEGER, json_errors INTEGER NOT NULL DEFAULT 0,
  imported_rows INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL, scanned_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS artifact_errors(
  manifest_path TEXT NOT NULL, ordinal INTEGER NOT NULL, payload TEXT NOT NULL,
  PRIMARY KEY(manifest_path,ordinal)
);
CREATE TABLE IF NOT EXISTS ledger_runs(
  id INTEGER PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT, status TEXT NOT NULL,
  roots TEXT NOT NULL, summary TEXT
);
"""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def jsonl_counts(path: Path) -> tuple[int, int]:
    records = errors = 0
    with path.open(encoding='utf-8', errors='replace') as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                json.loads(line); records += 1
            except json.JSONDecodeError:
                errors += 1
    return records, errors


def role(path: Path) -> str:
    if path.name == 'manifest.json': return 'MANIFEST'
    if path.name == 'checkpoint.json': return 'CHECKPOINT'
    if path.suffix == '.jsonl': return 'DATA_JSONL'
    if path.suffix.lower() in {'.html', '.htm', '.xls', '.xlsx', '.pdf'}: return 'DOCUMENT'
    if path.suffix in {'.log', '.txt'}: return 'LOG'
    return 'OTHER'


def imported_by_checksum(db: sqlite3.Connection) -> dict[str, int]:
    result: dict[str, int] = {}
    for table in ('notices', 'facts', 'notice_events'):
        columns = {row[1] for row in db.execute(f'PRAGMA table_info({table})')}
        if 'checksum' not in columns:
            continue
        for checksum, count in db.execute(f'SELECT checksum,COUNT(*) FROM {table} WHERE checksum IS NOT NULL GROUP BY checksum'):
            result[checksum] = result.get(checksum, 0) + count
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='artifacts/local-ingestion.sqlite3')
    parser.add_argument('--root', action='append', required=True)
    args = parser.parse_args()
    db = sqlite3.connect(Path(args.db).resolve())
    db.executescript(LEDGER_SCHEMA)
    now = datetime.now(timezone.utc).isoformat()
    run = db.execute('INSERT INTO ledger_runs(started_at,status,roots) VALUES(?,?,?)',
                     (now, 'RUNNING', json.dumps(args.root, ensure_ascii=False))).lastrowid
    expected: dict[Path, tuple[str, int | None, str]] = {}
    manifests = errors_total = declared_records = 0
    roots = [Path(item).resolve() for item in args.root]
    try:
        # A ledger run is a fresh snapshot for the selected roots. Removing old
        # rows first prevents deleted junk or renamed files from lingering.
        for root in roots:
            root_rel = str(root.relative_to(Path.cwd())) if root.is_relative_to(Path.cwd()) else str(root)
            db.execute('DELETE FROM artifact_files WHERE root_name=?', (root.name,))
            db.execute('DELETE FROM artifact_errors WHERE manifest_path LIKE ?', (root_rel + '/%',))
            db.execute('DELETE FROM artifact_manifests WHERE path LIKE ?', (root_rel + '/%',))
        for root in roots:
            for manifest in sorted(root.rglob('manifest.json')):
                manifests += 1; rel = str(manifest.relative_to(Path.cwd())) if manifest.is_relative_to(Path.cwd()) else str(manifest)
                try:
                    data = json.loads(manifest.read_text(encoding='utf-8'))
                    items = data.get('files') or []; errs = data.get('errors') or []
                    count = sum(int(item.get('records', 0) or 0) for item in items); declared_records += count
                    status = 'HAS_ERRORS' if errs else 'VALID'
                    db.execute('INSERT OR REPLACE INTO artifact_manifests VALUES(?,?,?,?,?,?,?,?)',
                               (rel, data.get('schema'), data.get('source'), len(items), count, len(errs), status, now))
                    db.execute('DELETE FROM artifact_errors WHERE manifest_path=?', (rel,))
                    for ordinal, payload in enumerate(errs):
                        db.execute('INSERT INTO artifact_errors VALUES(?,?,?)', (rel, ordinal, json.dumps(payload, ensure_ascii=False)))
                    errors_total += len(errs)
                    for item in items:
                        name = item.get('path') or item.get('file')
                        if name:
                            bundle_path = (manifest.parent / name).resolve()
                            expected[bundle_path] = (str(item.get('sha256') or ''), item.get('records'), rel)
                            if data.get('schema') == 'boursnegar-browser-codal-jsonl-v1' and bundle_path.exists():
                                with bundle_path.open(encoding='utf-8', errors='replace') as handle:
                                    for line in handle:
                                        try: record = json.loads(line)
                                        except json.JSONDecodeError: continue
                                        for document in record.get('documents') or []:
                                            doc_name = document.get('path'); doc_sha = document.get('sha256')
                                            if doc_name:
                                                expected[(bundle_path.parent / doc_name).resolve()] = (str(doc_sha or ''), None, rel)
                    for document in data.get('source_documents') or []:
                        doc_name = document.get('path'); doc_sha = document.get('sha256')
                        if not doc_name: continue
                        doc_path = Path(doc_name)
                        if not doc_path.is_absolute():
                            doc_path = (Path.cwd() / doc_path) if doc_path.parts and doc_path.parts[0] == 'artifacts' else (manifest.parent / doc_path)
                        expected[doc_path.resolve()] = (str(doc_sha or ''), None, rel)
                except Exception as exc:
                    db.execute('INSERT OR REPLACE INTO artifact_manifests VALUES(?,?,?,?,?,?,?,?)',
                               (rel, None, None, 0, 0, 1, 'FAILED', now))
                    db.execute('INSERT OR REPLACE INTO artifact_errors VALUES(?,?,?)',
                               (rel, 0, json.dumps({'error': str(exc)}, ensure_ascii=False)))
                    errors_total += 1
        imported = imported_by_checksum(db)
        expected_by_sha: dict[str, tuple[int | None, str]] = {}
        for expected_sha, declared, manifest_path in expected.values():
            if expected_sha:
                expected_by_sha.setdefault(expected_sha, (declared, manifest_path))
        status_counts: dict[str, int] = {}
        scanned = 0
        for root in roots:
            for path in sorted(p for p in root.rglob('*') if p.is_file()):
                scanned += 1
                actual = sha256(path); expected_item = expected.get(path.resolve())
                checksum_item = expected_by_sha.get(actual)
                expected_sha, declared, manifest_path = expected_item or ('', None, '')
                if not expected_item and checksum_item:
                    expected_sha, manifest_path = actual, checksum_item[1]
                records = json_errors = 0
                if path.suffix == '.jsonl': records, json_errors = jsonl_counts(path)
                imported_rows = imported.get(actual, 0)
                if json_errors:
                    status = 'QUARANTINED'
                elif expected_sha and actual != expected_sha:
                    status = 'QUARANTINED'
                elif imported_rows:
                    status = 'IMPORTED'
                elif expected_item or checksum_item:
                    status = 'VERIFIED'
                elif role(path) in {'MANIFEST', 'CHECKPOINT', 'LOG', 'OTHER'}:
                    status = 'INVENTORIED'
                else:
                    status = 'DISCOVERED'
                status_counts[status] = status_counts.get(status, 0) + 1
                rel = str(path.relative_to(Path.cwd())) if path.is_relative_to(Path.cwd()) else str(path)
                db.execute('INSERT OR REPLACE INTO artifact_files VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                           (rel, root.name, role(path), manifest_path or None, path.stat().st_size,
                            expected_sha or None, actual, declared, records if path.suffix == '.jsonl' else None,
                            json_errors, imported_rows, status, now))
                if scanned % 250 == 0: db.commit()
        missing = 0
        for path, (expected_sha, declared, manifest_path) in expected.items():
            if path.exists(): continue
            missing += 1; status_counts['FAILED'] = status_counts.get('FAILED', 0) + 1
            rel = str(path.relative_to(Path.cwd())) if path.is_relative_to(Path.cwd()) else str(path)
            db.execute('INSERT OR REPLACE INTO artifact_files VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                       (rel, path.parts[-4] if len(path.parts) >= 4 else '', 'MISSING', manifest_path,
                        0, expected_sha or None, '', declared, None, 0, 0, 'FAILED', now))
        summary = {'manifests': manifests, 'manifest_errors': errors_total, 'declared_records': declared_records,
                   'files_scanned': scanned, 'missing_files': missing, 'statuses': status_counts}
        db.execute('UPDATE ledger_runs SET finished_at=?,status=?,summary=? WHERE id=?',
                   (datetime.now(timezone.utc).isoformat(), 'PASSED', json.dumps(summary, ensure_ascii=False), run))
        db.commit(); print(json.dumps(summary, ensure_ascii=False))
    except Exception as exc:
        db.execute('UPDATE ledger_runs SET finished_at=?,status=?,summary=? WHERE id=?',
                   (datetime.now(timezone.utc).isoformat(), 'FAILED', str(exc), run)); db.commit(); raise


if __name__ == '__main__': main()
