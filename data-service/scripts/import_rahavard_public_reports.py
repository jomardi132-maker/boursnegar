#!/usr/bin/env python3
"""Collect public Rahavard365 reports into a quarantined, auditable cache.

This importer deliberately stops before financial_facts. Rahavard PDFs are an
external supplemental source; values must be reconciled with Codal before they
can affect the deterministic analysis engine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import urljoin

import requests

BASE_URL = "https://rahavard365.com"
LIST_URL = f"{BASE_URL}/api/v2/report/top-reports"
DETAIL_URL = f"{BASE_URL}/api/v2/report/reports/{{report_id}}"
FILE_URL = f"{BASE_URL}/api/v2/report/images/{{image_id}}/file"
PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")


def normalize_text(value: str) -> str:
    value = value.replace("\u200c", " ").replace("\u200f", " ").replace("\u202c", " ")
    return re.sub(r"[ \t]+", " ", value).strip()


def get_json(session: requests.Session, url: str, timeout: int = 30) -> dict:
    response = session.get(url, timeout=timeout, headers={"User-Agent": "Boursnegar-public-report-audit/1.0"})
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), (dict, list)):
        raise ValueError(f"unexpected response shape from {url}")
    return payload


def collect(limit: int, output: Path, delay: float = 1.0, session: requests.Session | None = None) -> dict:
    """Download at most ``limit`` latest public reports into ``output``."""
    output.mkdir(parents=True, exist_ok=True)
    (output / "pdf").mkdir(exist_ok=True)
    (output / "text").mkdir(exist_ok=True)
    session = session or requests.Session()
    reports = get_json(session, LIST_URL)["data"]
    if not isinstance(reports, list):
        raise ValueError("top-reports data is not a list")
    selected = reports[: max(0, limit)]
    manifest_path = output / "manifest.jsonl"
    results = {"candidates": len(selected), "downloaded": 0, "skipped": 0, "failed": 0}
    with manifest_path.open("a", encoding="utf-8") as manifest:
        for index, report in enumerate(selected):
            report_id = str(report.get("id") or "")
            try:
                if not report_id:
                    raise ValueError("report has no id")
                detail = get_json(session, DETAIL_URL.format(report_id=report_id))["data"]
                image_id = str(detail.get("image_id") or "")
                if not image_id:
                    raise ValueError("report has no public image_id")
                pdf_url = FILE_URL.format(image_id=image_id)
                pdf_response = session.get(pdf_url, timeout=60, headers={"User-Agent": "Boursnegar-public-report-audit/1.0"})
                pdf_response.raise_for_status()
                content = pdf_response.content
                if not content.startswith(b"%PDF"):
                    raise ValueError("public file endpoint did not return a PDF")
                checksum = hashlib.sha256(content).hexdigest()
                pdf_path = output / "pdf" / f"{checksum}.pdf"
                text_path = output / "text" / f"{checksum}.txt"
                if not pdf_path.exists():
                    pdf_path.write_bytes(content)
                if not text_path.exists():
                    subprocess.run(["pdftotext", "-raw", str(pdf_path), str(text_path)], check=True, timeout=60)
                text_sample = normalize_text(text_path.read_text(encoding="utf-8", errors="ignore"))[:500]
                record = {"status": "QUARANTINED", "source": "rahavard365", "report": detail,
                          "list_report": report, "pdf_url": pdf_url, "checksum_sha256": checksum,
                          "pdf_path": str(pdf_path), "text_path": str(text_path), "text_sample": text_sample,
                          "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                manifest.write(json.dumps(record, ensure_ascii=False) + "\n")
                manifest.flush()
                results["downloaded"] += 1
            except Exception as exc:
                manifest.write(json.dumps({"status": "FAILED", "source": "rahavard365", "report": report,
                                           "error": str(exc)[:300]}, ensure_ascii=False) + "\n")
                manifest.flush()
                results["failed"] += 1
            if index + 1 < len(selected):
                time.sleep(max(0.0, delay))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--output", default=os.getenv("RAHAVARD_QUARANTINE_ROOT", "/var/lib/boursnegar/rahavard-quarantine"))
    args = parser.parse_args()
    print(json.dumps(collect(args.limit, Path(args.output), args.delay), ensure_ascii=False))
