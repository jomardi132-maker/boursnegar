#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import uuid
from datetime import datetime, timezone

from sqlalchemy import text

from app.config import CODAL_RATE_LIMIT_SECONDS
from app.database import engine
from app.ingestion.market_history import gregorian_to_jalali, normalize_persian
from app.services.codal_service import fetch_letters_page


SOURCE = "codal-search-api"
PIPELINE = "codal-metadata-1404-v1"
PILOT_FAMILIES = ("metals", "petrochemical", "refinery", "bank", "cement")
YEAR_RE = re.compile(r"14(?:04|05)")
DATE_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")


def _url(value: str | None, host: str) -> str | None:
    if not value:
        return None
    return f"{host}{value}" if value.startswith("/") else value


def _is_in_scope(letter: dict) -> bool:
    searchable = " ".join(
        str(letter.get(key) or "") for key in ("Title", "PublishDateTime")
    ).translate(DATE_DIGITS)
    return bool(YEAR_RE.search(searchable))


def _fetch_with_backoff(symbol: str, page: int) -> dict:
    for attempt in range(5):
        try:
            return fetch_letters_page(symbol, page)
        except Exception as exc:
            if "429" not in str(exc) or attempt == 4:
                raise
            wait_seconds = 15 * (attempt + 1)
            print(json.dumps({"symbol": symbol, "page": page, "retryIn": wait_seconds}), flush=True)
            time.sleep(wait_seconds)
    raise RuntimeError("unreachable")


def _fetch_global_with_backoff(page: int, from_date: str, to_date: str) -> dict:
    for attempt in range(6):
        try:
            return fetch_letters_page(None, page, from_date, to_date)
        except Exception as exc:
            if "429" not in str(exc) or attempt == 5:
                raise
            wait_seconds = 30 * (attempt + 1)
            print(json.dumps({"page": page, "retryIn": wait_seconds}), flush=True)
            time.sleep(wait_seconds)
    raise RuntimeError("unreachable")


def _symbols(connection) -> list[dict]:
    return list(connection.execute(text("""
      SELECT DISTINCT sa.symbol,i.id AS instrument_id,ir.id AS issuer_id,ir.legal_name
      FROM symbol_aliases sa
      JOIN instruments i ON i.id=sa.instrument_id
      JOIN issuers ir ON ir.id=i.issuer_id
      JOIN industries ind ON ind.id=ir.industry_id
      WHERE sa.valid_to IS NULL AND i.active AND ind.model_family = ANY(:families)
        AND sa.symbol !~ '[0-9۰-۹]$'
      ORDER BY sa.symbol
    """), {"families": list(PILOT_FAMILIES)}).mappings())


def _save_letter(connection, symbol: dict, letter: dict) -> bool:
    tracing_no = str(letter.get("TracingNo") or "").strip()
    if not tracing_no:
        return False
    title = str(letter.get("Title") or "بدون عنوان")
    published = letter.get("PublishDateTime")
    audited = "حسابرسی شده" in title and "حسابرسی نشده" not in title
    scope = "consolidated" if "تلفیقی" in title else "separate"
    metadata = dict(letter)
    metadata["symbol"] = symbol["symbol"]
    metadata["excel_url"] = _url(letter.get("ExcelUrl"), "https://excel.codal.ir")
    metadata["detail_url"] = _url(letter.get("Url"), "https://codal.ir")
    encoded = json.dumps(metadata, ensure_ascii=False, sort_keys=True, default=str)
    checksum = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    disclosure_id = connection.execute(text("""
      INSERT INTO disclosures(
        issuer_id,instrument_id,source,source_disclosure_id,letter_code,
        disclosure_type,title,published_at,published_date_jalali,is_audited,scope
      ) VALUES(
        :issuer_id,:instrument_id,:source,:tracing_no,:letter_code,'codal_letter',
        :title,NULL,:published,:audited,:scope
      ) ON CONFLICT(source,source_disclosure_id) DO UPDATE SET
        title=excluded.title,letter_code=excluded.letter_code,
        published_date_jalali=excluded.published_date_jalali,
        is_audited=excluded.is_audited,scope=excluded.scope
      RETURNING id
    """), {
        **symbol, "source": SOURCE, "tracing_no": tracing_no,
        "letter_code": letter.get("LetterCode"), "title": title,
        "published": published, "audited": audited, "scope": scope,
    }).scalar_one()
    exists = connection.execute(text("""
      SELECT 1 FROM disclosure_versions
      WHERE disclosure_id=:disclosure_id AND content_checksum=:checksum
    """), {"disclosure_id": disclosure_id, "checksum": checksum}).first()
    if exists:
        return False
    connection.execute(text("""
      UPDATE disclosure_versions SET is_current=false WHERE disclosure_id=:disclosure_id
    """), {"disclosure_id": disclosure_id})
    connection.execute(text("""
      INSERT INTO disclosure_versions(
        disclosure_id,version_number,source_version_id,retrieved_at,
        content_checksum,metadata,is_current
      ) SELECT :disclosure_id,COALESCE(MAX(version_number),0)+1,:source_version_id,
        now(),:checksum,CAST(:metadata AS jsonb),true
      FROM disclosure_versions WHERE disclosure_id=:disclosure_id
    """), {
        "disclosure_id": disclosure_id, "source_version_id": tracing_no,
        "checksum": checksum, "metadata": encoded,
    })
    return True


