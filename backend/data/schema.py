from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class InteractionRecord:
    user_id: str
    item_id: str
    rating: float
    review_text: str
    timestamp: Optional[str]
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
