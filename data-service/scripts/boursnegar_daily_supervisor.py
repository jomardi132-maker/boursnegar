#!/usr/bin/env python3
"""Run the bounded daily Boursnegar workflow and write an auditable report.

The supervisor deliberately delegates collection/import/refresh to the existing
daily monitor. Historical recovery is never inferred from a daily run.
"""
from __future__ import annotations

import argparse
import glob
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / "data-service" / "venv" / "bin" / "python"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-import", action="store_true")
    parser.add_argument("--local-db", default=str(ROOT / "data-service/artifacts/local-ingestion.sqlite3"))
    parser.add_argument("--report-dir", default=str(ROOT / "data-service/artifacts/daily-supervisor"))
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    command = [str(PYTHON), "data-service/scripts/daily_codal_monitor.py",
               "--batch-size", str(args.batch_size), "--local-db", args.local_db]
    if args.force:
        command.append("--force")
    if args.no_import:
        command.append("--no-import")
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    plan_command = [str(PYTHON), "data-service/scripts/plan_local_recovery.py",
                    "--db", args.local_db,
                    "--out", str(report_dir / "local-recovery-plan.csv")]
    # Feed the newest authoritative Production coverage mirror into the next
    # recovery plan when available.  This keeps scheduling adaptive without
    # making Production a symbol source or inventing missing facts.
    coverage_files = glob.glob(str(ROOT / "data-service/artifacts/coverage-cycle-*/coverage-symbols.csv"))
    if coverage_files:
        latest_coverage = max(coverage_files, key=lambda item: Path(item).stat().st_mtime)
        plan_command += ["--coverage-csv", latest_coverage,
                         "--recent-artifact-root", str(ROOT / "data-service/artifacts")]
    plan_result = subprocess.run(plan_command, cwd=ROOT, capture_output=True, text=True)
    report = {
        "schema": "boursnegar-daily-supervisor-v1",
        "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "returncode": result.returncode,
        "status": "success" if result.returncode == 0 else "failed",
        "stdout": result.stdout,
        "stderr": result.stderr,
        "recovery_plan": {
            "command": plan_command,
            "returncode": plan_result.returncode,
            "stdout": plan_result.stdout,
            "stderr": plan_result.stderr,
        },
        "historical_recovery": "separate-explicit-workflow",
        "provenance_policy": "official-evidence-only-no-fabrication",
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = report_dir / f"{stamp}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(path), "returncode": result.returncode}, ensure_ascii=False))
    return result.returncode or plan_result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
