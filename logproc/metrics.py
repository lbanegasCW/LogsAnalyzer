"""Metric data structures and helpers for log processing.

This module centralizes immutable-ish containers used across CLI and web interfaces.
All heavy processing keeps only aggregated counters to preserve bounded memory usage.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, Optional, Sequence, Tuple


@dataclass(slots=True)
class PartialStats:
    """Worker-local counters for a single processed batch.

    Attributes:
        total_lines: Number of lines seen in the batch.
        bad_lines: Number of malformed lines in the batch.
        total_status: Number of lines matching the target status code.
        total_slow: Number of lines with response time above threshold.
        status_by_url: Per-URL frequencies for target status code.
        slow_by_url: Per-URL frequencies for slow responses.
    """

    total_lines: int = 0
    bad_lines: int = 0
    total_status: int = 0
    total_slow: int = 0
    status_by_url: Dict[str, int] = field(default_factory=dict)
    slow_by_url: Dict[str, int] = field(default_factory=dict)


@dataclass(slots=True)
class ProcessingResult:
    """Final aggregated metrics for a full log run.

    Attributes:
        total_lines: Total number of processed lines.
        bad_lines: Total malformed lines.
        total_status: Total entries matching ``status_code``.
        total_slow: Total entries above ``slow_threshold``.
        top_url_status: URL with most matching status occurrences.
        top_url_slow: URL with most slow occurrences.
        top_10_status: Top 10 URLs for matching status.
        top_10_slow: Top 10 URLs for slow responses.
        elapsed_seconds: End-to-end processing duration in seconds.
        status_code: Status code used for filtering.
        slow_threshold: Slow threshold in milliseconds.
        workers: Number of workers used.
        profile_stats_path: Path to cProfile stats file, when profiling is enabled.
    """

    total_lines: int
    bad_lines: int
    total_status: int
    total_slow: int
    top_url_status: Tuple[Optional[str], int]
    top_url_slow: Tuple[Optional[str], int]
    top_10_status: Sequence[Tuple[str, int]]
    top_10_slow: Sequence[Tuple[str, int]]
    elapsed_seconds: float
    status_code: int
    slow_threshold: int
    workers: int
    profile_stats_path: Optional[str] = None

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary representation."""

        return asdict(self)


def top_url(counts: Dict[str, int]) -> Tuple[Optional[str], int]:
    """Return the URL with highest frequency.

    Args:
        counts: Mapping ``url -> count``.

    Returns:
        Tuple with (url, count). If ``counts`` is empty, returns ``(None, 0)``.
    """

    if not counts:
        return None, 0
    return max(counts.items(), key=lambda item: item[1])


def top_n_urls(counts: Dict[str, int], limit: int = 10) -> Sequence[Tuple[str, int]]:
    """Return the top-N URLs sorted by descending frequency.

    Args:
        counts: Mapping ``url -> count``.
        limit: Maximum number of pairs returned.

    Returns:
        A list of ``(url, count)`` pairs.

    Complexity:
        Runs in ``O(m log m)`` over number of unique URLs ``m``.
    """

    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]
