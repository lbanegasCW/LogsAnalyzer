"""Configuración de URLs de ``logproc_web``."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("logproc_web.dashboard.urls")),
]
