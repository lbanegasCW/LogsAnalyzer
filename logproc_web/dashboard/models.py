"""Modelos de base de datos para ejecuciones de procesamiento."""

from __future__ import annotations

from django.db import models


class ProcessingRun(models.Model):
    """Ejecución persistida de un trabajo de procesamiento de logs."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        RUNNING = "RUNNING", "En ejecución"
        DONE = "DONE", "Finalizada"
        FAILED = "FAILED", "Fallida"

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)

    input_path = models.CharField(max_length=1000)
    uploaded_file = models.FileField(upload_to="uploads/", null=True, blank=True)

    batch_size = models.PositiveIntegerField(default=10_000)
    slow_threshold = models.PositiveIntegerField(default=200)
    status_code = models.PositiveIntegerField(default=500)
    workers = models.PositiveIntegerField(default=1)
    profile = models.BooleanField(default=False)

    total_lines = models.BigIntegerField(default=0)
    bad_lines = models.BigIntegerField(default=0)
    total_500 = models.BigIntegerField(default=0)
    total_slow = models.BigIntegerField(default=0)

    top_url_500 = models.CharField(max_length=2000, null=True, blank=True)
    top_url_500_count = models.BigIntegerField(default=0)
    top_url_slow = models.CharField(max_length=2000, null=True, blank=True)
    top_url_slow_count = models.BigIntegerField(default=0)

    duration_seconds = models.FloatField(default=0.0)
    metrics_json = models.JSONField(default=dict, blank=True)
    profile_stats_path = models.CharField(max_length=1000, null=True, blank=True)
    error_message = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Devuelve una descripción legible para humanos."""

        return f"Ejecución #{self.pk} - {self.status}"
