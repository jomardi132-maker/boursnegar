#!/usr/bin/env python3
"""Run checkpointed local completion batches until a safe stop condition.

The supervisor never writes to Production.  It stops on queue exhaustion, the
first failed batch, or repeated batches that yield no new local facts.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable


def fact_count(db: Path) -> int:
    connection = sqlite3.connect(db)
    try:
        return int(connection.execute('SELECT COUNT(*) FROM facts').fetchone()[0])
    finally:
        connection.close()


def run_streaming(command: list[str]) -> int:
    print(json.dumps({'batch_command': ' '.join(command)}, ensure_ascii=False), flush=True)
    process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True,
                               encoding='utf-8', errors='replace')
    assert process.stdout is not None
    for line in process.stdout:
        print(line.rstrip(), flush=True)
    return process.wait()


def should_stop_for_no_progress(consecutive: int, limit: int) -> bool:
    return consecutive >= limit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True)
    parser.add_argument('--ssh-target', default='boursnegar')
    parser.add_argument('--from-jalali', required=True)
    parser.add_argument('--to-jalali', required=True)
    parser.add_argument('--batch-size', type=int, default=10)
    parser.add_argument('--max-batches', type=int, default=100)
    parser.add_argument('--max-no-progress', type=int, default=3)
    parser.add_argument('--run-root', required=True)
    # Accepted explicitly to make the no-Production boundary visible in logs
    # and in GUI command-contract tests.
    parser.add_argument('--skip-production', action='store_true', required=True)
    args = parser.parse_args()
    if not 1 <= args.batch_size <= 1524:
        raise SystemExit('batch-size must be between 1 and 1524')
    if args.max_batches < 1 or args.max_no_progress < 1:
        raise SystemExit('supervisor limits must be positive')

    db = Path(args.db).resolve()
    supervisor_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    report_root = Path(args.run_root).resolve() / 'supervisor' / supervisor_id
    no_progress = 0
    batches: list[dict] = []
    stop_reason = 'max-batches'
    for ordinal in range(1, args.max_batches + 1):
        report = report_root / f'batch-{ordinal:03d}.json'
        before = fact_count(db)
        command = [
            PYTHON, str(ROOT / 'data-service/scripts/auto_local_to_production.py'),
            '--db', str(db), '--ssh-target', args.ssh_target,
            '--from-jalali', args.from_jalali, '--to-jalali', args.to_jalali,
            '--limit', str(args.batch_size), '--run-root', str(Path(args.run_root).resolve()),
            '--report', str(report), '--apply', '--allow-download', '--skip-production',
        ]
        code = run_streaming(command)
        after = fact_count(db)
        payload = json.loads(report.read_text(encoding='utf-8')) if report.exists() else {}
        selected = list((payload.get('plan') or {}).get('selected_symbols') or [])
        batch = {'ordinal': ordinal, 'exit_code': code, 'selected_symbols': selected,
                 'facts_before': before, 'facts_after': after, 'new_facts': after - before,
                 'report': str(report)}
        batches.append(batch)
        print(json.dumps({'supervisor_batch': batch}, ensure_ascii=False), flush=True)
        if code != 0:
            stop_reason = 'batch-failed'
            break
        if not selected:
            stop_reason = 'queue-exhausted'
            break
        no_progress = no_progress + 1 if after == before else 0
        if should_stop_for_no_progress(no_progress, args.max_no_progress):
            stop_reason = 'no-progress-safety-stop'
            break

    summary = {'status': 'passed' if stop_reason in {'queue-exhausted', 'max-batches'} else 'attention',
               'stop_reason': stop_reason, 'batches': batches, 'facts': fact_count(db)}
    report_root.mkdir(parents=True, exist_ok=True)
    (report_root / 'supervisor-report.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'continuous_local_completion': summary}, ensure_ascii=False), flush=True)
    if stop_reason == 'batch-failed':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
