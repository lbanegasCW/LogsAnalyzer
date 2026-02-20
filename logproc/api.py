"""Public stable API to process logs from any interface (CLI, web, scripts)."""

from __future__ import annotations

import json
import os
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from time import perf_counter
from typing import Iterable, Optional

from .metrics import PartialStats, ProcessingResult, top_n_urls, top_url
from .profiling import run_with_profile
from .reader import read_batches
from .reducer import merge_partials
from .worker import process_batch


def process_log(
    input_path: str,
    batch_size: int = 10_000,
    slow_threshold: int = 200,
    status_code: int = 500,
    workers: Optional[int] = None,
    profile: bool = False,
    json_out_path: Optional[str] = None,
    profile_stats_path: str = "profile.stats",
) -> ProcessingResult:
    """Process a large log file using streaming and optional multi-processing.

    Args:
        input_path: Path to input log file.
        batch_size: Number of lines per batch.
        slow_threshold: Slow request threshold in milliseconds.
        status_code: HTTP status code to aggregate.
        workers: Worker count. ``None`` defaults to ``os.cpu_count()``.
        profile: Whether to run processing under cProfile.
        json_out_path: Optional path to dump serialized result.
        profile_stats_path: cProfile stats output path when ``profile=True``.

    Returns:
        A ``ProcessingResult`` dataclass with aggregate metrics and top URLs.

    Raises:
        OSError: If the file cannot be read.
        ValueError: If invalid processing parameters are provided.

    Performance:
        Time complexity is ``O(n)`` over log lines. Memory is bounded by
        ``batch_size`` plus URL aggregate dictionaries.
    """

    worker_count = workers or (os.cpu_count() or 1)

    def _run() -> ProcessingResult:
        start = perf_counter()
        batch_iter = read_batches(input_path, batch_size=batch_size)
        worker_func = partial(process_batch, status_code=status_code, slow_threshold=slow_threshold)

        partials: Iterable[PartialStats]
        if worker_count == 1:
            partials = (worker_func(batch) for batch in batch_iter)
            merged = merge_partials(partials)
        else:
            with ProcessPoolExecutor(max_workers=worker_count) as executor:
                partials = executor.map(worker_func, batch_iter)
                merged = merge_partials(partials)

        elapsed = perf_counter() - start
        return ProcessingResult(
            total_lines=merged.total_lines,
            bad_lines=merged.bad_lines,
            total_status=merged.total_status,
            total_slow=merged.total_slow,
            top_url_status=top_url(merged.status_by_url),
            top_url_slow=top_url(merged.slow_by_url),
            top_10_status=top_n_urls(merged.status_by_url, limit=10),
            top_10_slow=top_n_urls(merged.slow_by_url, limit=10),
            elapsed_seconds=elapsed,
            status_code=status_code,
            slow_threshold=slow_threshold,
            workers=worker_count,
        )

    result = run_with_profile(_run, stats_path=profile_stats_path) if profile else _run()
    if profile:
        result.profile_stats_path = profile_stats_path

    if json_out_path:
        with open(json_out_path, "w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2, ensure_ascii=False)

    return result
