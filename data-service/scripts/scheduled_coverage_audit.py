#!/usr/bin/env python3
"""Run the authoritative Production coverage audit and retain local evidence."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY = ROOT / "data-service" / "venv" / "bin" / "python"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True, **kwargs)


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "data-service" / "artifacts" / f"coverage-cycle-{stamp}"
    out.mkdir(parents=True, exist_ok=True)
    remote = f"/tmp/boursnegar-scheduled-audit-{stamp}"
    target = os.environ.get("BOURSNEGAR_SSH_TARGET", "boursnegar")
    try:
        run(["ssh", target, f"mkdir -p {remote}"])
        run(["scp", str(ROOT / "data-service/scripts/analysis_coverage_audit.py"), f"{target}:{remote}/"])
        run(["ssh", target, f"PYTHONPATH=/var/www/boursnegar-data-current /var/www/boursnegar-runtimes/data-venv/bin/python3 {remote}/analysis_coverage_audit.py --output {remote}/coverage.json --symbols-output {remote}/coverage-symbols.csv"])
        for name in ("coverage.json", "coverage-symbols.csv"):
            run(["scp", f"{target}:{remote}/{name}", str(out / name)])
        health = run(["ssh", target, "curl", "-fsS", "http://127.0.0.1:8001/healthz"])
        ready = run(["ssh", target, "curl", "-fsS", "http://127.0.0.1:8001/readyz"])
        runtime = {"health": health.stdout.strip(), "ready": ready.stdout.strip()}
        (out / "runtime.json").write_text(json.dumps(runtime, ensure_ascii=False, indent=2), encoding="utf-8")
        coverage = json.loads((out / "coverage.json").read_text(encoding="utf-8"))
        report = {"schema": "boursnegar-scheduled-coverage-v1", "status": "success", "generated_at": datetime.now(timezone.utc).isoformat(), "output": str(out), "runtime": runtime, "coverage_summary": {"generatedAt": coverage.get("generatedAt"), "global": coverage.get("global"), "symbolCoverageTiers": coverage.get("symbolCoverageTiers"), "latestDecisions": coverage.get("latestDecisions")}}
    except subprocess.CalledProcessError as exc:
        report = {"schema": "boursnegar-scheduled-coverage-v1", "status": "failed", "generated_at": datetime.now(timezone.utc).isoformat(), "output": str(out), "stderr": exc.stderr[-4000:] if exc.stderr else ""}
        (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False)); return exc.returncode or 1
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
