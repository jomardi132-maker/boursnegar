#!/usr/bin/env python3
"""Quarantine legacy child-entity facts without deleting provenance."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlalchemy import text

from app.database import engine

PREDICATE = "d.title ~ '\\([[:space:]]*(شرکت|موسسه)[[:space:]]+[^()]+\\)[[:space:]]*$'"
COUNT_SQL = text(f"""
SELECT count(DISTINCT d.source_disclosure_id) disclosures,
       count(DISTINCT fp.id) periods, count(ff.id) facts
FROM disclosures d JOIN disclosure_versions dv ON dv.disclosure_id=d.id
JOIN financial_periods fp ON fp.disclosure_version_id=dv.id
JOIN financial_facts ff ON ff.period_id=fp.id
WHERE {PREDICATE} AND ff.quality_status='VALID'
""")
UPDATE_SQL = text(f"""
UPDATE financial_facts ff SET quality_status='REVIEW'
FROM financial_periods fp, disclosure_versions dv, disclosures d
WHERE ff.period_id=fp.id AND fp.disclosure_version_id=dv.id
  AND dv.disclosure_id=d.id AND {PREDICATE} AND ff.quality_status='VALID'
""")
SNAPSHOT_PREDICATE = (
    "quality_summary->'report'->>'title' ~ "
    "'\\([[:space:]]*(شرکت|موسسه)[[:space:]]+[^()]+\\)[[:space:]]*$'"
)
SNAPSHOT_COUNT_SQL = text(f"""
SELECT count(*) snapshots
FROM analytical_snapshots
WHERE {SNAPSHOT_PREDICATE}
  AND coalesce(quality_summary->>'evidenceQuarantined','false') <> 'true'
""")
SNAPSHOT_UPDATE_SQL = text(f"""
UPDATE analytical_snapshots
SET quality_summary=jsonb_set(
  quality_summary,'{{evidenceQuarantined}}','true'::jsonb,true
)
WHERE {SNAPSHOT_PREDICATE}
  AND coalesce(quality_summary->>'evidenceQuarantined','false') <> 'true'
""")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    with engine.begin() as connection:
        if not connection.execute(text("SELECT pg_try_advisory_xact_lock(hashtextextended('boursnegar:child-entity-quarantine',0))")).scalar():
            raise SystemExit('advisory lock is held')
        before = dict(connection.execute(COUNT_SQL).mappings().one())
        snapshots_before = dict(connection.execute(SNAPSHOT_COUNT_SQL).mappings().one())
        changed = connection.execute(UPDATE_SQL).rowcount if args.apply else 0
        snapshots_changed = connection.execute(SNAPSHOT_UPDATE_SQL).rowcount if args.apply else 0
        after = dict(connection.execute(COUNT_SQL).mappings().one())
        snapshots_after = dict(connection.execute(SNAPSHOT_COUNT_SQL).mappings().one())
    result = {'schema':'boursnegar-child-entity-fact-quarantine-v1','applied':args.apply,
              'before':before,'changed':changed,'remaining_valid':after,
              'snapshots_before':snapshots_before,'snapshots_changed':snapshots_changed,
              'remaining_unquarantined_snapshots':snapshots_after,'physical_deletion':False}
    Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()
