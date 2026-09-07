#!/usr/bin/env python3
"""Repair browser-imported period lengths from official disclosure titles only."""
from __future__ import annotations

import argparse
import json
import re

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.database import engine


_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
_PERIOD = re.compile(r"(?:دوره\s*)?([0-9]{1,2})\s*ماهه")


def title_period_months(title: str | None) -> int | None:
    normalized = str(title or "").translate(_DIGITS)
    match = _PERIOD.search(normalized)
    if match:
        months = int(match.group(1))
        return months if 1 <= months <= 60 else None
    if "سال مالی" in normalized or "سالانه" in normalized:
        return 12
    return None


def repair(*, apply: bool, move_safe_facts: bool = False,
           quarantine_identical_duplicates: bool = False,
           quarantine_conflicting_period_facts: bool = False,
           move_nonoverlap_facts: bool = False) -> dict[str, object]:
    with engine.begin() as db:
        if not db.execute(
            text("SELECT pg_try_advisory_xact_lock(hashtextextended('boursnegar:browser-period-repair',0))")
        ).scalar():
            raise SystemExit("period repair lock is held")
        rows = db.execute(text("""
            SELECT fp.id, fp.length_months, d.title
            FROM financial_periods fp
            JOIN disclosure_versions dv ON dv.id = fp.disclosure_version_id
            JOIN disclosures d ON d.id = dv.disclosure_id
            WHERE d.source = 'browser/codal.ir'
        """)).mappings().all()
        candidates = []
        skipped = 0
        for row in rows:
            expected = title_period_months(row["title"])
            if expected is None:
                skipped += 1
            elif int(row["length_months"] or 0) != expected:
                candidates.append((row["id"], expected, int(row["length_months"] or 0), row["title"]))
        changed = 0
        conflicts = 0
        conflict_details = []
        moved_facts = 0
        blocked_fact_overlaps = 0
        quarantined_duplicate_facts = 0
        nonidentical_duplicates = 0
        quarantined_conflicting_facts = 0
        moved_nonoverlap_facts = 0
        if apply:
            for period_id, expected, current, title in candidates:
                canonical = db.execute(text("""
                    SELECT id
                    FROM financial_periods
                    WHERE id <> :id
                      AND issuer_id = (SELECT issuer_id FROM financial_periods WHERE id=:id)
                      AND end_date = (SELECT end_date FROM financial_periods WHERE id=:id)
                      AND audited = (SELECT audited FROM financial_periods WHERE id=:id)
                      AND scope = (SELECT scope FROM financial_periods WHERE id=:id)
                      AND disclosure_version_id = (SELECT disclosure_version_id FROM financial_periods WHERE id=:id)
                      AND length_months = :length
                    LIMIT 1
                """), {"id": period_id, "length": expected}).scalar()
                fact_count = None
                differing_fact_keys = []
                differing_fact_values = {}
                if move_safe_facts and canonical:
                    overlap = db.execute(text("""
                        SELECT count(*)
                        FROM financial_facts bad
                        JOIN financial_facts good
                          ON good.period_id=:canonical
                         AND good.fact_key=bad.fact_key
                         AND good.parser_version_id=bad.parser_version_id
                        WHERE bad.period_id=:bad
                    """), {"bad": period_id, "canonical": canonical}).scalar_one()
                    if overlap:
                        blocked_fact_overlaps += 1
                    else:
                        with db.begin_nested():
                            moved_facts += db.execute(
                                text("UPDATE financial_facts SET period_id=:canonical WHERE period_id=:bad"),
                                {"bad": period_id, "canonical": canonical},
                            ).rowcount
                if move_nonoverlap_facts and canonical:
                    with db.begin_nested():
                        moved_nonoverlap_facts += db.execute(text("""
                            UPDATE financial_facts bad
                            SET period_id=:canonical, quality_status='VALID'
                            WHERE bad.period_id=:bad
                              AND NOT EXISTS (
                                  SELECT 1 FROM financial_facts good
                                  WHERE good.period_id=:canonical
                                    AND good.fact_key=bad.fact_key
                                    AND good.parser_version_id=bad.parser_version_id
                              )
                        """), {"bad": period_id, "canonical": canonical}).rowcount
                if quarantine_identical_duplicates and canonical:
                    bad_facts = db.execute(text("""
                        SELECT fact_key, parser_version_id, raw_value, normalized_value,
                               raw_unit, normalized_unit, unit_multiplier, quality_status
                        FROM financial_facts WHERE period_id=:period
                    """), {"period": period_id}).mappings().all()
                    good_facts = db.execute(text("""
                        SELECT fact_key, parser_version_id, raw_value, normalized_value,
                               raw_unit, normalized_unit, unit_multiplier, quality_status
                        FROM financial_facts WHERE period_id=:period
                    """), {"period": canonical}).mappings().all()
                    # Quality status may already be DATA_REVIEW from a prior
                    # run; compare the underlying evidence fields instead.
                    comparable = lambda row: tuple(row[key] for key in (
                        "fact_key", "parser_version_id", "raw_value", "normalized_value",
                        "raw_unit", "normalized_unit", "unit_multiplier"
                    ))
                    fact_count = len(bad_facts)
                    bad_by_key = {f"{r['fact_key']}:{r['parser_version_id']}": comparable(r) for r in bad_facts}
                    good_by_key = {f"{r['fact_key']}:{r['parser_version_id']}": comparable(r) for r in good_facts}
                    differing_fact_keys = sorted(k for k in set(bad_by_key) | set(good_by_key) if bad_by_key.get(k) != good_by_key.get(k))
                    differing_fact_values = {
                        key: {"bad": bad_by_key.get(key), "canonical": good_by_key.get(key)}
                        for key in differing_fact_keys
                    }
                    if bad_facts and sorted(map(comparable, bad_facts), key=str) == sorted(map(comparable, good_facts), key=str):
                        with db.begin_nested():
                            quarantined_duplicate_facts += db.execute(
                                text("UPDATE financial_facts SET quality_status='DATA_REVIEW' WHERE period_id=:period AND quality_status='VALID'"),
                                {"period": period_id},
                            ).rowcount
                    else:
                        nonidentical_duplicates += 1
                try:
                    with db.begin_nested():
                        changed += db.execute(
                            text("UPDATE financial_periods SET length_months=:length WHERE id=:id"),
                            {"id": period_id, "length": expected},
                        ).rowcount
                except IntegrityError:
                    conflicts += 1
                    if quarantine_conflicting_period_facts and canonical:
                        with db.begin_nested():
                            quarantined_conflicting_facts += db.execute(
                                text("UPDATE financial_facts SET quality_status='DATA_REVIEW' WHERE period_id=:period AND quality_status='VALID'"),
                                {"period": period_id},
                            ).rowcount
                    symbol = db.execute(text("""
                        SELECT min(sa.symbol)
                        FROM financial_periods p
                        JOIN issuers iss ON iss.id=p.issuer_id
                        JOIN instruments ins ON ins.issuer_id=iss.id
                        JOIN symbol_aliases sa ON sa.instrument_id=ins.id AND sa.valid_to IS NULL
                        WHERE p.id=:id
                    """), {"id": period_id}).scalar()
                    conflict_details.append({
                        "period_id": str(period_id),
                        "current": current,
                        "expected": expected,
                        "title": title,
                        "canonical_period_id": str(canonical) if canonical else None,
                        "fact_count": fact_count,
                        "differing_fact_keys": differing_fact_keys,
                        "differing_fact_values": differing_fact_values,
                        "symbol": symbol,
                    })
        return {
            "apply": apply,
            "browser_periods": len(rows),
            "candidates": len(candidates),
            "changed": changed,
            "conflicts": conflicts,
            "move_safe_facts": move_safe_facts,
            "moved_facts": moved_facts,
            "blocked_fact_overlaps": blocked_fact_overlaps,
            "quarantine_identical_duplicates": quarantine_identical_duplicates,
            "quarantined_duplicate_facts": quarantined_duplicate_facts,
            "nonidentical_duplicates": nonidentical_duplicates,
            "quarantine_conflicting_period_facts": quarantine_conflicting_period_facts,
            "quarantined_conflicting_facts": quarantined_conflicting_facts,
            "move_nonoverlap_facts": move_nonoverlap_facts,
            "moved_nonoverlap_facts": moved_nonoverlap_facts,
            "conflict_details": conflict_details,
            "skipped_without_title_period": skipped,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--move-safe-facts", action="store_true")
    parser.add_argument("--quarantine-identical-duplicates", action="store_true")
    parser.add_argument("--quarantine-conflicting-period-facts", action="store_true")
    parser.add_argument("--move-nonoverlap-facts", action="store_true")
    args = parser.parse_args()
    print(json.dumps(repair(
        apply=args.apply,
        move_safe_facts=args.move_safe_facts,
        quarantine_identical_duplicates=args.quarantine_identical_duplicates,
        quarantine_conflicting_period_facts=args.quarantine_conflicting_period_facts,
        move_nonoverlap_facts=args.move_nonoverlap_facts,
    ), ensure_ascii=False, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
