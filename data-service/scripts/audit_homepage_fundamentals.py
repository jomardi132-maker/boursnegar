#!/usr/bin/env python3
"""Audit the public fundamental payload for an explicit homepage symbol set."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from sqlalchemy import bindparam, text

from app.database import engine

CHILD_ENTITY_RE = re.compile(r"\(\s*(?:شرکت|موسسه)\s+[^()]+\s*\)\s*$")
INTEGRITY_SQL = text("SELECT id::text,quality_summary FROM analytical_snapshots WHERE id IN :ids").bindparams(
    bindparam("ids", expanding=True)
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols-file", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:3000")
    args = parser.parse_args()
    symbols = [value.strip() for value in Path(args.symbols_file).read_text(encoding="utf-8").splitlines() if value.strip()]
    rows, errors = [], []
    session = requests.Session()
    for symbol in symbols:
        response = session.get(f"{args.base_url.rstrip('/')}/api/stocks/{requests.utils.quote(symbol, safe='')}", timeout=30)
        if response.status_code != 200:
            errors.append({"symbol": symbol, "status": response.status_code, "detail": response.text[:200]})
            continue
        payload = response.json()
        stock, snapshot = payload["stock"], payload.get("snapshot") or {}
        rows.append({
            "symbol": symbol, "industry": stock.get("industry"), "model_family": stock.get("model_family"),
            "decision": snapshot.get("decision"), "analysis_state": snapshot.get("analysis_state"),
            "coverage": snapshot.get("coverage"), "confidence": snapshot.get("confidence"),
            "health_score": snapshot.get("score"), "valuation_method": snapshot.get("valuation_method"),
            "valuation_gate": snapshot.get("valuation_gate_status"), "valuation_reason": snapshot.get("valuation_gate_reason"),
            "missing_metrics": snapshot.get("missing_metrics") or [], "critical_warning": snapshot.get("critical_warning"),
            "disclosures": len(payload.get("disclosures") or []), "prices": len(payload.get("prices") or []),
            "snapshot_id": snapshot.get("id"),
        })
    ids = [row["snapshot_id"] for row in rows if row.get("snapshot_id")]
    selected = []
    if ids:
        with engine.begin() as connection:
            selected = list(connection.execute(INTEGRITY_SQL, {"ids": ids}).mappings())
    quarantined = child_titles = 0
    for selected_row in selected:
        quality = selected_row["quality_summary"] or {}
        quarantined += quality.get("evidenceQuarantined") is True
        child_titles += bool(CHILD_ENTITY_RE.search(str((quality.get("report") or {}).get("title") or "")))
    result = {
        "schema": "boursnegar-homepage-fundamental-audit-v2", "generated_at": datetime.now(timezone.utc).isoformat(),
        "symbols": len(symbols), "http_ok": len(rows), "errors": errors,
        "selected_snapshot_integrity": {"total": len(selected), "quarantined": quarantined, "child_titles": child_titles},
        "summary": {
            "valuation_ready": sum(row["valuation_gate"] == "READY" for row in rows),
            "standard": sum(row["analysis_state"] == "STANDARD" for row in rows),
            "market_closure_regime": sum(row["analysis_state"] == "MARKET_CLOSURE_REGIME" for row in rows),
            "with_missing_metrics": sum(bool(row["missing_metrics"]) for row in rows),
        }, "rows": rows,
    }
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("symbols", "http_ok", "errors", "selected_snapshot_integrity", "summary")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
