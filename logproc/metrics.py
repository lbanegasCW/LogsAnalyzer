"""Estructuras de datos y utilidades de métricas para el procesamiento de logs.

Este módulo centraliza contenedores casi inmutables usados por CLI e interfaz web.
El procesamiento pesado conserva solo contadores agregados para mantener memoria acotada.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, Optional, Sequence, Tuple


@dataclass(slots=True)
class PartialStats:
    """Contadores locales de worker para un único lote procesado.

    Attributes:
        total_lines: Cantidad de líneas vistas en el lote.
        bad_lines: Cantidad de líneas malformadas en el lote.
        total_status: Cantidad de líneas que coinciden con el estado objetivo.
        total_slow: Cantidad de líneas con tiempo de respuesta sobre el umbral.
        status_by_url: Frecuencias por URL para el código de estado objetivo.
        slow_by_url: Frecuencias por URL para respuestas lentas.
    """

    total_lines: int = 0
    bad_lines: int = 0
    total_status: int = 0
    total_slow: int = 0
    status_by_url: Dict[str, int] = field(default_factory=dict)
    slow_by_url: Dict[str, int] = field(default_factory=dict)


@dataclass(slots=True)
class ProcessingResult:
    """Métricas finales agregadas para una ejecución completa de log.

    Attributes:
        total_lines: Cantidad total de líneas procesadas.
        bad_lines: Cantidad total de líneas malformadas.
        total_status: Total de entradas que coinciden con ``status_code``.
        total_slow: Total de entradas por encima de ``slow_threshold``.
        top_url_status: URL con más ocurrencias del estado objetivo.
        top_url_slow: URL con más ocurrencias lentas.
        top_10_status: Top 10 URLs para el estado objetivo.
        top_10_slow: Top 10 URLs para respuestas lentas.
        elapsed_seconds: Duración total del procesamiento en segundos.
        status_code: Código de estado usado para el filtrado.
        slow_threshold: Umbral de lentitud en milisegundos.
        workers: Cantidad de procesos worker utilizados.
        profile_stats_path: Ruta al archivo de cProfile, si hubo profiling.
    """

    total_lines: int
    bad_lines: int
    total_status: int
    total_slow: int
    top_url_status: Tuple[Optional[str], int]
    top_url_slow: Tuple[Optional[str], int]
    top_10_status: Sequence[Tuple[str, int]]
    top_10_slow: Sequence[Tuple[str, int]]
    elapsed_seconds: float
    status_code: int
    slow_threshold: int
    workers: int
    profile_stats_path: Optional[str] = None

    def to_dict(self) -> dict:
        """Devuelve una representación en diccionario serializable a JSON."""

        return asdict(self)


def top_url(counts: Dict[str, int]) -> Tuple[Optional[str], int]:
    """Devuelve la URL con mayor frecuencia.

    Args:
        counts: Mapeo ``url -> cantidad``.

    Returns:
        Tupla ``(url, cantidad)``. Si ``counts`` está vacío, devuelve ``(None, 0)``.
    """

    if not counts:
        return None, 0
    return max(counts.items(), key=lambda item: item[1])


def top_n_urls(counts: Dict[str, int], limit: int = 10) -> Sequence[Tuple[str, int]]:
    """Devuelve el top-N de URLs ordenado por frecuencia descendente.

    Args:
        counts: Mapeo ``url -> cantidad``.
        limit: Cantidad máxima de pares devueltos.

    Returns:
        Una lista de pares ``(url, cantidad)``.

    Complejidad:
        Ejecuta en ``O(m log m)`` sobre la cantidad de URLs únicas ``m``.
    """

    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]