def run(max_pages: int, resume: bool) -> dict:
    run_id = str(uuid.uuid4())
    with engine.begin() as connection:
        connection.execute(text("""
          INSERT INTO ingestion_runs(id,pipeline,source,partition_key,status)
          VALUES(:id,:pipeline,:source,'pilot-industries','RUNNING')
        """), {"id": run_id, "pipeline": PIPELINE, "source": SOURCE})
        symbols = _symbols(connection)
        done = set()
        if resume:
            done = {row[0] for row in connection.execute(text("""
              SELECT partition_key FROM ingestion_checkpoints
              WHERE source=:source AND pipeline=:pipeline
                AND (cursor->>'completed')::boolean=true
                AND COALESCE((cursor->>'letters')::integer,0)>0
            """), {"source": SOURCE, "pipeline": PIPELINE})}
    saved = failures = processed = 0
    for item in symbols:
        symbol = item["symbol"]
        if symbol in done:
            continue
        try:
            letters = []
            for page in range(1, max_pages + 1):
                payload = _fetch_with_backoff(symbol, page)
                page_letters = payload.get("Letters") or []
                letters.extend(letter for letter in page_letters if _is_in_scope(letter))
                if not page_letters or page >= int(payload.get("Page") or page):
                    break
                # Once a full page is older than 1404, later pages are older too.
                if page_letters and not any(_is_in_scope(letter) for letter in page_letters):
                    break
                time.sleep(CODAL_RATE_LIMIT_SECONDS)
            with engine.begin() as connection:
                for letter in letters:
                    saved += int(_save_letter(connection, item, letter))
                connection.execute(text("""
                  INSERT INTO ingestion_checkpoints(source,pipeline,partition_key,cursor,watermark_at)
                  VALUES(:source,:pipeline,:symbol,CAST(:cursor AS jsonb),now())
                  ON CONFLICT(source,pipeline,partition_key) DO UPDATE SET
                    cursor=excluded.cursor,watermark_at=excluded.watermark_at,updated_at=now()
                """), {"source": SOURCE, "pipeline": PIPELINE, "symbol": symbol,
                         "cursor": json.dumps({"completed": True, "letters": len(letters)})})
            processed += 1
            print(json.dumps({"symbol": symbol, "letters": len(letters), "saved": saved}, ensure_ascii=False), flush=True)
            time.sleep(CODAL_RATE_LIMIT_SECONDS)
        except Exception as exc:
            failures += 1
            with engine.begin() as connection:
                connection.execute(text("""
                  INSERT INTO ingestion_dead_letters(ingestion_run_id,source_reference,stage,error_code,payload_reference)
                  VALUES(:run_id,:symbol,'discover','CODAL_FETCH_FAILED',:error)
                """), {"run_id": run_id, "symbol": symbol, "error": str(exc)[:1000]})
            print(json.dumps({"symbol": symbol, "error": str(exc)}, ensure_ascii=False), flush=True)
            time.sleep(CODAL_RATE_LIMIT_SECONDS)
    result = {"runId": run_id, "symbols": processed, "saved": saved, "failures": failures}
    with engine.begin() as connection:
        connection.execute(text("""
          UPDATE ingestion_runs SET status=:status,finished_at=now(),metrics=CAST(:metrics AS jsonb),
            error_summary=:error WHERE id=:id
        """), {"id": run_id, "status": "PASSED" if failures == 0 else "FAILED",
                 "metrics": json.dumps(result), "error": None if failures == 0 else f"{failures} symbols failed"})
    return result


