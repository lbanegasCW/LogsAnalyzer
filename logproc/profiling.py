"""Utilidades para ejecutar funciones bajo cProfile."""

from __future__ import annotations

import cProfile
import pstats
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")


def run_with_profile(func: Callable[[], T], stats_path: str = "profile.stats", top_n: int = 20) -> T:
    """Ejecuta ``func`` bajo cProfile y persiste estadísticas del profiler.

    Parámetros:
        func: Callable sin argumentos a ejecutar.
        stats_path: Ruta destino para estadísticas de profile.
        top_n: Cantidad de hotspots a imprimir por tiempo acumulado.

    Retorna:
        El valor retornado por ``func``.
    """

    profiler = cProfile.Profile()
    profiler.enable()
    result = func()
    profiler.disable()

    output = Path(stats_path)
    profiler.dump_stats(str(output))

    print(f"\n[profile] Estadísticas guardadas en: {output}")
    pstats.Stats(profiler).sort_stats("cumtime").print_stats(top_n)
    return result
