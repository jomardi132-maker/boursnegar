#!/usr/bin/env python3
"""Run the Production backup-retention validator in non-destructive mode."""
from __future__ import annotations
import json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def main() -> int:
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = ROOT / 'data-service' / 'artifacts' / 'retention-cycle' / f'{stamp}.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    target = os.environ.get('BOURSNEGAR_SSH_TARGET', 'boursnegar')
    try:
        result = subprocess.run(['ssh', target, 'cd /var/www/boursnegar-data-current && scripts/production-backup-retention.sh'], cwd=ROOT, text=True, capture_output=True, check=True)
        report = {'schema':'boursnegar-scheduled-retention-v1','status':'success','generated_at':datetime.now(timezone.utc).isoformat(),'stdout':result.stdout,'stderr':result.stderr}
    except subprocess.CalledProcessError as exc:
        report = {'schema':'boursnegar-scheduled-retention-v1','status':'failed','generated_at':datetime.now(timezone.utc).isoformat(),'stdout':exc.stdout,'stderr':exc.stderr}
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status':report['status'],'report':str(out)}, ensure_ascii=False))
    return 0 if report['status']=='success' else 1

if __name__ == '__main__':
    raise SystemExit(main())
