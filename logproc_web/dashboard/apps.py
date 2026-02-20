"""App configuration for dashboard."""

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Dashboard app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "logproc_web.dashboard"
    verbose_name = "Log Processor Dashboard"
