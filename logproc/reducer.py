"""Reduction helpers to merge worker partials into final aggregates."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from .metrics import PartialStats


def merge_partials(partials: Iterable[PartialStats]) -> PartialStats:
    """Merge ``PartialStats`` stream into a single ``PartialStats``.

    Args:
        partials: Iterable of worker partial outputs.

    Returns:
        A merged ``PartialStats`` object.

    Complexity:
        ``O(p + u)`` where ``p`` is number of partials and ``u`` unique URLs.
    """

    merged = PartialStats()
    merged_status_counter: Counter[str] = Counter()
    merged_slow_counter: Counter[str] = Counter()

    for part in partials:
        merged.total_lines += part.total_lines
        merged.bad_lines += part.bad_lines
        merged.total_status += part.total_status
        merged.total_slow += part.total_slow
        merged_status_counter.update(part.status_by_url)
        merged_slow_counter.update(part.slow_by_url)

    merged.status_by_url = dict(merged_status_counter)
    merged.slow_by_url = dict(merged_slow_counter)
    return merged
