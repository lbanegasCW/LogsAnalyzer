"""Registro de modelos del dashboard en el admin."""

from django.contrib import admin

from .models import ProcessingRun


@admin.register(ProcessingRun)
class ProcessingRunAdmin(admin.ModelAdmin):
    """Vista básica de administración para ``ProcessingRun``."""

    list_display = ("id", "created_at", "status", "input_path", "total_lines", "duration_seconds")
    list_filter = ("status", "created_at")
    search_fields = ("input_path", "error_message")
