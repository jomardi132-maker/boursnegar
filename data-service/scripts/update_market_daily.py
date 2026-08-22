#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from psycopg2.extras import execute_values
from sqlalchemy import text

from app.database import engine
from app.ingestion.market_history import jalali_iso
from app.services.tsetmc_service import get_all_symbols


SOURCE = "tsetmc-closing-price-api"
PIPELINE = "market-daily-eod-v1"
TEHRAN = ZoneInfo("Asia/Tehran")
MARKET_WEEKDAYS = {0, 1, 2, 5, 6}  # Monday-Wednesday and Saturday-Sunday


def valid_quote(row: dict) -> bool:
    return bool(
        str(row.get("id") or "").strip()
        and str(row.get("l18") or "").strip()
        and float(row.get("pc") or 0) > 0
        and float(row.get("py") or 0) > 0
    )


def market_fingerprint(rows: list[dict]) -> str:
    payload = [
        [str(row.get("id")), row.get("pc"), row.get("pl"), row.get("tvol"), row.get("tval"), row.get("tno")]
        for row in rows
        if valid_quote(row)
    ]
    payload.sort(key=lambda item: item[0])
    return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()


def adjusted_close(previous_adjusted: object, previous_close: object, close: object, yesterday: object) -> float:
    base = float(previous_adjusted if previous_adjusted is not None else previous_close or close)
    return base * float(close) / float(yesterday)


