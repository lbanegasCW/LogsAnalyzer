"""Line parser utilities for access log entries."""

from __future__ import annotations

import re
from typing import Optional, Tuple

# Example line:
# 192.168.0.1 - - [10/Sep/2024:15:03:27] "GET /index.html" 200 125
_LOG_RE = re.compile(
    r'^(?P<ip>\S+)\s+-\s+-\s+\[(?P<date>[^\]]+)\]\s+"(?P<method>[A-Z]+)\s+(?P<url>\S+)"\s+(?P<status>\d{3})\s+(?P<response_time>\d+)$'
)

ParsedLine = Tuple[str, int, int]


def parse_log_line(line: str) -> Optional[ParsedLine]:
    """Parse a log line and return (url, status, response_time_ms).

    Returns None for malformed lines. This function is intentionally pure and
    side-effect free, so workers can call it safely in parallel.
    """

    match = _LOG_RE.match(line.strip())
    if not match:
        return None

    groups = match.groupdict()
    return groups["url"], int(groups["status"]), int(groups["response_time"])
