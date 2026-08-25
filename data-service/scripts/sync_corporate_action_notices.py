#!/usr/bin/env python3
"""Promote confirmed Codal capital-registration notices with full lineage."""
from __future__ import annotations

import json

from sqlalchemy import text

from app.database import engine


SQL = text("""
INSERT INTO corporate_actions(
  instrument_id,action_type,announced_at,effective_date,effective_date_jalali,
  payload,disclosure_version_id,source,source_action_id
)
SELECT d.instrument_id,'capital_increase_registered',d.published_at,
  d.published_at::date,split_part(d.published_date_jalali,' ',1),
  jsonb_build_object(
    'title',d.title,'tracingNo',d.source_disclosure_id,
    'verification','registered_notice_without_inferred_ratio'
  ),dv.id,'codal-disclosure',d.source_disclosure_id
FROM disclosures d
JOIN LATERAL (
  SELECT id FROM disclosure_versions
  WHERE disclosure_id=d.id AND is_current ORDER BY version_number DESC LIMIT 1
) dv ON true
WHERE d.instrument_id IS NOT NULL
  AND d.title LIKE 'آگهی ثبت افزایش سرمایه%'
ON CONFLICT(source,source_action_id) DO UPDATE SET
  announced_at=excluded.announced_at,effective_date=excluded.effective_date,
  effective_date_jalali=excluded.effective_date_jalali,
  payload=excluded.payload,disclosure_version_id=excluded.disclosure_version_id
""")


def main() -> None:
    with engine.begin() as connection:
        affected = connection.execute(SQL).rowcount
        total = connection.execute(text(
            "select count(*) from corporate_actions where action_type='capital_increase_registered'"
        )).scalar_one()
    print(json.dumps({"affected": affected, "registeredActions": total}, ensure_ascii=False))


if __name__ == "__main__":
    main()
