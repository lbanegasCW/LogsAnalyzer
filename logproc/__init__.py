"""logproc package.

Reusable, efficient log processing core designed to be invoked from CLI, web, or scripts.
"""

from .api import process_log
from .metrics import ProcessingResult

__all__ = ["process_log", "ProcessingResult"]
