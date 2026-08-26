#!/usr/bin/env python3
"""Create a deterministic, local-only recovery plan from the coverage mirror."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sqlite3


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--db', default='artifacts/local-ingestion.sqlite3')
    p.add_argument('--out', default='artifacts/local-recovery-plan.csv')
    a = p.parse_args()
    db = sqlite3.connect(Path(a.db).resolve())
    rows = db.execute(
        """SELECT symbol, COALESCE(industry,'نامشخص'), status,
                  standard_count, period_count, gap_summary
           FROM symbols
           ORDER BY CASE status WHEN 'incomplete' THEN 0 WHEN 'comparable' THEN 1 ELSE 2 END,
                    period_count DESC, standard_count DESC, symbol"""
    ).fetchall()
    out = Path(a.out).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(('اولویت','نماد','صنعت','وضعیت','fact','دوره','کمبودها'))
        for n, row in enumerate(rows, 1): w.writerow((n, *row))
    print(f'rows={len(rows)} out={out}')


if __name__ == '__main__': main()
