#!/usr/bin/env python3
"""Download and parse cached Codal financial documents without using BrsApi."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import uuid
from pathlib import Path

from sqlalchemy import text

from app.database import engine
from app.ingestion.market_history import jalali_to_gregorian
from app.services.codal_excel_parser import (
    CodalExcelParseError,
    extract_period_end_jalali,
    fetch_and_parse,
    download_codal_excel,
)

PERIOD_RE = re.compile(r"(?P<months>۳|۶|۹|۱۲|3|6|9|12)\s*ماهه")
FACT_KEYS = ("revenue", "cogs", "gross_profit", "operating_profit", "net_profit",
             "eps_basic", "total_assets", "total_liabilities", "total_equity",
             "operating_cash_flow")


def period_months(title: str) -> int | None:
    normalized = str(title or "").translate(str.maketrans("۱۲۳۴۵۶۷۸۹۰", "1234567890"))
    if "سال مالی" in normalized or "۱۲ ماهه" in normalized or "12 ماهه" in normalized:
        return 12
    match = PERIOD_RE.search(normalized)
    return int(match.group("months")) if match else None


def detect_unit(content: bytes) -> str | None:
    text_content = content[:2_000_000].decode("utf-8", errors="ignore")
    if "میلیارد ریال" in text_content:
        return "IRR_billion"
    if "میلیون ریال" in text_content:
        return "IRR_million"
    if "ریال" in text_content:
        return "IRR"
    return None


def _jalali_to_date(value: str):
    year, month, day = (int(part) for part in value.split("/"))
    return jalali_to_gregorian(year, month, day)


def _current_version(connection, disclosure_id):
    return connection.execute(text("""
      SELECT dv.id,d.source_disclosure_id,d.title,d.published_date_jalali,d.is_audited,d.scope,
             (dv.metadata->>'excel_url') AS excel_url
      FROM disclosure_versions dv JOIN disclosures d ON d.id=dv.disclosure_id
      WHERE dv.disclosure_id=:id AND dv.is_current
    """), {"id": disclosure_id}).mappings().first()


def ingest(limit: int, root: Path) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    with engine.begin() as connection:
        rows = list(connection.execute(text("""
          SELECT d.id AS disclosure_id,d.issuer_id,d.source_disclosure_id,d.title,d.is_audited,d.scope,
                 dv.id AS version_id,(dv.metadata->>'excel_url') AS excel_url
          FROM disclosures d JOIN disclosure_versions dv ON dv.disclosure_id=d.id AND dv.is_current
          -- Permanent parser failures (for example Codal error pages with no
          -- tables) are audited but must not monopolize every retry batch.
          -- Network/download failures remain retryable as FAILED.
          WHERE NOT EXISTS (
                  SELECT 1 FROM raw_documents rd
                  WHERE rd.disclosure_version_id=dv.id
                    AND rd.parser_status IN ('PARSED', 'FAILED_PERMANENT')
                )
            AND (dv.metadata->>'excel_url') IS NOT NULL
            AND d.published_date_jalali >= '1404/01/01'
            AND d.title ~ '(صورت|مالی|ترازنامه|سود|زیان)'
            AND d.title !~ 'فعالیت ماهانه'
          ORDER BY d.published_date_jalali,d.source_disclosure_id
          LIMIT :limit
        """), {"limit": limit}).mappings())
    processed = saved = skipped = failed = 0
    for row in rows:
        try:
            content = download_codal_excel(row["excel_url"])
            checksum = hashlib.sha256(content).hexdigest()
            unit = detect_unit(content)
            file_path = root / f"{checksum}.html"
            if not file_path.exists():
                file_path.write_bytes(content)
            parsed = fetch_and_parse(row["excel_url"])
            end_jalali = extract_period_end_jalali(row["title"])
            months = period_months(row["title"])
            if not end_jalali or not months:
                marker = hashlib.sha256(f"skipped:{row['version_id']}".encode()).hexdigest()
                with engine.begin() as connection:
                    connection.execute(text("""
                      INSERT INTO raw_documents(disclosure_version_id,source_url,storage_key,checksum_sha256,mime_type,byte_size,retrieved_at,parser_status)
                      VALUES(:version,:url,:key,:checksum,'text/plain',0,now(),'FAILED_PERMANENT')
                      ON CONFLICT(disclosure_version_id,checksum_sha256) DO UPDATE SET
                        parser_status='FAILED_PERMANENT',retrieved_at=now()
                    """), {"version": row["version_id"], "url": row["excel_url"],
                            "key": f"skipped/{row['version_id']}", "checksum": marker})
                skipped += 1
                continue
            end_date = _jalali_to_date(end_jalali)
            start_date = end_date
            period_id = str(uuid.uuid4())
            with engine.begin() as connection:
                connection.execute(text("""
                  INSERT INTO raw_documents(disclosure_version_id,source_url,storage_key,checksum_sha256,mime_type,byte_size,retrieved_at,parser_status)
                  VALUES(:version,:url,:key,:checksum,'text/html',:size,now(),'PARSED')
                  ON CONFLICT(disclosure_version_id,checksum_sha256) DO NOTHING
                """), {"version": row["version_id"], "url": row["excel_url"], "key": str(file_path),
                       "checksum": checksum, "size": len(content)})
                period_id = connection.execute(text("""
                  INSERT INTO financial_periods(issuer_id,period_type,start_date,end_date,start_date_jalali,end_date_jalali,length_months,fiscal_year,audited,scope,disclosure_version_id)
                  VALUES(:issuer,'interim',:start,:end,:start_j,:end_j,:months,:year,:audited,:scope,:version)
                  ON CONFLICT(issuer_id,end_date,length_months,audited,scope,disclosure_version_id)
                  DO UPDATE SET end_date=excluded.end_date RETURNING id
                """), {"issuer": row["issuer_id"], "start": start_date, "end": end_date,
                       "start_j": end_jalali, "end_j": end_jalali, "months": months,
                       "year": int(end_jalali[:4]), "audited": bool(row["is_audited"]),
                       "scope": row["scope"] or "unknown", "version": row["version_id"]}).scalar_one()
                parser_id = connection.execute(text("""
                  INSERT INTO parser_versions(parser_name,version,document_type,active)
                  VALUES('codal_excel_parser','v1','html_excel',true)
                  ON CONFLICT(parser_name,version,document_type) DO UPDATE SET active=true RETURNING id
                """)).scalar_one()
                for key in FACT_KEYS:
                    value = parsed["metrics"].get(key)
                    if value is None:
                        continue
                    connection.execute(text("""
                      INSERT INTO financial_facts(issuer_id,period_id,fact_key,raw_value,normalized_value,raw_unit,normalized_unit,unit_multiplier,parser_version_id,quality_status)
                      VALUES(:issuer,:period,:key,:value,:value,:unit,:unit,1,:parser,:quality)
                      ON CONFLICT(period_id,fact_key,parser_version_id) DO UPDATE SET raw_value=excluded.raw_value,normalized_value=excluded.normalized_value,quality_status=excluded.quality_status
                    """), {"issuer": row["issuer_id"], "period": period_id, "key": key, "value": value,
                           "unit": unit or "UNKNOWN", "parser": parser_id,
                           "quality": "VALID" if unit else "UNIT_UNKNOWN"})
            processed += 1
            saved += len(parsed["found_items"])
        except CodalExcelParseError as exc:
            # Permanent format failures (for example a Codal error page with
            # no tables) must not occupy every hourly retry forever. Keep a
            # durable audit record while allowing network/download failures
            # to be retried on the next run.
            if 'content' in locals() and content:
                with engine.begin() as connection:
                    connection.execute(text("""
                      INSERT INTO raw_documents(disclosure_version_id,source_url,storage_key,checksum_sha256,mime_type,byte_size,retrieved_at,parser_status)
                      VALUES(:version,:url,:key,:checksum,'text/html',:size,now(),'FAILED_PERMANENT')
                      ON CONFLICT(disclosure_version_id,checksum_sha256) DO UPDATE SET
                        parser_status='FAILED_PERMANENT',retrieved_at=now()
                    """), {"version": row["version_id"], "url": row["excel_url"],
                           "key": str(root / f"{row['version_id']}-{hashlib.sha256(content).hexdigest()}.failed.html"),
                           "checksum": hashlib.sha256(content).hexdigest(), "size": len(content)})
            failed += 1
            print(json.dumps({"disclosure": row["source_disclosure_id"], "error": str(exc)[:300], "permanent": True}, ensure_ascii=False), flush=True)
        except Exception as exc:
            failed += 1
            print(json.dumps({"disclosure": row["source_disclosure_id"], "error": str(exc)[:300]}, ensure_ascii=False), flush=True)
    return {"candidates": len(rows), "processed": processed, "facts": saved, "skipped": skipped, "failed": failed}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--root", default=os.getenv("CODAL_DOCUMENT_ROOT", "/var/lib/boursnegar/codal"))
    args = parser.parse_args()
    print(json.dumps(ingest(args.limit, Path(args.root)), ensure_ascii=False))