def parse_market_time(value: object) -> tuple[int, int, int]:
    parts = str(value or "00:00:00").split(":")
    if len(parts) != 3:
        return 0, 0, 0
    try:
        return tuple(max(0, int(part)) for part in parts)  # type: ignore[return-value]
    except ValueError:
        return 0, 0, 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Store one validated end-of-day market snapshot.")
    parser.add_argument("--date", type=date.fromisoformat)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-non-market-day", action="store_true")
    parser.add_argument("--pipeline", default=PIPELINE)
    parser.add_argument("--source", default=SOURCE)
    args = parser.parse_args()

    trading_date = args.date or datetime.now(TEHRAN).date()
    if trading_date.weekday() not in MARKET_WEEKDAYS and not args.allow_non_market_day:
        print(json.dumps({"status": "skipped", "reason": "non-market-weekday", "date": str(trading_date)}))
        return

    rows = get_all_symbols(force_refresh=True)
    quotes = [row for row in rows if valid_quote(row)]
    traded = sum(1 for row in quotes if int(row.get("tno") or 0) > 0 and float(row.get("tvol") or 0) > 0)
    if len(quotes) < 1000 or traded < 100:
        raise RuntimeError(f"market snapshot failed quality gate: quotes={len(quotes)}, traded={traded}")

    fingerprint = market_fingerprint(quotes)
    if args.dry_run:
        print(json.dumps({"status": "validated", "date": str(trading_date), "quotes": len(quotes),
                          "traded": traded, "fingerprint": fingerprint}))
        return

    run_id = str(uuid.uuid4())
    with engine.begin() as connection:
        previous = connection.execute(text("""
          SELECT watermark->>'fingerprint' FROM ingestion_runs
          WHERE pipeline=:pipeline AND source=:source AND status='PASSED'
          ORDER BY finished_at DESC NULLS LAST LIMIT 1
        """), {"pipeline": args.pipeline, "source": args.source}).scalar()
        connection.execute(text("""
          INSERT INTO ingestion_runs(id,pipeline,source,partition_key,status,watermark)
          VALUES(:id,:pipeline,:source,:partition,'RUNNING',CAST(:watermark AS jsonb))
        """), {"id": run_id, "pipeline": args.pipeline, "source": args.source,
                 "partition": str(trading_date),
                 "watermark": json.dumps({"date": str(trading_date), "fingerprint": fingerprint})})
        if previous == fingerprint:
            connection.execute(text("""
              UPDATE ingestion_runs SET status='PASSED',finished_at=now(),
                metrics=CAST(:metrics AS jsonb) WHERE id=:id
            """), {"id": run_id, "metrics": json.dumps({"skipped": True, "reason": "unchanged-source"})})
            print(json.dumps({"status": "skipped", "reason": "unchanged-source", "date": str(trading_date)}))
            return

    try:
        with engine.begin() as connection:
            catalog = connection.execute(text("""
              SELECT i.id::text AS instrument_id,i.market_instrument_id,
                p.close AS previous_close,p.adjusted_close AS previous_adjusted
              FROM instruments i
              LEFT JOIN LATERAL (
                SELECT close,adjusted_close FROM daily_prices
                WHERE instrument_id=i.id AND trading_date<:trading_date
                ORDER BY trading_date DESC LIMIT 1
              ) p ON true
              WHERE i.active=true AND i.market_instrument_id IS NOT NULL
            """), {"trading_date": trading_date}).mappings()
            by_market_id = {str(row["market_instrument_id"]): row for row in catalog}
            retrieved_at = datetime.now(timezone.utc)
            values = []
            missing = 0
            for quote in quotes:
                instrument = by_market_id.get(str(quote["id"]))
                if not instrument:
                    missing += 1
                    continue
                hour, minute, second = parse_market_time(quote.get("time"))
                timestamp = datetime(trading_date.year, trading_date.month, trading_date.day,
                                     min(hour, 23), min(minute, 59), min(second, 59), tzinfo=TEHRAN)
                values.append((
                    instrument["instrument_id"], trading_date, jalali_iso(trading_date), timestamp,
                    quote.get("pf"), quote.get("pmax"), quote.get("pmin"), quote.get("pc"), quote.get("pl"),
                    adjusted_close(instrument["previous_adjusted"], instrument["previous_close"],
                                   quote.get("pc"), quote.get("py")),
                    quote.get("tvol"), quote.get("tval"), quote.get("tno"), quote.get("mv"), quote.get("z"),
                    args.source, retrieved_at,
                ))
            if len(values) < 1000 or missing > 100:
                raise RuntimeError(f"catalog coverage failed: values={len(values)}, missing={missing}")
            raw = connection.connection.driver_connection
            with raw.cursor() as cursor:
                execute_values(cursor, """
                  INSERT INTO daily_prices(
                    instrument_id,trading_date,trading_date_jalali,price_timestamp,
                    open,high,low,close,last,adjusted_close,volume,value,trade_count,
                    market_cap,shares_outstanding,source,retrieved_at
                  ) VALUES %s
                  ON CONFLICT(instrument_id,trading_date,source,adjustment_version)
                  DO UPDATE SET open=excluded.open,high=excluded.high,low=excluded.low,
                    close=excluded.close,last=excluded.last,adjusted_close=excluded.adjusted_close,
                    volume=excluded.volume,value=excluded.value,trade_count=excluded.trade_count,
                    market_cap=excluded.market_cap,shares_outstanding=excluded.shares_outstanding,
                    price_timestamp=excluded.price_timestamp,retrieved_at=excluded.retrieved_at,
                    quality_status='VALID'
                """, values, page_size=500)
            connection.execute(text("""
              UPDATE ingestion_runs SET status='PASSED',finished_at=now(),
                metrics=CAST(:metrics AS jsonb) WHERE id=:id
            """), {"id": run_id, "metrics": json.dumps({"quotes": len(quotes), "traded": traded,
                                                           "prices": len(values), "missing": missing})})
        print(json.dumps({"status": "passed", "runId": run_id, "date": str(trading_date),
                          "prices": len(values), "missing": missing}))
    except Exception as error:
        with engine.begin() as connection:
            connection.execute(text("""
              UPDATE ingestion_runs SET status='FAILED',finished_at=now(),error_summary=:error
              WHERE id=:id
            """), {"id": run_id, "error": str(error)[:1000]})
        raise


if __name__ == "__main__":
    main()
