#!/usr/bin/env python3
"""Fetch/report Codalpy data. Persistence is intentionally opt-in."""
import argparse, json
from app.ingestion.codalpy_pipeline import fetch

parser = argparse.ArgumentParser()
parser.add_argument("--symbol", default="دکوثر")
parser.add_argument("--today")
parser.add_argument("--retries", type=int, default=3)
parser.add_argument("--output", default="-")
parser.add_argument("--persist", action="store_true", help="write after migration 013 was explicitly applied")
args = parser.parse_args()
payload = fetch(args.symbol, args.today, args.retries)
summary = {"symbol": payload["symbol"], "source": payload["source"], "ranges": payload["ranges"], "total_records": len(payload["records"])}
text = json.dumps(summary, ensure_ascii=False, indent=2)
if args.persist:
    from app.ingestion.codalpy_pipeline import persist_records
    summary["inserted"] = persist_records(payload["records"])
    text = json.dumps(summary, ensure_ascii=False, indent=2)
if args.output == "-": print(text)
else:
    from pathlib import Path
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(text)
