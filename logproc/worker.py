"""Batch worker logic executed in-process or in process pools."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from .metrics import PartialStats
from .parser import parse_line


def process_batch(batch: Iterable[str], status_code: int = 500, slow_threshold: int = 200) -> PartialStats:
    """Process one batch and return partial aggregate counters.

    Args:
        batch: Iterable of raw log lines.
        status_code: HTTP status code to count.
        slow_threshold: Milliseconds threshold for "slow" requests.

    Returns:
        ``PartialStats`` with counts and per-URL partial histograms.

    Complexity:
        ``O(b)`` per batch with bounded extra memory proportional to unique URLs.
    """

    stats = PartialStats()
    status_counter: Counter[str] = Counter()
    slow_counter: Counter[str] = Counter()

    for line in batch:
        stats.total_lines += 1
        parsed = parse_line(line)
        if parsed is None:
            stats.bad_lines += 1
            continue

        url, status, response_time = parsed

        if status == status_code:
            stats.total_status += 1
            status_counter[url] += 1

        if response_time > slow_threshold:
            stats.total_slow += 1
            slow_counter[url] += 1

    stats.status_by_url = dict(status_counter)
    stats.slow_by_url = dict(slow_counter)
    return stats
