"""Streaming readers for very large log files."""

from __future__ import annotations

from typing import Generator, List


def read_batches(path: str, batch_size: int = 10_000) -> Generator[List[str], None, None]:
    """Yield fixed-size batches from a text file.

    Args:
        path: Input file path.
        batch_size: Number of lines per yielded batch.

    Yields:
        Lists of raw lines, except the last batch which may be smaller.

    Raises:
        ValueError: If ``batch_size <= 0``.
        OSError: If file cannot be opened/read.

    Performance:
        - Time: ``O(n)`` over number of lines.
        - Memory: ``O(batch_size * avg_line_size)``.
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")

    batch: List[str] = []
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            batch.append(line)
            if len(batch) == batch_size:
                yield batch
                batch = []

    if batch:
        yield batch
