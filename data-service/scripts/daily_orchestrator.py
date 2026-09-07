#!/usr/bin/env python3
"""Safe, checkpointed daily coordinator for Boursnegar.

This is an operator-facing wrapper around the existing daily supervisor.  It
does not fetch Codal directly, does not promote evidence, and does not write
Production.  Those actions remain explicit later workflow stages.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYTHON = Path(sys.executable)
SCHEMA = "boursnegar-daily-orchestrator-v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def validate_artifacts(root: Path, *, latest_only: bool = False) -> dict:
    issues: list[str] = []
    # Quarantined browser profiles and explicitly isolated incomplete downloads
    # are historical evidence, not promotion candidates.  Including them in a
    # workspace-wide gate made every later run BLOCKED forever and encouraged
    # expensive rechecks of stale files.
    def relevant(path: Path) -> bool:
        return not any(part.startswith('.quarantine-chrome-') or part == 'incomplete-downloads'
                       for part in path.parts)
    manifests = [p for p in root.rglob("manifest.json") if relevant(p)] if root.exists() else []
    if latest_only and manifests:
        cursor_dirs = {p.parent.parent for p in manifests if p.parent.parent.name.startswith("cursor-")}
        if cursor_dirs:
            # Directory mtimes are not reliable across copied/restored artifact
            # trees.  Use the newest manifest within each cursor instead.
            newest = max(cursor_dirs, key=lambda p: (
                max((manifest.stat().st_mtime for manifest in manifests if p in manifest.parents), default=0),
                p.name,
            ))
            manifests = [p for p in manifests if newest in p.parents]
    for partial in (root.rglob("*.crdownload") if root.exists() else []):
        if not relevant(partial):
            continue
        issues.append(f"incomplete-download:{partial}")
    for manifest_path in manifests:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(f"invalid-manifest:{manifest_path}:{exc}")
            continue
        for error in manifest.get("errors", []) or []:
            issues.append(f"manifest-error:{manifest_path}:{error}")
        for item in manifest.get("files", []) or []:
            relative = item.get("path")
            expected = item.get("sha256")
            if not relative or not expected:
                issues.append(f"incomplete-file-entry:{manifest_path}")
                continue
            file_path = manifest_path.parent / relative
            if not file_path.is_file():
                issues.append(f"missing-file:{file_path}")
                continue
            digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
            if digest != expected:
                issues.append(f"checksum-mismatch:{file_path}")
    return {"root": str(root), "manifests": len(manifests), "issues": issues,
            "valid": not issues}


def classify(returncode: int, supervisor_returncode: int, plan_returncode: int, *, no_notices: bool = False, artifact_valid: bool = True) -> str:
    if not artifact_valid:
        return "BLOCKED"
    if no_notices and supervisor_returncode == 0:
        return "REVIEW"
    if returncode == 0 and supervisor_returncode == 0 and plan_returncode == 0:
        return "PASS"
    if supervisor_returncode == 2:
        return "REVIEW"
    return "BLOCKED"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="validate the plan without running the monitor")
    parser.add_argument("--latest-only", action="store_true", help="validate only the newest cursor under the artifact root")
    parser.add_argument("--local-db", default=str(ROOT / "data-service/artifacts/local-ingestion.sqlite3"))
    parser.add_argument("--run-dir", default=str(ROOT / "data-service/artifacts/daily-orchestrator"))
    parser.add_argument("--artifact-root", default=str(ROOT / "data-service/artifacts/daily-codal"))
    parser.add_argument("--allow-production-import", action="store_true",
                        help="explicitly allow the supervisor's remote import stage")
    parser.add_argument("--lock-file", default=str(ROOT / "data-service/artifacts/.daily-orchestrator.lock"))
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    if args.allow_production_import and not args.dry_run:
        # This wrapper has no backup gate.  Do not let a convenience flag
        # bypass promote_evidence/auto_local_to_production, which take the
        # rollback dump, verify checksums, replay idempotently, and gate ready.
        raise SystemExit("refusing production import: use the backup-gated promotion workflow")

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    lock_path = Path(args.lock_file)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps({"schema": SCHEMA, "status": "ALREADY_RUNNING"}, ensure_ascii=False))
            return 3

        started = utc_now()
        supervisor = [str(PYTHON), str(ROOT / "data-service/scripts/boursnegar_daily_supervisor.py"),
                      "--batch-size", str(args.batch_size), "--local-db", args.local_db,
                      "--report-dir", str(run_dir / "supervisor")]
        if args.force:
            supervisor.append("--force")
        plan = {
            "schema": SCHEMA,
            "started_at": started,
            "mode": "dry-run" if args.dry_run else "local-supervisor",
            "production_write": False,
            "promotion": False,
            "provenance_policy": "official-evidence-only-no-fabrication",
            "commands": [supervisor],
        }
        supervisor_result = subprocess.CompletedProcess(supervisor, 0, "dry-run: supervisor not executed\n", "")
        plan_returncode = 0
        if not args.dry_run and args.allow_production_import:
            supervisor_result = subprocess.run(supervisor, cwd=ROOT, capture_output=True, text=True)
        elif not args.dry_run:
            supervisor.append("--no-import")
            supervisor_result = subprocess.run(supervisor, cwd=ROOT, capture_output=True, text=True)
        plan["supervisor"] = {
            "returncode": supervisor_result.returncode,
            "stdout": supervisor_result.stdout,
            "stderr": supervisor_result.stderr,
        }
        artifacts = validate_artifacts(Path(args.artifact_root), latest_only=args.latest_only)
        plan["artifact_validation"] = artifacts
        no_notices = "NO_NOTICES" in supervisor_result.stdout
        status = classify(0, supervisor_result.returncode, plan_returncode,
                          no_notices=no_notices, artifact_valid=artifacts["valid"])
        plan.update({"finished_at": utc_now(), "status": status,
                     "gates": {"no_notices_observed": no_notices,
                               "absence_of_notice_proven": False if no_notices else None},
                     "next_action": "review artifacts and gates" if status != "PASS" else "operator review before any promotion"})
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        report = run_dir / f"{stamp}.json"
        atomic_json(report, plan)
        atomic_json(run_dir / "latest.json", plan)
        print(json.dumps({"schema": SCHEMA, "status": status, "report": str(report),
                          "production_write": bool(args.allow_production_import and not args.dry_run)}, ensure_ascii=False))
        return 0 if status == "PASS" else (2 if status == "REVIEW" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
