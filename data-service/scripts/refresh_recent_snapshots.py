#!/usr/bin/env python3
"""Refresh only symbols with newly retrieved Codal evidence.

The existing refresh script remains checkpointed and evidence-only. This
wrapper keeps the daily job cheap by selecting symbols touched recently.
"""
from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import text

from app.database import engine


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=int, default=48)
    parser.add_argument("--base-url", default="http://127.0.0.1:8001")
    parser.add_argument("--workdir", default="/var/lib/boursnegar/snapshot-refresh")
    args = parser.parse_args()
    since = datetime.now(timezone.utc) - timedelta(hours=max(1, args.hours))
    with engine.connect() as connection:
        rows = connection.execute(text("""
          SELECT DISTINCT sa.symbol
          FROM symbol_aliases sa
          JOIN instruments i ON i.id=sa.instrument_id AND i.active
          JOIN disclosures d ON d.instrument_id=i.id
          JOIN disclosure_versions v ON v.disclosure_id=d.id
          WHERE sa.valid_to IS NULL AND v.retrieved_at>=:since
          ORDER BY sa.symbol
        """), {"since": since}).scalars().all()
    if not rows:
        print({"status": "no_recent_evidence", "since": since.isoformat()})
        return
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    symbols = workdir / "symbols.txt"
    checkpoint = workdir / "checkpoint.json"
    symbols.write_text("\n".join(rows) + "\n", encoding="utf-8")
    if not checkpoint.exists():
        checkpoint.write_text('{"done":{},"errors":{}}\n', encoding="utf-8")
    command = [
        "python3", "scripts/refresh_internal_snapshots.py",
        "--symbols-file", str(symbols), "--checkpoint", str(checkpoint),
        "--base-url", args.base_url, "--report-mode", "latest_codal",
        "--pause", "0.15", "--timeout", "45",
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
