import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .schema import InteractionRecord


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

    return [_row_to_record(row, field_map, source) for row in rows]


def _row_to_record(row: Dict[str, object], field_map: FieldMap, source: str) -> InteractionRecord:
    return InteractionRecord(
        user_id=str(row.get(field_map["user_id"], "")).strip(),
        item_id=str(row.get(field_map["item_id"], "")).strip(),
        rating=float(row.get(field_map["rating"], 0.0)),
        review_text=str(row.get(field_map["review_text"], "")).strip(),
        timestamp=_normalize_timestamp(row.get(field_map["timestamp"], None)),
        source=source,
        metadata={k: v for k, v in row.items() if k not in field_map.values()},
    )


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