def run_global(resume: bool) -> dict:
    """Fetch each dated Codal result page once instead of querying every symbol."""
    run_id = str(uuid.uuid4())
    jy, jm, jd = gregorian_to_jalali(datetime.now().date())
    from_date = "1404/01/01"
    to_date = f"{jy:04d}/{jm:02d}/{jd:02d}"
    with engine.begin() as connection:
        connection.execute(text("""
          UPDATE ingestion_runs SET status='CANCELLED',finished_at=now(),
            error_summary='superseded by global-page ingestion'
          WHERE pipeline=:pipeline AND status='RUNNING'
        """), {"pipeline": PIPELINE})
        connection.execute(text("""
          INSERT INTO ingestion_runs(id,pipeline,source,partition_key,status,watermark)
          VALUES(:id,:pipeline,:source,'global-pages','RUNNING',CAST(:watermark AS jsonb))
        """), {"id": run_id, "pipeline": PIPELINE, "source": SOURCE,
                 "watermark": json.dumps({"from": from_date, "to": to_date})})
        catalog = list(connection.execute(text("""
          SELECT sa.symbol,i.id AS instrument_id,ir.id AS issuer_id,ir.legal_name
          FROM symbol_aliases sa JOIN instruments i ON i.id=sa.instrument_id
          JOIN issuers ir ON ir.id=i.issuer_id
          WHERE sa.valid_to IS NULL AND i.active
        """)).mappings())
        symbols = {normalize_persian(row["symbol"]): dict(row) for row in catalog}
        next_page = 1
        if resume:
            cursor = connection.execute(text("""
              SELECT cursor FROM ingestion_checkpoints
              WHERE source=:source AND pipeline=:pipeline AND partition_key='global-pages'
            """), {"source": SOURCE, "pipeline": PIPELINE}).scalar()
            if cursor and cursor.get("to") == to_date:
                next_page = max(1, int(cursor.get("nextPage") or 1))

    saved = matched = unmatched = 0
    total_pages = next_page
    try:
        while next_page <= total_pages:
            payload = _fetch_global_with_backoff(next_page, from_date, to_date)
            total_pages = int(payload.get("Page") or 0)
            letters = payload.get("Letters") or []
            with engine.begin() as connection:
                for letter in letters:
                    item = symbols.get(normalize_persian(str(letter.get("Symbol") or "")))
                    if not item:
                        unmatched += 1
                        continue
                    matched += 1
                    saved += int(_save_letter(connection, item, letter))
                connection.execute(text("""
                  INSERT INTO ingestion_checkpoints(source,pipeline,partition_key,cursor,watermark_at)
                  VALUES(:source,:pipeline,'global-pages',CAST(:cursor AS jsonb),now())
                  ON CONFLICT(source,pipeline,partition_key) DO UPDATE SET
                    cursor=excluded.cursor,watermark_at=excluded.watermark_at,updated_at=now()
                """), {"source": SOURCE, "pipeline": PIPELINE,
                         "cursor": json.dumps({"nextPage": next_page + 1, "totalPages": total_pages,
                                               "from": from_date, "to": to_date})})
            if next_page % 25 == 0 or next_page == total_pages:
                print(json.dumps({"page": next_page, "totalPages": total_pages, "saved": saved,
                                  "matched": matched, "unmatched": unmatched}), flush=True)
            next_page += 1
            time.sleep(CODAL_RATE_LIMIT_SECONDS)
        result = {"runId": run_id, "pages": total_pages, "saved": saved,
                  "matched": matched, "unmatched": unmatched}
        with engine.begin() as connection:
            connection.execute(text("""
              UPDATE ingestion_runs SET status='PASSED',finished_at=now(),metrics=CAST(:metrics AS jsonb)
              WHERE id=:id
            """), {"id": run_id, "metrics": json.dumps(result)})
        return result
    except Exception as exc:
        with engine.begin() as connection:
            connection.execute(text("""
              UPDATE ingestion_runs SET status='FAILED',finished_at=now(),error_summary=:error,
                metrics=CAST(:metrics AS jsonb) WHERE id=:id
            """), {"id": run_id, "error": str(exc)[:1000],
                     "metrics": json.dumps({"nextPage": next_page, "saved": saved})})
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-pages", type=int, default=12)
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--global-pages", action="store_true")
    args = parser.parse_args()
    result = run_global(not args.no_resume) if args.global_pages else run(args.max_pages, not args.no_resume)
    print(json.dumps(result, ensure_ascii=False))
