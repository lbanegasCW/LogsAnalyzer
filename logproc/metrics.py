"""Estructuras de métricas y utilidades para el procesamiento de logs.

Este módulo centraliza contenedores casi inmutables usados por las interfaces
CLI y web. Todo el procesamiento pesado mantiene solo contadores agregados para
preservar un uso de memoria acotado.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, Optional, Sequence, Tuple


@dataclass(slots=True)
class PartialStats:
    """Contadores locales de un worker para un lote procesado.

    Attributes:
        total_lines: Cantidad de líneas vistas en el lote.
        bad_lines: Cantidad de líneas malformadas en el lote.
        total_status: Cantidad de líneas que matchean el código objetivo.
        total_slow: Cantidad de líneas con latencia por encima del umbral.
        status_by_url: Frecuencias por URL para el código objetivo.
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
    """Métricas finales agregadas para una corrida completa de log.

    Attributes:
        total_lines: Total de líneas procesadas.
        bad_lines: Total de líneas malformadas.
        total_status: Total de entradas que cumplen ``status_code``.
        total_slow: Total de entradas por encima de ``slow_threshold``.
        top_url_status: URL con mayor ocurrencia del estado objetivo.
        top_url_slow: URL con mayor ocurrencia de lentitud.
        top_10_status: Top 10 URLs para el estado objetivo.
        top_10_slow: Top 10 URLs para respuestas lentas.
        elapsed_seconds: Duración total del procesamiento en segundos.
        status_code: Primer código de estado usado para filtrar.
        status_codes: Códigos de estado usados para filtrar.
        slow_threshold: Umbral de lentitud en milisegundos.
        workers: Cantidad de workers usados.
        profile_stats_path: Ruta al archivo de cProfile, cuando corresponde.
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
    status_codes: Sequence[int]
    slow_threshold: int
    workers: int
    profile_stats_path: Optional[str] = None

    def to_dict(self) -> dict:
        """Devuelve una representación serializable a JSON."""

        return asdict(self)


def top_url(counts: Dict[str, int]) -> Tuple[Optional[str], int]:
    """Devuelve la URL con mayor frecuencia.

    Parámetros:
        counts: Mapeo ``url -> conteo``.

    Retorna:
        Tupla ``(url, conteo)``. Si ``counts`` está vacío, devuelve ``(None, 0)``.
    """

    if not counts:
        return None, 0
    return max(counts.items(), key=lambda item: item[1])


def top_n_urls(counts: Dict[str, int], limit: int = 10) -> Sequence[Tuple[str, int]]:
    """Devuelve el top-N de URLs ordenado por frecuencia descendente.

    Parámetros:
        counts: Mapeo ``url -> conteo``.
        limit: Cantidad máxima de pares a devolver.

    Retorna:
        Lista de pares ``(url, conteo)``.

    Complejidad:
        Ejecuta en ``O(m log m)`` sobre ``m`` URLs únicas.
    """

    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]
