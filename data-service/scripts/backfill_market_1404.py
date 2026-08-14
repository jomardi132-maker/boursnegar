#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import uuid
from datetime import date, datetime, time as datetime_time, timezone

import requests
from psycopg2.extras import execute_values
from sqlalchemy import text

from app.config import HTTP_USER_AGENT, TSETMC_TIMEOUT_SECONDS
from app.database import engine
from app.ingestion.market_history import filter_history, jalali_iso, model_family
from app.services.tsetmc_service import get_all_symbols


SOURCE = "tsetmc-closing-price-api"
PIPELINE = "market-history-1404-v1"
HISTORY_URL = "https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{market_id}/0"


def adjusted_closes(rows: list[dict]) -> dict[int, float | None]:
    """Back-adjust closes using TSETMC's official previous-price discontinuities."""
    ordered = sorted(rows, key=lambda row: int(row.get("dEven") or 0))
    result: dict[int, float | None] = {}
    cumulative = 1.0
    for index in range(len(ordered) - 1, -1, -1):
        row = ordered[index]
        close = row.get("pClosing")
        result[int(row["dEven"])] = float(close) * cumulative if close is not None else None
        if index == 0:
            continue
        previous_close = ordered[index - 1].get("pClosing")
        official_previous = row.get("priceYesterday")
        if previous_close not in (None, 0) and official_previous not in (None, 0):
            ratio = float(official_previous) / float(previous_close)
            if abs(ratio - 1.0) > 0.001:
                cumulative *= ratio
    return result


def upsert_catalog(connection, rows: list[dict]) -> list[dict]:
    selected = []
    for row in rows:
        symbol = str(row.get("l18") or "").strip()
        legal_name = str(row.get("l30") or symbol).strip()
        isin = str(row.get("isin") or "").strip()
        market_id = str(row.get("id") or "").strip()
        industry = str(row.get("cs") or "نامشخص").strip()
        if not symbol or not isin or not market_id:
            continue
        family = model_family(industry)
        existing = connection.execute(text("""
          SELECT i.id AS instrument_id,ir.id AS issuer_id
          FROM symbol_aliases sa
          JOIN instruments i ON i.id=sa.instrument_id
          JOIN issuers ir ON ir.id=i.issuer_id
          WHERE sa.symbol=:symbol AND sa.valid_to IS NULL
        """), {"symbol": symbol}).mappings().first()
        if existing:
            industry_id = connection.execute(text("""
              INSERT INTO industries(code,title_fa,model_family)
              VALUES(:code,:title,:family)
              ON CONFLICT(code) DO UPDATE SET title_fa=excluded.title_fa,
                model_family=CASE WHEN excluded.model_family='unclassified'
                  THEN industries.model_family ELSE excluded.model_family END
              RETURNING id
            """), {"code": f"market:{industry}", "title": industry,
                     "family": family}).scalar_one()
            connection.execute(text("""
              UPDATE issuers SET stable_code=:isin,legal_name=:legal_name,
                industry_id=:industry_id,updated_at=now() WHERE id=:issuer_id
            """), {"isin": isin, "legal_name": legal_name,
                     "industry_id": industry_id, "issuer_id": existing["issuer_id"]})
            connection.execute(text("""
              UPDATE instruments SET isin=:isin,market_instrument_id=:market_id,
                active=true WHERE id=:instrument_id
            """), {"isin": isin, "market_id": market_id,
                     "instrument_id": existing["instrument_id"]})
            selected.append({"symbol": symbol, "market_id": market_id, "family": family})
            continue
        connection.execute(text("""
          WITH industry AS (
            INSERT INTO industries(code,title_fa,model_family)
            VALUES(:industry_code,:industry,:family)
            ON CONFLICT(code) DO UPDATE SET title_fa=excluded.title_fa,
              model_family=CASE WHEN excluded.model_family='unclassified'
                THEN industries.model_family ELSE excluded.model_family END
            RETURNING id
          ), issuer AS (
            INSERT INTO issuers(stable_code,legal_name,industry_id)
            VALUES(:stable_code,:legal_name,(SELECT id FROM industry))
            ON CONFLICT(stable_code) DO UPDATE SET legal_name=excluded.legal_name,
              industry_id=excluded.industry_id,updated_at=now()
            RETURNING id
          ), instrument AS (
            INSERT INTO instruments(issuer_id,isin,market_instrument_id)
            VALUES((SELECT id FROM issuer),:isin,:market_id)
            ON CONFLICT(isin) DO UPDATE SET issuer_id=excluded.issuer_id,
              market_instrument_id=excluded.market_instrument_id,active=true
            RETURNING id
          )
          INSERT INTO symbol_aliases(instrument_id,symbol,valid_from,source)
          VALUES((SELECT id FROM instrument),:symbol,DATE '2025-03-21','BrsApi')
          ON CONFLICT(instrument_id,symbol,valid_from) DO UPDATE SET valid_to=NULL
        """), {
            "industry_code": f"market:{industry}", "industry": industry,
            "family": family, "stable_code": isin, "legal_name": legal_name,
            "isin": isin, "market_id": market_id, "symbol": symbol,
        })
        selected.append({"symbol": symbol, "market_id": market_id, "family": family})
    return selected


