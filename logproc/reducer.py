"""Reduce/merge partial stats from workers into final metrics."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from .metrics import PartialStats


def merge_partials(partials: Iterable[PartialStats]) -> PartialStats:
    """Merge PartialStats objects efficiently using additive counters."""

    merged = PartialStats()
    merged_status_counter: Counter[str] = Counter()
    merged_slow_counter: Counter[str] = Counter()

    for part in partials:
        merged.total_lines += part.total_lines
        merged.bad_lines += part.bad_lines
        merged.total_500 += part.total_500
        merged.total_slow += part.total_slow
        merged_status_counter.update(part.status_by_url)
        merged_slow_counter.update(part.slow_by_url)

    merged.status_by_url = dict(merged_status_counter)
    merged.slow_by_url = dict(merged_slow_counter)
    return merged
