"""Formularios usados por las vistas del dashboard."""

from __future__ import annotations

import os

from django import forms

from .models import ProcessingRun


class ProcessingRunForm(forms.ModelForm):
    """Formulario para crear una nueva ejecución de procesamiento."""

    profile = forms.BooleanField(required=False, label="Habilitar profiling (cProfile)")

    class Meta:
        model = ProcessingRun
        fields = [
            "input_path",
            "uploaded_file",
            "batch_size",
            "slow_threshold",
            "status_code",
            "workers",
            "profile",
        ]

    def __init__(self, *args, **kwargs):
        """Define valores iniciales con paridad respecto de CLI."""

        super().__init__(*args, **kwargs)
        self.fields["batch_size"].initial = 10_000
        self.fields["slow_threshold"].initial = 200
        self.fields["status_code"].initial = 500
        self.fields["workers"].initial = os.cpu_count() or 1

        self.fields["input_path"].label = "Ruta del archivo de entrada"
        self.fields["uploaded_file"].label = "Archivo subido"
        self.fields["batch_size"].label = "Tamaño de lote"
        self.fields["slow_threshold"].label = "Umbral de lentitud (ms)"
        self.fields["status_code"].label = "Código de estado"
        self.fields["workers"].label = "Cantidad de procesos worker"

    def clean(self) -> dict:
        """Valida la consistencia entre fuente de archivo y ruta."""

        cleaned = super().clean()
        input_path = cleaned.get("input_path")
        uploaded_file = cleaned.get("uploaded_file")

        if not input_path and not uploaded_file:
            raise forms.ValidationError("Debe indicar una ruta de entrada o subir un archivo pequeño.")

        if input_path:
            if not os.path.exists(input_path):
                raise forms.ValidationError("La ruta de entrada no existe.")
            if not os.path.isfile(input_path):
                raise forms.ValidationError("La ruta de entrada debe ser un archivo regular.")

        return cleaned
