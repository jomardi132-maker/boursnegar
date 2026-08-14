#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from sqlalchemy import text

from app.database import SessionLocal
from app.ingestion.macro_seed import validate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Import an official macro dataset")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    dataset = validate_dataset(json.loads(args.dataset.read_text(encoding="utf-8")))
    print(
        json.dumps(
            {
                "valid": True,
                "series": dataset["series"]["code"],
                "observations": len(dataset["observations"]),
                "mode": "apply" if args.apply else "dry-run",
            }
        )
    )
    if not args.apply:
        return
    db = SessionLocal()
    try:
        series = dataset["series"]
        series_id = db.execute(
            text(
                """
                INSERT INTO macro_series(code,title_fa,source,unit,frequency,base_year)
                VALUES(:code,:title_fa,:source,:unit,:frequency,:base_year)
                ON CONFLICT(code) DO UPDATE SET title_fa=excluded.title_fa,
                  source=excluded.source,unit=excluded.unit,frequency=excluded.frequency,
                  base_year=excluded.base_year,active=true
                RETURNING id
                """
            ),
            {**series, "base_year": series.get("base_year")},
        ).scalar_one()
        for observation in dataset["observations"]:
            db.execute(
                text(
                    """
                    INSERT INTO macro_observations(
                      series_id,reference_start,reference_end,reference_period_jalali,
                      publication_date,effective_date,value,revision,retrieved_at,
                      source_reference,checksum,quality_status,confidence
                    ) VALUES(
                      :series_id,:reference_start,:reference_end,:reference_period_jalali,
                      :publication_date,:effective_date,:value,:revision,now(),
                      :source_reference,:checksum,:quality_status,:confidence
                    ) ON CONFLICT(series_id,reference_start,reference_end,revision)
                    DO UPDATE SET publication_date=excluded.publication_date,
                      effective_date=excluded.effective_date,value=excluded.value,
                      retrieved_at=now(),source_reference=excluded.source_reference,
                      checksum=excluded.checksum,quality_status=excluded.quality_status,
                      confidence=excluded.confidence
                    """
                ),
                {"series_id": series_id, **observation},
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
