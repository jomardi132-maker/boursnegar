#!/usr/bin/env python3
"""Reconcile public registry operator gates with all-active evidence tiers."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ACTION_CLOSED = "پایش دوره بعدی و refresh عادی؛ recovery دوره‌ای این نماد بسته شد."
ACTION_FIRST_REPORT = (
    "بازیابی نخستین صورت مالی رسمی قابل‌استخراج؛ تا آن زمان هیچ import یا تصمیم بنیادی."
)
ACTION_SECOND_PERIOD = "بازیابی یک دوره مالی معتبر دوم؛ period فعلی کافی برای مقایسه نیست."
ACTION_SNAPSHOT_REFRESH = "refresh snapshot از facts موجود؛ import جدید لازم نیست."
ACTION_FUND_MODEL = "مدل مستقل NAV/پورتفو برای صندوق لازم است؛ ارزش‌گذاری شرکتی اعمال نشود."
ACTION_CONFIDENCE = "گیت تحلیلی/اطمینان باقی است؛ recovery دوره‌ای بسته شده و تصمیم قطعی ساخته نشود."


def _float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def operator_gate(item: dict[str, Any]) -> tuple[str, str]:
    """Return the current operator-facing gate and next action.

    The source registry mixed old public gates with newer all-active tiers. This
    function keeps evidence gaps open only when the authoritative tier still
    says they are open.
    """
    tier = item.get("all_active_coverage_tier")
    periods = int(item.get("all_active_valid_periods") or 0)
    refresh = item.get("public_snapshot_refresh")
    decision = item.get("decision")
    coverage = _float(item.get("data_coverage"))

    if tier == "FUND_MODEL_REQUIRED":
        return "FUND_MODEL_REQUIRED", ACTION_FUND_MODEL
    if tier == "MISSING_COMPARABLE_PERIODS":
        if refresh == "no_stored_report_404" or periods == 0:
            return "NO_KNOWN_DATA_GATE", ACTION_FIRST_REPORT
        return "MISSING_COMPARABLE_PERIODS", ACTION_SECOND_PERIOD
    if tier == "MISSING_CORE_FACTS":
        return "MISSING_CORE_FACTS", "بازیابی fact اصلی رسمی؛ بدون مقدار حدسی."
    if tier == "NO_CURRENT_ALIAS":
        return "NO_CURRENT_ALIAS", "تطبیق alias رسمی فعال؛ بدون ساخت هویت نماد."
    if refresh != "success":
        return "SNAPSHOT_REFRESH_GATE", ACTION_SNAPSHOT_REFRESH
    if coverage is not None and coverage < 100:
        return "SNAPSHOT_COVERAGE_GAP", ACTION_CONFIDENCE
    if decision == "INSUFFICIENT_DATA":
        return "ANALYTICAL_CONFIDENCE_GATE", ACTION_CONFIDENCE
    return "RECOVERY_CLOSED", ACTION_CLOSED


def reconcile(registry: dict[str, Any]) -> dict[str, Any]:
    items = []
    changed = 0
    for original in registry.get("items", []):
        item = dict(original)
        source_gate = item.get("gate")
        gate, next_action = operator_gate(item)
        item["source_gate"] = source_gate
        item["gate"] = gate
        item["next_action"] = next_action
        if gate != source_gate or next_action != original.get("next_action"):
            changed += 1
        items.append(item)

    result = dict(registry)
    result["schema"] = "boursnegar-public-gate-registry-v2"
    result["generated_at"] = datetime.now(timezone.utc).isoformat()
    result["source_registry_schema"] = registry.get("schema")
    result["reconciliation"] = {
        "changed_items": changed,
        "gate_counts": dict(Counter(item.get("gate") for item in items)),
        "source_gate_counts": dict(Counter(item.get("source_gate") for item in items)),
        "policy": (
            "operator gate follows all_active_coverage_tier and refresh status; "
            "source_gate preserves the prior registry value"
        ),
    }
    result["items"] = items
    return result


def write_csv(registry: dict[str, Any], path: Path) -> None:
    items = registry.get("items", [])
    fieldnames: list[str] = []
    for item in items:
        for key in item:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--csv-output", type=Path)
    args = parser.parse_args()

    source = json.loads(args.registry.read_text(encoding="utf-8"))
    result = reconcile(source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    output = {"output": str(args.output), "sha256": sha256(args.output)}
    if args.csv_output:
        args.csv_output.parent.mkdir(parents=True, exist_ok=True)
        write_csv(result, args.csv_output)
        output["csv_output"] = str(args.csv_output)
        output["csv_sha256"] = sha256(args.csv_output)
    output["reconciliation"] = result["reconciliation"]
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
