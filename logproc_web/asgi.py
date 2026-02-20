"""Configuración ASGI para el proyecto logproc_web."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logproc_web.settings")

application = get_asgi_application()
