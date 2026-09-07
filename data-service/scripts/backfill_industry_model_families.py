#!/usr/bin/env python3
"""Backfill only model families that are deterministically mapped from industry titles."""
from __future__ import annotations

import argparse

from sqlalchemy import text

from app.database import engine
from app.ingestion.market_history import model_family


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    with engine.begin() as connection:
        rows = connection.execute(
            text("SELECT id, title_fa, model_family FROM industries ORDER BY id")
        ).mappings().all()
        changes = []
        for row in rows:
            family = model_family(row["title_fa"])
            current = row["model_family"] or "unclassified"
            if family != "unclassified" and family != current:
                changes.append({"id": row["id"], "family": family})
        if not args.dry_run and changes:
            connection.execute(
                text("UPDATE industries SET model_family=:family WHERE id=:id"), changes
            )
    print({"dry_run": args.dry_run, "industries": len(rows), "updated": len(changes)})


if __name__ == "__main__":
    main()
