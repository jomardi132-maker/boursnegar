#!/usr/bin/env python3
"""Refresh persisted snapshots from already imported Production evidence.

This intentionally calls only the local data-service endpoint. It never
discovers or downloads Codal documents and keeps a per-symbol checkpoint so a
bounded run can resume without losing successful refreshes.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols-file", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8001")
    parser.add_argument("--report-mode", default="latest_codal")
    parser.add_argument("--pause", type=float, default=0.2)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()
    symbols = [line.strip() for line in Path(args.symbols_file).read_text(encoding="utf-8").splitlines() if line.strip()]
    checkpoint_path = Path(args.checkpoint)
    state = json.loads(checkpoint_path.read_text(encoding="utf-8")) if checkpoint_path.exists() else {"done": {}, "errors": {}}
    session = requests.Session()
    for index, symbol in enumerate(symbols, start=1):
        if symbol in state["done"] or symbol in state["errors"]:
            continue
        try:
            response = session.post(
                f"{args.base_url.rstrip('/')}/api/v2/analyze",
                json={"query": symbol, "reportMode": args.report_mode},
                timeout=args.timeout,
            )
            if response.status_code == 200:
                payload = response.json()
                state["done"][symbol] = {"status": response.status_code, "analysis_id": payload.get("data", {}).get("analysisId")}
            else:
                state["errors"][symbol] = {"status": response.status_code, "detail": response.text[:240]}
        except requests.RequestException as exc:
            state["errors"][symbol] = {"status": "request_error", "detail": str(exc)[:240]}
        checkpoint_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        if index % 10 == 0 or index == len(symbols):
            print({"processed": index, "total": len(symbols), "ok": len(state["done"]), "errors": len(state["errors"])}, flush=True)
        time.sleep(max(0.0, args.pause))
    print(json.dumps({"total": len(symbols), "ok": len(state["done"]), "errors": len(state["errors"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
