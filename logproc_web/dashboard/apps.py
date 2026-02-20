"""Configuración de la app de dashboard."""

from django.apps import AppConfig


class panelConfig(AppConfig):
    """Configuración principal de la app panel."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "logproc_web.dashboard"
    verbose_name = "Panel del procesador de logs"
