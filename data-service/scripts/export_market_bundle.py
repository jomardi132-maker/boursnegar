#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import time

import requests

from app.config import HTTP_USER_AGENT, TSETMC_TIMEOUT_SECONDS
from app.ingestion.market_history import filter_history


HISTORY_URL = "https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{market_id}/0"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--start", default="2025-03-21")
    parser.add_argument("--delay", type=float, default=0.1)
    args = parser.parse_args()
    from datetime import date

    catalog = json.load(open(args.catalog, encoding="utf-8"))
    session = requests.Session()
    session.headers.update({"User-Agent": HTTP_USER_AGENT, "Accept": "application/json"})
    failures = exported = 0
    with gzip.open(args.output, "wt", encoding="utf-8") as bundle:
        for index, item in enumerate(catalog, 1):
            try:
                response = session.get(
                    HISTORY_URL.format(market_id=item["market_id"]),
                    timeout=max(20, TSETMC_TIMEOUT_SECONDS),
                )
                response.raise_for_status()
                rows = filter_history(response.json().get("closingPriceDaily") or [], date.fromisoformat(args.start))
                bundle.write(json.dumps({**item, "rows": rows}, ensure_ascii=False) + "\n")
                exported += 1
            except Exception as error:
                failures += 1
                print(json.dumps({"symbol": item["symbol"], "error": str(error)[:180]}, ensure_ascii=False), flush=True)
            print(json.dumps({"progress": index, "total": len(catalog), "exported": exported, "failures": failures}), flush=True)
            time.sleep(args.delay)
    print(json.dumps({"symbols": len(catalog), "exported": exported, "failures": failures, "output": args.output}), flush=True)


if __name__ == "__main__":
    main()
