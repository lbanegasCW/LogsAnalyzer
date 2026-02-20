"""API pública y estable para procesar logs desde cualquier interfaz."""

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
    """Procesa un archivo de logs grande con streaming y multiproceso opcional.

    Args:
        input_path: Ruta al archivo de log de entrada.
        batch_size: Cantidad de líneas por lote.
        slow_threshold: Umbral de request lenta en milisegundos.
        status_code: Código de estado HTTP a agregar.
        workers: Cantidad de procesos worker. ``None`` usa ``os.cpu_count()``.
        profile: Indica si se ejecuta el procesamiento bajo cProfile.
        json_out_path: Ruta opcional para guardar el resultado serializado.
        profile_stats_path: Ruta del archivo de estadísticas cuando ``profile=True``.

    Returns:
        Un dataclass ``ProcessingResult`` con métricas agregadas y top de URLs.

    Raises:
        OSError: Si no se puede leer el archivo.
        ValueError: Si se proveen parámetros de procesamiento inválidos.

    Rendimiento:
        La complejidad temporal es ``O(n)`` sobre las líneas del log. La memoria
        está acotada por ``batch_size`` más los diccionarios de agregación por URL.
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
