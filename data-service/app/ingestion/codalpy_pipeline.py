"""Codalpy ingestion adapter.

The adapter deliberately keeps the source labels and raw payload.  Only
explicitly known labels are promoted to standard fact keys; unknown cells are
reported, never guessed or assigned a numeric fallback.
"""
from __future__ import annotations

import json
import time
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Callable

import jdatetime

SOURCE = "codalpy/codal.ir"
PIPELINE = "codalpy-standard-v1"
STATEMENTS = ("income_statement", "balance_sheet", "monthly_activity")

# Exact labels observed in Codal are intentionally enumerated. Extend only
# after inspecting a real response and adding a fixture/test for the label.
FACT_LABELS = {
    "درآمدهای عملیاتی": "revenue",
    "بهای تمام شده درآمدهای عملیاتی": "cogs",
    "سود (زیان) ناخالص": "gross_profit",
    "سود (زیان) عملیاتی": "operating_profit",
    "سود (زیان) خالص": "net_profit",
    "جمع دارایی ها": "total_assets",
    "جمع بدهی ها": "total_liabilities",
    "جمع حقوق مالکانه": "total_equity",
    "جمع دارایی‌ها": "total_assets",
    "جمع بدهی‌ها": "total_liabilities",
    "جمع حقوق صاحبان سهام": "total_equity",
    "جمع دارايي‌ها": "total_assets",
    "جمع دارايي ها": "total_assets",
    "جمع حقوق مالکانه": "total_equity",
    "جمع حقوق مالكانه": "total_equity",
    "سود (زیان) خالص هر سهم – ریال": "eps_basic",
    "سود (زیان) خالص هر سهم - ریال": "eps_basic",
    "سود(زیان) خالص هر سهم – ریال": "eps_basic",
}
def _label_key(value: str) -> str:
    return value.replace("ي", "ی").replace("ى", "ی").replace("ك", "ک").replace("\u200f", "").replace("\u200c", "").replace(" ", "").replace("‌", "")


def current_jalali() -> str:
    now = jdatetime.date.today()
    return f"{now.year:04d}/{now.month:02d}/{now.day:02d}"


def ranges(today: str | None = None) -> tuple[tuple[str, str], tuple[str, str]]:
    today = today or current_jalali()
    return (("1404/01/01", "1404/12/29"), ("1405/01/01", today))


def _number(value: Any) -> Decimal | None:
    if value is None or str(value).strip() == "":
        return None
    text = str(value).translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٬", "0123456789,"))
    text = text.replace(",", "").replace(" ", "").replace("−", "-")
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def _call_with_retry(call: Callable[[], Any], retries: int = 3, backoff: float = 1.0) -> Any:
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return call()
        except Exception as exc:  # Codalpy wraps HTTP, timeout and validation errors.
            last = exc
            if attempt == retries:
                raise
            time.sleep(backoff * (2 ** attempt))
    raise RuntimeError(str(last))


def _dump(value: Any) -> dict:
    return value.model_dump(mode="json") if hasattr(value, "model_dump") else value


def standardize(result: Any, output_type: str) -> list[dict]:
    """Convert successful Codalpy results to lossless standard records."""
    if output_type not in STATEMENTS:
        raise ValueError(output_type)
    rows: list[dict] = []
    for item in result or []:
        data = getattr(item, "data", None)
        if getattr(item, "status", None) != "success" or data is None:
            continue
        d = _dump(data)
        for sheet in d.get("sheets", []):
            for table in sheet.get("tables", []):
                row_labels = {}
                for candidate in table.get("cells", []):
                    raw_label = candidate.get("value")
                    if candidate.get("row_code") is not None and isinstance(raw_label, str) and _number(raw_label) is None:
                        label_text = raw_label.strip()
                        if label_text and candidate.get("cell_group_name") != "Header":
                            # Codal tables frequently reuse row_code for many
                            # visual rows; row_sequence is the stable join key
                            # between a label cell and its numeric siblings.
                            row_labels.setdefault(candidate.get("row_sequence"), label_text)
                for cell in table.get("cells", []):
                    label = str(cell.get("financial_concept") or row_labels.get(cell.get("row_sequence")) or cell.get("cell_group_name") or "").strip()
                    number = _number(cell.get("value"))
                    if number is None:
                        continue
                    key = next((mapped for known, mapped in FACT_LABELS.items() if _label_key(known) == _label_key(label)), None) if output_type != "monthly_activity" else None
                    rows.append({
                        "source": SOURCE, "output_type": output_type,
                        "source_action_id": f"{getattr(data, 'tracing_no', d.get('tracing_no'))}:{cell.get('address')}",
                        "tracing_no": str(d.get("tracing_no")),
                        "period_end_jalali": d.get("period_end_to_date"),
                        "fact_key": key, "source_label": label,
                        "value": str(number), "raw_value": cell.get("value"),
                        "unit": None, "payload": {
                            "sheet": {k: sheet.get(k) for k in ("code", "title_fa", "title_en", "sequence")},
                            "table": {k: table.get(k) for k in ("meta_table_id", "code", "title_fa", "title_en", "sequence", "sheet_code")},
                            "cell": cell,
                        },
                    })
    return rows


def fetch(symbol: str = "دکوثر", today: str | None = None, retries: int = 3) -> dict:
    from codalpy import Codal
    result: dict = {"symbol": symbol, "source": SOURCE, "ranges": [], "records": []}
    for start, end in ranges(today):
        codal = Codal(symbol, start, end)
        partition = {"from": start, "to": end, "outputs": {}}
        for output_type in STATEMENTS:
            values = _call_with_retry(getattr(codal, output_type), retries=retries)
            records = standardize(values, output_type)
            partition["outputs"][output_type] = {"responses": len(values), "records": len(records), "periods": sorted({r["period_end_jalali"] for r in records if r["period_end_jalali"]})}
            result["records"].extend(records)
        result["ranges"].append(partition)
    return result


def persist_records(records: list[dict]) -> int:
    """Persist only after the caller has explicitly applied migration 013."""
    from sqlalchemy import text
    from app.database import engine
    inserted = 0
    with engine.begin() as connection:
        for record in records:
            inserted += connection.execute(text("""
                INSERT INTO codalpy_records
                  (source,output_type,source_action_id,tracing_no,period_end_jalali,
                   fact_key,source_label,value,raw_value,unit,payload)
                VALUES (:source,:output_type,:source_action_id,:tracing_no,:period_end_jalali,
                        :fact_key,:source_label,:value,:raw_value,:unit,CAST(:payload AS jsonb))
                ON CONFLICT (source,source_action_id) DO NOTHING
            """), {**record, "payload": json.dumps(record["payload"], ensure_ascii=False)}).rowcount
    return inserted
