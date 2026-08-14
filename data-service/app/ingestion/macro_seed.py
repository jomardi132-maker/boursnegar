import hashlib
import json
from datetime import date
from decimal import Decimal


REQUIRED_OBSERVATION_FIELDS = {
    "reference_start",
    "reference_end",
    "reference_period_jalali",
    "publication_date",
    "effective_date",
    "value",
    "source_reference",
}


def validate_dataset(dataset: dict) -> dict:
    series = dataset.get("series") or {}
    for field in ("code", "title_fa", "source", "unit", "frequency"):
        if not str(series.get(field) or "").strip():
            raise ValueError(f"series.{field} is required")
    if not str(series["source"]).startswith("https://"):
        raise ValueError("series.source must be an https URL")
    observations = dataset.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("observations must be a non-empty list")
    normalized = []
    for index, observation in enumerate(observations):
        missing = REQUIRED_OBSERVATION_FIELDS - observation.keys()
        if missing:
            raise ValueError(f"observation {index} missing {sorted(missing)}")
        start = date.fromisoformat(observation["reference_start"])
        end = date.fromisoformat(observation["reference_end"])
        publication = date.fromisoformat(observation["publication_date"])
        effective = date.fromisoformat(observation["effective_date"])
        if end < start or publication < end or effective < start:
            raise ValueError(f"observation {index} has an invalid date sequence")
        value = Decimal(str(observation["value"]))
        confidence = Decimal(str(observation.get("confidence", 100)))
        if confidence < 0 or confidence > 100:
            raise ValueError(f"observation {index} confidence is invalid")
        if not str(observation["source_reference"]).startswith("https://"):
            raise ValueError(f"observation {index} source_reference must be https")
        canonical = json.dumps(observation, ensure_ascii=False, sort_keys=True).encode()
        normalized.append(
            {
                **observation,
                "value": value,
                "confidence": confidence,
                "revision": int(observation.get("revision", 0)),
                "quality_status": observation.get("quality_status", "VALID"),
                "checksum": hashlib.sha256(canonical).hexdigest(),
            }
        )
    return {"series": series, "observations": normalized}