def save_prices(connection, instrument_id: str, rows: list[dict]) -> int:
    values = []
    retrieved_at = datetime.now(timezone.utc)
    adjusted = adjusted_closes(rows)
    for row in rows:
        raw_date = str(row["dEven"])
        trading_date = date(int(raw_date[:4]), int(raw_date[4:6]), int(raw_date[6:8]))
        raw_time = str(int(row.get("hEven") or 0)).zfill(6)
        timestamp = datetime.combine(
            trading_date,
            datetime_time(int(raw_time[:2]), int(raw_time[2:4]), int(raw_time[4:6])),
            tzinfo=timezone.utc,
        )
        values.append((
            instrument_id, trading_date, jalali_iso(trading_date), timestamp,
            row.get("priceFirst"), row.get("priceMax"), row.get("priceMin"),
            row.get("pClosing"), row.get("pDrCotVal"), adjusted.get(int(row["dEven"])),
            row.get("qTotTran5J"), row.get("qTotCap"), row.get("zTotTran"),
            SOURCE, retrieved_at,
        ))
    if not values:
        return 0
    raw = connection.connection.driver_connection
    with raw.cursor() as cursor:
        execute_values(cursor, """
          INSERT INTO daily_prices(
            instrument_id,trading_date,trading_date_jalali,price_timestamp,
            open,high,low,close,last,adjusted_close,volume,value,trade_count,
            source,retrieved_at
          ) VALUES %s
          ON CONFLICT(instrument_id,trading_date,source,adjustment_version)
          DO UPDATE SET open=excluded.open,high=excluded.high,low=excluded.low,
            close=excluded.close,last=excluded.last,adjusted_close=excluded.adjusted_close,
            volume=excluded.volume,
            value=excluded.value,trade_count=excluded.trade_count,
            retrieved_at=excluded.retrieved_at,quality_status='VALID'
        """, values, page_size=500)
    return len(values)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2025-03-21")
    parser.add_argument("--delay", type=float, default=0.35)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--refresh-catalog", action="store_true")
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    start = date.fromisoformat(args.start)
    run_id = str(uuid.uuid4())
    session = requests.Session()
    session.headers.update({"User-Agent": HTTP_USER_AGENT, "Accept": "application/json"})
    symbol_rows = get_all_symbols(force_refresh=True)
    selected = [
        {"symbol": str(row.get("l18") or "").strip(),
         "market_id": str(row.get("id") or "").strip(),
         "family": model_family(row.get("cs"))}
        for row in symbol_rows
        if str(row.get("l18") or "").strip()
        and str(row.get("id") or "").strip()
    ]
    with engine.begin() as connection:
        connection.execute(text("""
          INSERT INTO ingestion_runs(id,pipeline,source,partition_key,status,watermark)
          VALUES(:id,:pipeline,:source,:partition,'RUNNING',CAST(:watermark AS jsonb))
        """), {"id": run_id, "pipeline": PIPELINE, "source": SOURCE,
                 "partition": "all-market-instruments", "watermark": json.dumps({"start": args.start})})
        if args.refresh_catalog:
            selected = upsert_catalog(connection, symbol_rows)
        elif int(connection.execute(text("SELECT count(*) FROM instruments")).scalar_one()) < 1000:
            raise RuntimeError("catalog is incomplete; run once with --refresh-catalog")
        if not args.no_resume:
            completed = set(connection.execute(text("""
              SELECT partition_key FROM ingestion_checkpoints
              WHERE source=:source AND pipeline=:pipeline
            """), {"source": SOURCE, "pipeline": PIPELINE}).scalars())
            selected = [row for row in selected if row["market_id"] not in completed]
    selected.sort(key=lambda row: (row["family"], row["symbol"]))
    if args.limit:
        selected = selected[: args.limit]
    total_prices = failures = 0
    for index, item in enumerate(selected, 1):
        try:
            response = session.get(
                HISTORY_URL.format(market_id=item["market_id"]),
                timeout=max(20, TSETMC_TIMEOUT_SECONDS),
            )
            response.raise_for_status()
            history = filter_history(response.json().get("closingPriceDaily") or [], start)
            with engine.begin() as connection:
                instrument_id = connection.execute(text(
                    "SELECT id FROM instruments WHERE market_instrument_id=:market_id"
                ), {"market_id": item["market_id"]}).scalar_one()
                total_prices += save_prices(connection, str(instrument_id), history)
                connection.execute(text("""
                  INSERT INTO ingestion_checkpoints(source,pipeline,partition_key,cursor,watermark_at)
                  VALUES(:source,:pipeline,:partition,CAST(:cursor AS jsonb),now())
                  ON CONFLICT(source,pipeline,partition_key) DO UPDATE
                  SET cursor=excluded.cursor,watermark_at=excluded.watermark_at,updated_at=now()
                """), {"source": SOURCE, "pipeline": PIPELINE,
                         "partition": item["market_id"],
                         "cursor": json.dumps({"symbol": item["symbol"], "rows": len(history)})})
        except Exception as error:
            failures += 1
            with engine.begin() as connection:
                connection.execute(text("""
                  INSERT INTO ingestion_dead_letters(
                    ingestion_run_id,source_reference,stage,error_code,payload_reference
                  ) VALUES(:run,:reference,'history-fetch','FETCH_FAILED',:detail)
                """), {"run": run_id, "reference": item["market_id"],
                         "detail": str(error)[:500]})
        print(json.dumps({"progress": index, "total": len(selected), "symbol": item["symbol"],
                          "prices": total_prices, "failures": failures}, ensure_ascii=False), flush=True)
        if args.delay:
            time.sleep(args.delay)
    with engine.begin() as connection:
        connection.execute(text("""
          UPDATE ingestion_runs SET status=:status,finished_at=now(),
            metrics=CAST(:metrics AS jsonb),watermark=CAST(:watermark AS jsonb)
          WHERE id=:id
        """), {"id": run_id, "status": "PASSED" if failures == 0 else "FAILED",
                 "metrics": json.dumps({"symbols": len(selected), "prices": total_prices,
                                        "failures": failures}),
                 "watermark": json.dumps({"start": args.start, "completed": len(selected)})})
    print(json.dumps({"runId": run_id, "symbols": len(selected), "prices": total_prices,
                      "failures": failures}, ensure_ascii=False))


if __name__ == "__main__":
    main()
