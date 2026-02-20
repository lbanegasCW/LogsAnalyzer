"""Batch processor worker logic."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from .metrics import PartialStats
from .parser import parse_log_line


def process_batch(batch: Iterable[str], status_code: int = 500, slow_threshold: int = 200) -> PartialStats:
    """Process one batch and return partial counters.

    This function is pickle-friendly and designed for ProcessPoolExecutor workers.
    """

    stats = PartialStats()
    status_counter: Counter[str] = Counter()
    slow_counter: Counter[str] = Counter()

    for line in batch:
        stats.total_lines += 1
        parsed = parse_log_line(line)
        if parsed is None:
            stats.bad_lines += 1
            continue

        url, status, response_time = parsed

        if status == status_code:
            stats.total_500 += 1
            status_counter[url] += 1

        if response_time > slow_threshold:
            stats.total_slow += 1
            slow_counter[url] += 1

    stats.status_by_url = dict(status_counter)
    stats.slow_by_url = dict(slow_counter)
    return stats
