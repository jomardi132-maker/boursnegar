#!/usr/bin/env python3
"""Audit promotion reports without conflating legacy and current schemas."""
from __future__ import annotations

import argparse
import glob
import json
from collections import Counter
from pathlib import Path


def ok_report(report: dict) -> bool:
    schema = report.get("schema")
    if report.get("status") != "success":
        return False
    if not report.get("backup") or '"inserted": 0' not in report.get("idempotent_replay", ""):
        return False
    if '"status":"ready"' not in report.get("ready", ""):
        return False
    if schema == "boursnegar-notice-promotion-v1":
        return '"status":"ok"' in report.get("health", "")
    return schema == "boursnegar-evidence-promotion-v1"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default="data-service/artifacts")
    args = parser.parse_args()
    root = Path(args.root)
    # Cover both the historical follow-up layout and the canonical promotion
    # cycle reports.  Keep the patterns explicit so unrelated JSON artifacts
    # are not mistaken for promotion evidence.
    paths = sorted(set(
        glob.glob(str(root / "fund-nav-followup-*-docs" / "promotion-report.json"))
        + glob.glob(str(root / "promotion-cycle" / "*.json"))
        + glob.glob(str(root / "**" / "promotion-report.json"), recursive=True)
    ))
    schemas = Counter()
    failures = []
    legacy_unverified = []
    for path in paths:
        try:
            report = json.loads(Path(path).read_text(encoding="utf-8"))
            schemas[report.get("schema", "UNKNOWN")] += 1
            if not ok_report(report):
                if report.get("schema") == "boursnegar-notice-promotion-v1" and not report.get("health"):
                    legacy_unverified.append(path)
                else:
                    failures.append(path)
        except (OSError, json.JSONDecodeError):
            failures.append(path)
    result = {
        "schema": "boursnegar-promotion-report-audit-v1",
        "reports": len(paths),
        "schemas": dict(schemas),
        "invariant_failures": len(failures),
        "legacy_unverified": len(legacy_unverified),
        "legacy_unverified_paths": legacy_unverified,
        "failure_paths": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
