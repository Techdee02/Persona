from collections import defaultdict
from datetime import datetime
from typing import Iterable, List, Tuple

from .schema import InteractionRecord


def temporal_split(
    records: Iterable[InteractionRecord],
    train_ratio: float = 0.8,
    min_user_records: int = 2,
) -> Tuple[List[InteractionRecord], List[InteractionRecord]]:
    grouped = defaultdict(list)
    for record in records:
        grouped[record.user_id].append(record)

    train: List[InteractionRecord] = []
    test: List[InteractionRecord] = []

    for user_id, user_records in grouped.items():
        if len(user_records) < min_user_records:
            train.extend(user_records)
            continue

        ordered = sorted(user_records, key=timestamp_key)
        split_index = max(1, int(len(ordered) * train_ratio))
        train.extend(ordered[:split_index])
        test.extend(ordered[split_index:])

    return train, test


def timestamp_key(record: InteractionRecord) -> float:
    if record.timestamp is None:
        return 0.0
    value = record.timestamp
    if value.isdigit():
        return float(value)

    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).timestamp()
        except ValueError:
            continue

    return 0.0
