from __future__ import annotations


VALUATION_INPUT_UNITS = {
    "fcff": "IRR_million",
    "fcfe": "IRR_million",
    "capital_expenditure": "IRR_million",
    "net_borrowing": "IRR_million",
    "cost_of_equity": "percent",
    "wacc": "percent",
    "terminal_growth": "percent",
    "nav_per_share": "IRR",
    "units_outstanding": "units",
}


def validated_valuation_inputs(rows) -> tuple[dict, list[dict]]:
    """Accept only one fully sourced, canonical-unit value per period/key."""
    grouped = {}
    for row in rows:
        grouped.setdefault(row["input_key"], []).append(row)
    values = {}
    lineage = []
    for key, candidates in grouped.items():
        expected_unit = VALUATION_INPUT_UNITS.get(key)
        # Multiple VALID sources for one key remain an unresolved conflict,
        # even when their current numeric values happen to match.
        if expected_unit is None or len(candidates) != 1:
            continue
        row = candidates[0]
        if row["normalized_unit"] != expected_unit:
            continue
        if not row.get("source") or not row.get("source_disclosure_id") or not row.get("content_checksum"):
            continue
        value = float(row["value"])
        if key in {"cost_of_equity", "wacc"} and value <= 0:
            continue
        values[key] = value
        lineage.append({
            "inputKey": key,
            "unit": expected_unit,
            "source": row["source"],
            "sourceDisclosureId": row["source_disclosure_id"],
            "contentChecksum": row["content_checksum"],
        })
    return values, sorted(lineage, key=lambda item: item["inputKey"])
