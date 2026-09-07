#!/usr/bin/env python3
"""Run one bounded, resumable local Codal collection window per day."""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / "data-service" / "venv" / "bin" / "python"
CANONICAL_ARTIFACTS = ROOT / "data-service" / "artifacts"
STATE = CANONICAL_ARTIFACTS / "daily-codal-monitor.json"
LOCK = CANONICAL_ARTIFACTS / "daily-codal-monitor.lock"


def today_jalali() -> str:
    import jdatetime
    d = jdatetime.date.today()
    return f"{d.year:04d}/{d.month:02d}/{d.day:02d}"


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"cursor": 0, "last_run": None, "last_symbols": []}
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def cleanup_browser_profile(output: Path) -> None:
    """Remove only the disposable Chrome profile; artifacts remain intact."""
    profile = output / ".chrome-profile"
    if profile.exists():
        shutil.rmtree(profile, ignore_errors=True)


def discover_local(path: Path) -> list[str]:
    """Use the local operator registry; Production is never the symbol source."""
    with sqlite3.connect(path) as connection:
        rows = connection.execute(
            "SELECT symbol FROM symbols WHERE symbol IS NOT NULL AND trim(symbol) <> '' ORDER BY symbol"
        ).fetchall()
    return [row[0] for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ssh-target", default="boursnegar")
    parser.add_argument("--local-db", default=str(CANONICAL_ARTIFACTS / "local-ingestion.sqlite3"))
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--state", default=str(STATE))
    parser.add_argument("--out", default=str(CANONICAL_ARTIFACTS / "daily-codal"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="rerun the current Jalali date explicitly")
    parser.add_argument("--no-import", action="store_true", help="collect and normalize locally without remote import")
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")

    lock_path = Path(args.state).with_suffix(".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps({"status": "already-running"}, ensure_ascii=False))
            return 0
        return run_once(args)


def run_once(args) -> int:
    state_path = Path(args.state)
    state = load_state(state_path)
    today = today_jalali()
    if state.get("last_date") == today and not args.force:
        print(json.dumps({"status": "already-ran-today", "date": today}, ensure_ascii=False))
        return 0
    local_db = Path(args.local_db)
    if not local_db.exists():
        print(json.dumps({"status": "local-registry-missing", "path": str(local_db)}, ensure_ascii=False))
        return 2
    symbols = discover_local(local_db)
    if not symbols:
        print(json.dumps({"status": "no-active-symbols"}, ensure_ascii=False))
        return 0
    start = int(state.get("cursor", 0)) % len(symbols)
    batch = [symbols[(start + i) % len(symbols)] for i in range(min(args.batch_size, len(symbols)))]
    day_output = Path(args.out) / today.replace("/", "")
    output = day_output if state.get("last_date") != today else day_output / f"cursor-{start:04d}"
    command = [str(PYTHON), "data-service/scripts/daily_local_ingestion.py"]
    for symbol in batch:
        command += ["--symbol", symbol]
    # Daily monitoring is notice-only.  The Codalpy adapter intentionally
    # fetches historical statement ranges, so using it here would turn a
    # daily check into an accidental backfill. Historical recovery remains a
    # separate, explicitly targeted workflow.
    command += [
        "--from-jalali", today, "--to-jalali", today,
        "--out", str(output), "--ssh-target", args.ssh_target,
        "--profile", str(output / ".chrome-profile"),
        "--html-only",
    ]
    if not args.no_import:
        command.append("--import")
    print(json.dumps({"status": "planned", "date": today, "symbols": batch, "output": str(output)}, ensure_ascii=False))
    if args.dry_run:
        return 0
    result = subprocess.run(command, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "data-service")})
    if result.returncode != 0:
        return result.returncode
    # Keep the public analytical snapshot in the same successful transaction
    # boundary as the evidence import; never advance the cursor on refresh failure.
    refresh = subprocess.run([
        "ssh", args.ssh_target, "systemctl", "start", "--wait",
        "boursnegar-snapshot-refresh.service",
    ], cwd=ROOT)
    if refresh.returncode != 0:
        print(json.dumps({"status": "snapshot-refresh-failed", "returncode": refresh.returncode}, ensure_ascii=False))
        return refresh.returncode
    cleanup_browser_profile(output)
    state.update({"cursor": (start + len(batch)) % len(symbols), "last_date": today, "last_run": datetime.now(timezone.utc).isoformat(), "last_symbols": batch})
    atomic_write(state_path, state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
