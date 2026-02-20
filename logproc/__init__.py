"""Paquete logproc.

Núcleo reutilizable y eficiente para procesar logs desde CLI, web o scripts.
"""

from .api import process_log
from .metrics import ProcessingResult

__all__ = ["process_log", "ProcessingResult"]
