"""Streaming file reader that yields fixed-size batches."""

from __future__ import annotations

from typing import Generator, List


def read_batches(path: str, batch_size: int = 10_000) -> Generator[List[str], None, None]:
    """Yield log file lines in batches of exactly ``batch_size`` (except last batch).

    The function streams from disk and never loads the full file into memory.
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
