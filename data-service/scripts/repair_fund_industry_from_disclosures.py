#!/usr/bin/env python3
"""Repair fund classification only from explicit imported disclosure titles."""
from __future__ import annotations

import argparse
import json

from sqlalchemy import bindparam, text

from app.database import engine


CANDIDATES_SQL = text("""
SELECT DISTINCT iss.id issuer_id
FROM issuers iss
JOIN industries current_industry ON current_industry.id=iss.industry_id
JOIN instruments ins ON ins.issuer_id=iss.id AND ins.active
JOIN disclosures d ON d.issuer_id=iss.id
WHERE current_industry.model_family='unclassified'
  AND (d.title LIKE '%صندوق سرمایه گذاری%' OR d.title LIKE '%صندوق سرمایه‌گذاری%')
ORDER BY iss.id
""")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    with engine.begin() as connection:
        fund_industries = connection.execute(text(
            "SELECT id FROM industries WHERE model_family='fund' ORDER BY id"
        )).scalars().all()
        if len(fund_industries) != 1:
            raise SystemExit(f"expected exactly one fund industry, found {len(fund_industries)}")
        issuer_ids = list(connection.execute(CANDIDATES_SQL).scalars())
        updated = 0
        if args.apply and issuer_ids:
            update = text("""
              UPDATE issuers SET industry_id=:fund_industry_id,updated_at=now()
              WHERE id IN :issuer_ids
            """).bindparams(bindparam("issuer_ids", expanding=True))
            result = connection.execute(update, {
                "fund_industry_id": fund_industries[0], "issuer_ids": issuer_ids,
            })
            updated = result.rowcount
    print(json.dumps({
        "apply": args.apply, "candidates": len(issuer_ids), "updated": updated,
        "evidence": "explicit_imported_disclosure_title",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
