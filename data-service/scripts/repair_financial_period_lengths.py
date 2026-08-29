#!/usr/bin/env python3
"""Audit and optionally repair period lengths from authoritative Codal titles."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database import engine
from app.services.codal_excel_parser import extract_period_length_months


SQL = text("""
SELECT fp.id,fp.issuer_id,fp.end_date,fp.length_months,fp.audited,fp.scope,
       fp.disclosure_version_id,d.title
FROM financial_periods fp
JOIN disclosure_versions dv ON dv.id=fp.disclosure_version_id
JOIN disclosures d ON d.id=dv.disclosure_id
ORDER BY fp.id
""")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write title-derived lengths")
    args = parser.parse_args()
    changes = []
    with engine.begin() as connection:
        rows = connection.execute(SQL).mappings().all()
        repairs = []
        for row in rows:
            expected = extract_period_length_months(row["title"])
            if expected is None or expected == row["length_months"]:
                continue
            repairs.append((row, expected))
            action = "repair"
            item = {"id": str(row["id"]), "old": row["length_months"], "new": expected, "action": action}
            changes.append(item)
        if args.apply and repairs:
            # Free the unique key space first. This makes repair order independent.
            for index, (row, _) in enumerate(repairs, start=1):
                connection.execute(
                    text("UPDATE financial_periods SET length_months=:length WHERE id=:id"),
                    {"id": row["id"], "length": 20000 + index},
                )

            for row, expected in repairs:
                candidates = connection.execute(text("""
                  SELECT id FROM financial_periods
                  WHERE issuer_id=:issuer_id AND end_date=:end_date
                    AND audited=:audited AND scope=:scope
                    AND disclosure_version_id=:disclosure_version_id
                    AND length_months=:length
                  ORDER BY id
                """), {"issuer_id": row["issuer_id"], "end_date": row["end_date"],
                       "audited": row["audited"], "scope": row["scope"],
                       "disclosure_version_id": row["disclosure_version_id"],
                       "length": expected}).scalars().all()
                target_id = candidates[0] if candidates else row["id"]
                if target_id != row["id"]:
                    connection.execute(text("""
                      INSERT INTO financial_facts
                        (issuer_id,period_id,fact_key,raw_value,normalized_value,raw_unit,
                         normalized_unit,unit_multiplier,currency_code,parser_version_id,
                         quality_status,created_at)
                      SELECT issuer_id,:target_id,fact_key,raw_value,normalized_value,raw_unit,
                             normalized_unit,unit_multiplier,currency_code,parser_version_id,
                             quality_status,created_at
                      FROM financial_facts
                      WHERE period_id=:source_id
                      ON CONFLICT(period_id,fact_key,parser_version_id) DO NOTHING
                    """), {"source_id": row["id"], "target_id": target_id})
                    connection.execute(text("""
                      DELETE FROM statement_line_items
                      WHERE financial_fact_id IN (SELECT id FROM financial_facts WHERE period_id=:source_id)
                    """), {"source_id": row["id"]})
                    connection.execute(text("DELETE FROM financial_facts WHERE period_id=:id"), {"id": row["id"]})
                    connection.execute(text("DELETE FROM financial_periods WHERE id=:id"), {"id": row["id"]})
                else:
                    connection.execute(
                        text("UPDATE financial_periods SET length_months=:length WHERE id=:id"),
                        {"id": row["id"], "length": expected},
                    )
    print(json.dumps({"apply": args.apply, "changes": len(changes), "items": changes[:100]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
