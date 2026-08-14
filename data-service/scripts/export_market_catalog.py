#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from sqlalchemy import text

from app.database import engine


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with engine.connect() as connection:
        rows = connection.execute(text("""
          SELECT DISTINCT sa.symbol,i.market_instrument_id AS market_id
          FROM symbol_aliases sa JOIN instruments i ON i.id=sa.instrument_id
          WHERE sa.valid_to IS NULL AND i.active AND i.market_instrument_id IS NOT NULL
          ORDER BY sa.symbol
        """)).mappings().all()
    with open(args.output, "w", encoding="utf-8") as output:
        json.dump([dict(row) for row in rows], output, ensure_ascii=False)
    print(json.dumps({"instruments": len(rows), "output": args.output}))


if __name__ == "__main__":
    main()
