"""cProfile helper utilities for CLI integration."""

from __future__ import annotations

import cProfile
import pstats
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")


def run_with_profile(func: Callable[[], T], stats_path: str = "profile.stats", top_n: int = 20) -> T:
    """Execute ``func`` under cProfile, dump stats file, and print top hotspots."""

    profiler = cProfile.Profile()
    profiler.enable()
    result = func()
    profiler.disable()

    output = Path(stats_path)
    profiler.dump_stats(str(output))

    print(f"\n[profile] Stats guardadas en: {output}")
    pstats.Stats(profiler).sort_stats("cumtime").print_stats(top_n)
    return result
