"""Lectores en streaming para archivos de log muy grandes."""

from __future__ import annotations

from typing import Generator, List


def read_batches(path: str, batch_size: int = 10_000) -> Generator[List[str], None, None]:
    """Entrega lotes de tamaño fijo desde un archivo de texto.

    Args:
        path: Ruta del archivo de entrada.
        batch_size: Cantidad de líneas por lote entregado.

    Yields:
        Listas de líneas crudas, salvo el último lote que puede ser más pequeño.

    Raises:
        ValueError: Si ``batch_size <= 0``.
        OSError: Si no se puede abrir o leer el archivo.

    Rendimiento:
        - Tiempo: ``O(n)`` sobre la cantidad de líneas.
        - Memoria: ``O(batch_size * tamaño_promedio_línea)``.
    """

    if batch_size <= 0:
        raise ValueError("batch_size debe ser > 0")

    batch: List[str] = []
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            batch.append(line)
            if len(batch) == batch_size:
                yield batch
                batch = []

    if batch:
        yield batch
