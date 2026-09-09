#!/usr/bin/env python3
"""Create a deterministic, local-only recovery plan from the coverage mirror."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sqlite3
import json


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--db', default='data-service/artifacts/local-ingestion.sqlite3')
    p.add_argument('--out', default='data-service/artifacts/local-recovery-plan.csv')
    p.add_argument('--include-complete', action='store_true',
                   help='Include complete symbols only for an explicitly requested audit')
    p.add_argument('--exclusions', default='data-service/artifacts/local-recovery-exclusions.txt')
    p.add_argument('--recent-artifact-root', default='',
                   help='Skip symbols already attempted in batch-gate reports under this root')
    p.add_argument('--coverage-csv', default='',
                   help='Authoritative Production coverage-symbols.csv used for adaptive ordering')
    a = p.parse_args()
    db = sqlite3.connect(Path(a.db).resolve())
    # The planner is also used before the first local artifact import.  Make
    # the registry schema available without inventing symbols or facts; the
    # authoritative registry is populated separately by ingestion_console.
    db.executescript("""
        CREATE TABLE IF NOT EXISTS symbols(
          symbol TEXT PRIMARY KEY, industry TEXT,
          status TEXT NOT NULL DEFAULT 'unknown',
          last_remote_count INTEGER, last_local_count INTEGER,
          standard_count INTEGER NOT NULL DEFAULT 0,
          period_count INTEGER NOT NULL DEFAULT 0,
          gap_summary TEXT NOT NULL DEFAULT '', last_error TEXT,
          updated_at TEXT NOT NULL DEFAULT ''
        );
    """)
    try:
        db.execute("ALTER TABLE symbols ADD COLUMN completion_state TEXT NOT NULL DEFAULT 'UNKNOWN'")
    except sqlite3.OperationalError:
        pass
    exclusion_path = Path(a.exclusions)
    exclusions = {line.strip() for line in exclusion_path.read_text(encoding='utf-8').splitlines()
                  if line.strip() and not line.lstrip().startswith('#')} if exclusion_path.exists() else set()
    recent = Path(a.recent_artifact_root)
    if recent.exists():
        for report_path in recent.glob('fund-nav-followup-*-docs/batch-gate-report.json'):
            try:
                report = json.loads(report_path.read_text(encoding='utf-8'))
                exclusions.update(report.get('symbols', []))
            except (OSError, json.JSONDecodeError):
                continue
    rows = db.execute(
        """SELECT symbol, COALESCE(industry,'نامشخص'), status,
                  standard_count, period_count, gap_summary
           FROM symbols
           WHERE (:include_complete = 1 OR (status NOT IN ('complete','not_applicable')
                  AND completion_state NOT IN ('SOURCE_EXHAUSTED','FUND_MISSING','FUND_PARTIAL')))
           ORDER BY CASE
                      WHEN gap_summary LIKE '%دوره مقایسه%' THEN 0
                      WHEN gap_summary LIKE '%fact%' OR gap_summary LIKE '%صورت%' THEN 1
                      WHEN gap_summary LIKE '%اطلاعیه%' THEN 2
                      WHEN status = 'incomplete' THEN 3
                      WHEN status = 'comparable' THEN 4
                      ELSE 9 END,
                    period_count DESC, standard_count DESC, symbol"""
    , {'include_complete': int(a.include_complete)}).fetchall()
    rows = [row for row in rows if row[0] not in exclusions]
    coverage = {}
    if a.coverage_csv:
        with Path(a.coverage_csv).open(encoding='utf-8-sig', newline='') as f:
            for item in csv.DictReader(f):
                symbol = (item.get('symbol') or '').strip()
                if symbol:
                    coverage[symbol] = item
        def adaptive_key(row):
            item = coverage.get(row[0], {})
            tier = item.get('coverage_tier', '')
            tier_rank = {'MISSING_COMPARABLE_PERIODS': 0, 'FUND_MODEL_REQUIRED': 1,
                         'CORE_READY': 2}.get(tier, 9)
            try:
                periods = int(item.get('valid_periods') or 0)
                facts = int(item.get('valid_fact_keys') or 0)
            except ValueError:
                periods, facts = 0, 0
            # Prefer the least-covered members within the most important tier.
            return (tier_rank, periods, facts, row[0])
        rows.sort(key=adaptive_key)
    out = Path(a.out).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(('اولویت','نماد','صنعت','وضعیت','fact','دوره','کمبودها','coverage_tier','valid_periods','valid_fact_keys'))
        for n, row in enumerate(rows, 1):
            item = coverage.get(row[0], {})
            w.writerow((n, *row, item.get('coverage_tier',''), item.get('valid_periods',''), item.get('valid_fact_keys','')))
    print(f'rows={len(rows)} out={out}')


if __name__ == '__main__': main()
