"""Simple background job runner for development environments.

For production deployments, use a robust queue system (Celery/RQ/Arq) with external
workers and retries. This in-process thread runner is intentionally lightweight for
local and practical usage.
"""

from __future__ import annotations

import threading
from pathlib import Path

from django.utils import timezone

from logproc.api import process_log

from .models import ProcessingRun


def _resolve_input_path(run: ProcessingRun) -> str:
    """Resolve effective input path from explicit path or uploaded file."""

    if run.input_path:
        return run.input_path
    if run.uploaded_file:
        return run.uploaded_file.path
    raise ValueError("Run without input source")


def _execute_run(run_id: int) -> None:
    """Execute a run and persist final status/metrics."""

    run = ProcessingRun.objects.get(pk=run_id)
    run.status = ProcessingRun.Status.RUNNING
    run.started_at = timezone.now()
    run.error_message = ""
    run.save(update_fields=["status", "started_at", "error_message"])

    try:
        input_path = _resolve_input_path(run)
        stats_dir = Path("profile_stats")
        stats_dir.mkdir(exist_ok=True)
        profile_stats_path = str(stats_dir / f"run_{run.pk}.stats") if run.profile else "profile.stats"

        result = process_log(
            input_path=input_path,
            batch_size=run.batch_size,
            slow_threshold=run.slow_threshold,
            status_code=run.status_code,
            workers=run.workers,
            profile=run.profile,
            profile_stats_path=profile_stats_path,
        )

        run.total_lines = result.total_lines
        run.bad_lines = result.bad_lines
        run.total_500 = result.total_status
        run.total_slow = result.total_slow
        run.top_url_500 = result.top_url_status[0]
        run.top_url_500_count = result.top_url_status[1]
        run.top_url_slow = result.top_url_slow[0]
        run.top_url_slow_count = result.top_url_slow[1]
        run.duration_seconds = result.elapsed_seconds
        run.metrics_json = {
            "top_10_status": list(result.top_10_status),
            "top_10_slow": list(result.top_10_slow),
        }
        run.profile_stats_path = result.profile_stats_path
        run.status = ProcessingRun.Status.DONE
    except Exception as exc:  # noqa: BLE001
        run.status = ProcessingRun.Status.FAILED
        run.error_message = str(exc)
    finally:
        run.finished_at = timezone.now()
        run.save()


def launch_run_in_background(run: ProcessingRun) -> None:
    """Start an asynchronous daemon thread for a processing run."""

    thread = threading.Thread(target=_execute_run, args=(run.pk,), daemon=True)
    thread.start()
