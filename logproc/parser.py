"""Parsing helpers for access-log lines.

The parser is pure and stateless to remain process-safe and testable.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple

ParsedLine = Tuple[str, int, int]

_LOG_RE = re.compile(
    r'^(?P<ip>\S+)\s+-\s+-\s+\[(?P<date>[^\]]+)\]\s+"(?P<method>[A-Z]+)\s+(?P<url>\S+)"\s+(?P<status>\d{3})\s+(?P<response_time>\d+)$'
)


def parse_line(line: str) -> Optional[ParsedLine]:
    """Parse a raw line into normalized fields.

    Args:
        line: Raw log line.

    Returns:
        Tuple ``(url, status_code, response_time_ms)`` when parsing succeeds,
        otherwise ``None`` for malformed lines.

    Complexity:
        ``O(k)`` where ``k`` is line length.
    """

    match = _LOG_RE.match(line.strip())
    if not match:
        return None

    groups = match.groupdict()
    return groups["url"], int(groups["status"]), int(groups["response_time"])


def parse_log_line(line: str) -> Optional[ParsedLine]:
    """Backward-compatible alias for previous public parser name."""

    return parse_line(line)
