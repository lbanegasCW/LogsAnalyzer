"""Configuración de la app dashboard."""

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Configuración principal de la app dashboard."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "logproc_web.dashboard"
    verbose_name = "Panel de procesamiento de logs"
