"""Data containers and presentation helpers for aggregated metrics."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, Optional, Tuple


@dataclass
class PartialStats:
    """Worker-local counters for a single batch."""

    total_lines: int = 0
    bad_lines: int = 0
    total_500: int = 0
    total_slow: int = 0
    status_by_url: Dict[str, int] = field(default_factory=dict)
    slow_by_url: Dict[str, int] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Final reduced metrics for the full file."""

    total_lines: int
    bad_lines: int
    total_500: int
    total_slow: int
    url_mas_500: Tuple[Optional[str], int]
    url_mas_slow: Tuple[Optional[str], int]
    elapsed_seconds: float

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary."""

        return asdict(self)


def top_url(counts: Dict[str, int]) -> Tuple[Optional[str], int]:
    """Return the most frequent URL and count, or (None, 0) if empty."""

    if not counts:
        return None, 0
    return max(counts.items(), key=lambda item: item[1])
