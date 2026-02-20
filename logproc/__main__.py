"""CLI entrypoint for streaming, parallel log processing."""

from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from time import perf_counter
from typing import Iterable, Optional

from .metrics import PartialStats, ProcessingResult, top_url
from .profiling import run_with_profile
from .reader import read_batches
from .reducer import merge_partials
from .worker import process_batch


def process_file(
    input_path: str,
    batch_size: int = 10_000,
    slow_threshold: int = 200,
    status_code: int = 500,
    workers: Optional[int] = None,
) -> ProcessingResult:
    """Process a log file and return merged metrics."""

    start = perf_counter()
    workers = workers or (os.cpu_count() or 1)

    batch_iter = read_batches(input_path, batch_size=batch_size)
    worker_func = partial(process_batch, status_code=status_code, slow_threshold=slow_threshold)

    partials: Iterable[PartialStats]
    if workers == 1:
        partials = (worker_func(batch) for batch in batch_iter)
        merged = merge_partials(partials)
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            # map(...) preserves streaming behavior and avoids accumulating futures.
            partials = executor.map(worker_func, batch_iter)
            merged = merge_partials(partials)

    elapsed = perf_counter() - start
    return ProcessingResult(
        total_lines=merged.total_lines,
        bad_lines=merged.bad_lines,
        total_500=merged.total_500,
        total_slow=merged.total_slow,
        url_mas_500=top_url(merged.status_by_url),
        url_mas_slow=top_url(merged.slow_by_url),
        elapsed_seconds=elapsed,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Procesador eficiente de logs en streaming")
    parser.add_argument("--input", required=True, help="Ruta al archivo de logs")
    parser.add_argument("--batch-size", type=int, default=10_000, help="Tamaño de lote (default: 10000)")
    parser.add_argument("--slow-threshold", type=int, default=200, help="Umbral de request lenta en ms")
    parser.add_argument("--status", type=int, default=500, help="Código de estado a contabilizar")
    parser.add_argument(
        "--workers",
        type=int,
        default=os.cpu_count() or 1,
        help="Número de workers (default: cpu_count)",
    )
    parser.add_argument("--json-out", help="Ruta opcional para exportar resumen en JSON")
    parser.add_argument("--profile", action="store_true", help="Ejecuta bajo cProfile")
    parser.add_argument(
        "--profile-stats-path",
        default="profile.stats",
        help="Archivo de salida para stats de cProfile",
    )
    return parser


def print_summary(result: ProcessingResult) -> None:
    """Pretty summary to stdout."""

    print("\n=== Resumen de procesamiento ===")
    print(f"Total líneas procesadas: {result.total_lines}")
    print(f"bad_lines: {result.bad_lines}")
    print(f"total_500: {result.total_500}")
    print(f"total_slow: {result.total_slow}")
    print(f"url_mas_500: {result.url_mas_500[0]} ({result.url_mas_500[1]})")
    print(f"url_mas_slow: {result.url_mas_slow[0]} ({result.url_mas_slow[1]})")
    print(f"tiempo total: {result.elapsed_seconds:.4f} s")


def main() -> int:
    args = build_parser().parse_args()

    run = partial(
        process_file,
        input_path=args.input,
        batch_size=args.batch_size,
        slow_threshold=args.slow_threshold,
        status_code=args.status,
        workers=args.workers,
    )

    result = run_with_profile(run, stats_path=args.profile_stats_path) if args.profile else run()

    print_summary(result)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2, ensure_ascii=False)
        print(f"Resumen JSON exportado en: {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
