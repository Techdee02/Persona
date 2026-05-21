import csv
import json
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from .schema import InteractionRecord

logger = logging.getLogger("persona.loaders")

FieldMap = Dict[str, str]


DEFAULT_YELP_FIELDS: FieldMap = {
    "user_id": "user_id",
    "item_id": "business_id",
    "rating": "stars",
    "review_text": "text",
    "timestamp": "date",
}

DEFAULT_AMAZON_FIELDS: FieldMap = {
    "user_id": "reviewerID",
    "item_id": "asin",
    "rating": "overall",
    "review_text": "reviewText",
    "timestamp": "unixReviewTime",
}

DEFAULT_GOODREADS_FIELDS: FieldMap = {
    "user_id": "user_id",
    "item_id": "book_id",
    "rating": "rating",
    "review_text": "review_text",
    "timestamp": "date",
}


def load_yelp_reviews(path: str, field_map: Optional[FieldMap] = None) -> List[InteractionRecord]:
    return _load_reviews(path, field_map or DEFAULT_YELP_FIELDS, source="yelp")


def load_amazon_reviews(path: str, field_map: Optional[FieldMap] = None) -> List[InteractionRecord]:
    return _load_reviews(path, field_map or DEFAULT_AMAZON_FIELDS, source="amazon")


def load_goodreads_reviews(path: str, field_map: Optional[FieldMap] = None) -> List[InteractionRecord]:
    return _load_reviews(path, field_map or DEFAULT_GOODREADS_FIELDS, source="goodreads")


def _load_reviews(path: str, field_map: FieldMap, source: str) -> List[InteractionRecord]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    if file_path.suffix.lower() in {".jsonl", ".json"}:
        rows = _read_json_lines(file_path)
    elif file_path.suffix.lower() in {".csv"}:
        rows = _read_csv(file_path)
    else:
        raise ValueError(f"Unsupported dataset format: {file_path.suffix}")

    records: List[InteractionRecord] = []
    skipped = 0
    for row in rows:
        record, error = _row_to_record(row, field_map, source)
        if error:
            skipped += 1
            logger.debug("Skipping row: %s | row=%s", error, row)
        else:
            records.append(record)

    if skipped:
        logger.warning("Skipped %d invalid rows from %s", skipped, file_path)

    return records


def _row_to_record(
    row: Dict[str, object], field_map: FieldMap, source: str
) -> Tuple[Optional[InteractionRecord], Optional[str]]:
    """Return (record, None) on success or (None, error_message) on validation failure."""
    user_id = str(row.get(field_map["user_id"], "")).strip()
    item_id = str(row.get(field_map["item_id"], "")).strip()

    if not user_id:
        return None, "missing user_id"
    if not item_id:
        return None, "missing item_id"

    raw_rating = row.get(field_map["rating"])
    try:
        rating = float(raw_rating)
    except (TypeError, ValueError):
        return None, f"invalid rating: {raw_rating!r}"

    if not (0.0 <= rating <= 5.0):
        return None, f"rating out of range: {rating}"

    return InteractionRecord(
        user_id=user_id,
        item_id=item_id,
        rating=rating,
        review_text=str(row.get(field_map["review_text"], "")).strip(),
        timestamp=_normalize_timestamp(row.get(field_map["timestamp"], None)),
        source=source,
        metadata={k: v for k, v in row.items() if k not in field_map.values()},
    ), None


def _read_json_lines(path: Path) -> Iterable[Dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _read_csv(path: Path) -> Iterable[Dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield row


def _normalize_timestamp(value: object) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return str(int(value))
    text = str(value).strip()
    return text if text else None
