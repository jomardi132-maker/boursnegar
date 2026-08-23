#!/usr/bin/env python3
"""Register quarantined public Rahavard reports in the raw staging table."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlalchemy import text

from app.database import engine


def run(manifest: Path) -> dict:
    rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    saved = 0
    with engine.begin() as connection:
        for row in rows:
            if row.get("status") != "QUARANTINED":
                continue
            report = row["report"]
            connection.execute(text("""
              INSERT INTO rahavard_public_reports(
                report_id,image_id,symbol,title,subtitle,report_date,fiscal_year,
                pdf_url,checksum_sha256,storage_path,text_path,text_status,
                source_status,raw_json,collected_at,updated_at
              ) VALUES(
                :report_id,:image_id,:symbol,:title,CAST(:subtitle AS jsonb),
                :report_date,:fiscal_year,:pdf_url,:checksum,:storage_path,
                :text_path,:text_status,:source_status,CAST(:raw_json AS jsonb),
                COALESCE(CAST(:collected_at AS timestamptz),now()),now()
              ) ON CONFLICT(report_id) DO UPDATE SET
                image_id=excluded.image_id,symbol=excluded.symbol,title=excluded.title,
                subtitle=excluded.subtitle,report_date=excluded.report_date,
                fiscal_year=excluded.fiscal_year,pdf_url=excluded.pdf_url,
                checksum_sha256=excluded.checksum_sha256,storage_path=excluded.storage_path,
                text_path=excluded.text_path,text_status=excluded.text_status,
                source_status=excluded.source_status,raw_json=excluded.raw_json,
                collected_at=excluded.collected_at,updated_at=now()
            """), {
                "report_id": str(report["id"]), "image_id": str(report.get("image_id") or ""),
                "symbol": report.get("trade_symbol"), "title": report.get("title"),
                "subtitle": json.dumps(report.get("subtitle") or [], ensure_ascii=False),
                "report_date": report.get("date"), "fiscal_year": report.get("fiscal_year"),
                "pdf_url": row["pdf_url"], "checksum": row["checksum_sha256"],
                "storage_path": row["pdf_path"], "text_path": row.get("text_path"),
                "text_status": row.get("text_status") or "PENDING_TEXT_EXTRACTION",
                "source_status": row.get("status"), "raw_json": json.dumps(row, ensure_ascii=False),
                "collected_at": row.get("collected_at"),
            })
            saved += 1
    return {"manifest_rows": len(rows), "staged": saved}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    args = parser.parse_args()
    print(json.dumps(run(Path(args.manifest)), ensure_ascii=False))
