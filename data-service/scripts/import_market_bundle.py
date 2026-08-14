#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import uuid

from sqlalchemy import text

from app.database import engine
from scripts.backfill_market_1404 import PIPELINE, SOURCE, save_prices


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True)
    args = parser.parse_args()
    run_id = str(uuid.uuid4())
    with engine.begin() as connection:
        connection.execute(text("""
          INSERT INTO ingestion_runs(id,pipeline,source,partition_key,status)
          VALUES(:id,:pipeline,:source,'all-market-offline-bundle','RUNNING')
        """), {"id": run_id, "pipeline": PIPELINE, "source": SOURCE})
    imported = prices = failures = 0
    with gzip.open(args.bundle, "rt", encoding="utf-8") as bundle:
        for line in bundle:
            item = json.loads(line)
            try:
                with engine.begin() as connection:
                    instrument_id = connection.execute(
                        text("SELECT id FROM instruments WHERE market_instrument_id=:market_id"),
                        {"market_id": item["market_id"]},
                    ).scalar_one()
                    prices += save_prices(connection, str(instrument_id), item["rows"])
                imported += 1
            except Exception as error:
                failures += 1
                print(json.dumps({"symbol": item.get("symbol"), "error": str(error)[:180]}, ensure_ascii=False), flush=True)
            print(json.dumps({"imported": imported, "prices": prices, "failures": failures}), flush=True)
    metrics = {"symbols": imported, "prices": prices, "failures": failures}
    with engine.begin() as connection:
        connection.execute(text("""
          UPDATE ingestion_runs SET status=:status,finished_at=now(),metrics=CAST(:metrics AS jsonb),
            error_summary=:error WHERE id=:id
        """), {"id": run_id, "status": "PASSED" if failures == 0 else "FAILED",
                 "metrics": json.dumps(metrics), "error": None if failures == 0 else f"{failures} imports failed"})
    print(json.dumps({"runId": run_id, **metrics}), flush=True)


if __name__ == "__main__":
    main()
