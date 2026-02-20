"""Utilidades de parseo para líneas de access-log.

El parser es puro y sin estado para mantenerse seguro en multiproceso y testeable.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple

ParsedLine = Tuple[str, int, int]

_LOG_RE = re.compile(
    r'^(?P<ip>\S+)\s+-\s+-\s+\[(?P<date>[^\]]+)\]\s+"(?P<method>[A-Z]+)\s+(?P<url>\S+)"\s+(?P<status>\d{3})\s+(?P<response_time>\d+)$'
)


def parse_line(line: str) -> Optional[ParsedLine]:
    """Parsea una línea cruda en campos normalizados.

    Args:
        line: Línea cruda del log.

    Returns:
        Tupla ``(url, status_code, response_time_ms)`` cuando el parseo es
        exitoso; en caso contrario ``None`` para líneas malformadas.

    Complejidad:
        ``O(k)`` donde ``k`` es el largo de la línea.
    """

    match = _LOG_RE.match(line.strip())
    if not match:
        return None

    groups = match.groupdict()
    return groups["url"], int(groups["status"]), int(groups["response_time"])


def parse_log_line(line: str) -> Optional[ParsedLine]:
    """Alias retrocompatible para el nombre público anterior del parser."""

    return parse_line(line)
