#!/usr/bin/env python3
"""Build a minimal, auditable NAV evidence set from existing browser artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

TARGETS = {
    "1516095": "آتیمس",
    "1457062": "آتیه ملت",
    "1572614": "امتیاز",
    "1573834": "امین شهر",  # correction supersedes 1573540 for the same period
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, action="append", required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    rows = []
    for input_path in a.input:
        for line in input_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("fact_key") != "nav_per_share":
                continue
            tracing = str(row.get("tracing_no", ""))
            document = str(row.get("payload", {}).get("document", ""))
            if tracing in TARGETS and document.endswith("-excel.xls") and row.get("unit") == "IRR":
                rows.append(row)
    rows.sort(key=lambda r: str(r.get("tracing_no")))
    seen = set()
    unique = []
    for row in rows:
        key = (row.get("symbol"), row.get("period_end_jalali"), row.get("tracing_no"))
        if key not in seen:
            seen.add(key)
            unique.append(row)
    if {str(r.get("tracing_no")) for r in unique} != set(TARGETS):
        raise SystemExit("refusing: curated NAV set is incomplete")
    a.output.mkdir(parents=True, exist_ok=True)
    data = a.output / "normalized.jsonl"
    data.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in unique) + "\n", encoding="utf-8")
    manifest = {
        "schema": "boursnegar-codalpy-jsonl-v1",
        "source": "browser/codal.ir",
        "selection": "verified NAV queue; correction 1573834 supersedes 1573540",
        "files": [{"path": data.name, "symbol": "*", "records": len(unique), "sha256": hashlib.sha256(data.read_bytes()).hexdigest()}],
        "source_actions": [r["source_action_id"] for r in unique],
        "source_documents": [
            {"document": r["payload"]["document"], "sha256": r["payload"]["document_sha256"], "detail_url": r["payload"]["detail_url"]}
            for r in unique
        ],
    }
    (a.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "records": len(unique), "actions": manifest["source_actions"], "manifest": str(a.output / "manifest.json")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
