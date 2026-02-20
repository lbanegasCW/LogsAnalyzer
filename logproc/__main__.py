"""Punto de entrada CLI para procesamiento de logs en streaming y paralelo."""

from __future__ import annotations

import argparse
import os

from .api import process_log
from .metrics import ProcessingResult


def build_parser() -> argparse.ArgumentParser:
    """Construye y devuelve el parser de argumentos de la CLI."""

    parser = argparse.ArgumentParser(description="Procesador eficiente de logs en streaming")
    parser.add_argument("--input", required=True, help="Ruta al archivo de logs")
    parser.add_argument("--batch-size", type=int, default=10_000, help="Tamaño de lote (por defecto: 10000)")
    parser.add_argument("--slow-threshold", type=int, default=200, help="Umbral de request lenta en ms")
    parser.add_argument("--status", type=int, default=500, help="Código de estado a contabilizar")
    parser.add_argument(
        "--workers",
        type=int,
        default=os.cpu_count() or 1,
        help="Número de workers (por defecto: cpu_count)",
    )
    parser.add_argument("--json-out", help="Ruta opcional para exportar resumen en JSON")
    parser.add_argument("--profile", action="store_true", help="Ejecuta bajo cProfile")
    parser.add_argument(
        "--profile-stats-path",
        default="profile.stats",
        help="Archivo de salida para estadísticas de cProfile",
    )
    return parser


def print_summary(result: ProcessingResult) -> None:
    """Imprime en stdout el resumen de procesamiento."""

    print("\n=== Resumen de procesamiento ===")
    print(f"Total líneas procesadas: {result.total_lines}")
    print(f"líneas_malformadas: {result.bad_lines}")
    print(f"total_estado({result.status_code}): {result.total_status}")
    print(f"total_lentas: {result.total_slow}")
    print(f"top_estado: {result.top_url_status[0]} ({result.top_url_status[1]})")
    print(f"top_lentas: {result.top_url_slow[0]} ({result.top_url_slow[1]})")
    print(f"tiempo_total: {result.elapsed_seconds:.4f} s")


def main() -> int:
    """Rutina principal de la CLI."""

    args = build_parser().parse_args()
    result = process_log(
        input_path=args.input,
        batch_size=args.batch_size,
        slow_threshold=args.slow_threshold,
        status_code=args.status,
        workers=args.workers,
        profile=args.profile,
        json_out_path=args.json_out,
        profile_stats_path=args.profile_stats_path,
    )

    print_summary(result)
    if args.json_out:
        print(f"Resumen JSON exportado en: {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
