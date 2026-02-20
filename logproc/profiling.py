"""Utilities to run callables under cProfile."""

from __future__ import annotations

import cProfile
import pstats
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")


def run_with_profile(func: Callable[[], T], stats_path: str = "profile.stats", top_n: int = 20) -> T:
    """Execute ``func`` under cProfile and persist profiler stats.

    Args:
        func: Zero-arg callable to execute.
        stats_path: Destination path for profile stats.
        top_n: Number of hotspots to print by cumulative time.

    Returns:
        The value returned by ``func``.
    """

    profiler = cProfile.Profile()
    profiler.enable()
    result = func()
    profiler.disable()

    output = Path(stats_path)
    profiler.dump_stats(str(output))

    print(f"\n[profile] Stats guardadas en: {output}")
    pstats.Stats(profiler).sort_stats("cumtime").print_stats(top_n)
    return result
