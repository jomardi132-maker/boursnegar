#!/usr/bin/env python3
"""Export VALID Production facts with lineage and merge them into local SQLite.

The default is a read-only plan.  ``--apply`` creates a verified local backup,
imports a checksum-backed JSONL artifact, and recalculates local coverage.
Production is never modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def output_type(fact_key: str) -> str:
    if fact_key in {'total_assets', 'total_liabilities', 'total_equity', 'nav_per_share', 'units_outstanding'}:
        return 'balance_sheet'
    if fact_key in {'operating_cash_flow', 'capital_expenditure', 'net_borrowing'}:
        return 'cash_flow'
    return 'income_statement'


def production_sql() -> str:
    return r"""
COPY (
  SELECT row_to_json(export_row)::text
  FROM (
    SELECT DISTINCT ON (sa.symbol,d.source_disclosure_id,ff.fact_key)
      sa.symbol,
      d.source_disclosure_id::text AS tracing_no,
      fp.end_date_jalali AS period_end_jalali,
      ff.fact_key,
      COALESCE(ff.normalized_value,ff.raw_value)::text AS value,
      ff.normalized_unit AS unit,
      dv.content_checksum,
      d.source,
      d.title,
      d.published_date_jalali,
      pv.parser_name,
      pv.version AS parser_version,
      dv.metadata
    FROM financial_facts ff
    JOIN financial_periods fp ON fp.id=ff.period_id
    JOIN disclosure_versions dv ON dv.id=fp.disclosure_version_id
    JOIN disclosures d ON d.id=dv.disclosure_id
    JOIN instruments i ON i.id=d.instrument_id
    JOIN symbol_aliases sa ON sa.instrument_id=i.id AND sa.valid_to IS NULL
    LEFT JOIN parser_versions pv ON pv.id=ff.parser_version_id
    WHERE ff.quality_status='VALID'
      AND d.source_disclosure_id IS NOT NULL
      AND fp.end_date_jalali IS NOT NULL
      AND dv.content_checksum IS NOT NULL
    ORDER BY sa.symbol,d.source_disclosure_id,ff.fact_key,fp.end_date DESC,ff.created_at DESC
  ) export_row
) TO STDOUT;
"""


def export_from_server(target: str, artifact_dir: Path) -> dict:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    destination = artifact_dir / 'normalized.jsonl'
    remote = ['ssh', target, 'cd /tmp && sudo -u postgres psql -X -q -d boursnegar_db']
    process = subprocess.Popen(remote, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, encoding='utf-8')
    stdout, stderr = process.communicate(production_sql(), timeout=900)
    if process.returncode:
        raise SystemExit(f'Production export failed: {stderr.strip()}')
    records = 0
    with destination.open('w', encoding='utf-8') as handle:
        for number, line in enumerate(stdout.splitlines(), 1):
            if not line.strip():
                continue
            try:
                source = json.loads(line)
            except json.JSONDecodeError as exc:
                destination.unlink(missing_ok=True)
                raise SystemExit(f'Production export returned invalid JSON at line {number}: {exc}')
            required = ('symbol', 'tracing_no', 'period_end_jalali', 'fact_key', 'content_checksum')
            if any(not source.get(key) for key in required):
                destination.unlink(missing_ok=True)
                raise SystemExit(f'Production export row {number} lacks required lineage')
            record = {
                'source': 'production/boursnegar_db',
                'symbol': source['symbol'],
                'tracing_no': str(source['tracing_no']),
                'output_type': output_type(str(source['fact_key'])),
                'period_end_jalali': source['period_end_jalali'],
                'fact_key': source['fact_key'],
                'value': source.get('value'),
                'source_label': source['fact_key'],
                'payload': {
                    'production_source': source.get('source'),
                    'title': source.get('title'),
                    'published_date_jalali': source.get('published_date_jalali'),
                    'unit': source.get('unit'),
                    'parser_name': source.get('parser_name'),
                    'parser_version': source.get('parser_version'),
                    'metadata': source.get('metadata'),
                    'production_content_checksum': source['content_checksum'],
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + '\n')
            records += 1
    manifest = {
        'schema': 'boursnegar-production-local-mirror-v1',
        'source': 'production/boursnegar_db',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'files': [{'path': destination.name, 'records': records, 'sha256': sha256(destination)}],
        'errors': [],
    }
    (artifact_dir / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return manifest


def table_counts(db_path: Path) -> dict:
    connection = sqlite3.connect(db_path)
    try:
        return {table: connection.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
                for table in ('notices', 'notice_events', 'facts')}
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', default='data-service/artifacts/local-ingestion.sqlite3')
    parser.add_argument('--ssh-target', default='boursnegar')
    parser.add_argument('--out-root', default='data-service/artifacts/server-to-local')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    db_path = Path(args.db).resolve()
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    artifact_dir = Path(args.out_root).resolve() / run_id / 'normalized'
    manifest = export_from_server(args.ssh_target, artifact_dir)
    result = {'status': 'planned', 'manifest': str(artifact_dir / 'manifest.json'),
              'records': manifest['files'][0]['records']}
    if args.apply:
        sys.path.insert(0, str(ROOT / 'data-service'))
        from scripts.auto_local_to_production import backup_local_sqlite, validate_artifact_directory
        errors = validate_artifact_directory(artifact_dir)
        if errors:
            raise SystemExit(f'Export validation failed: {errors[:3]}')
        before = table_counts(db_path)
        backup = backup_local_sqlite(db_path)
        subprocess.run([PYTHON, str(ROOT / 'data-service/scripts/build_local_codal_db.py'),
                        '--db', str(db_path), '--artifact', str(artifact_dir)], check=True, timeout=900)
        subprocess.run([PYTHON, str(ROOT / 'data-service/scripts/recalculate_local_coverage.py'),
                        '--db', str(db_path), '--export',
                        str(ROOT / 'data-service/artifacts/local-coverage-latest.csv')], check=True, timeout=300)
        after = table_counts(db_path)
        result.update({'status': 'applied', 'backup': backup, 'before': before, 'after': after,
                       'inserted': {key: after[key] - before[key] for key in before}})
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
