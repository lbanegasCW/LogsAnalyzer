"""Formularios usados por las vistas del dashboard."""

from __future__ import annotations

import os

from django import forms

from .models import ProcessingRun


class ProcessingRunForm(forms.ModelForm):
    """Formulario para crear una nueva ejecución de procesamiento."""

    profile = forms.BooleanField(required=False, label="Activar profiling")

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
        labels = {
            "input_path": "Ruta al archivo",
            "uploaded_file": "Subir archivo",
            "batch_size": "Tamaño de lote",
            "slow_threshold": "Umbral de lentitud (ms)",
            "status_code": "Código de estado",
            "workers": "Cantidad de workers",
        }

    def __init__(self, *args, **kwargs):
        """Configura valores por defecto alineados con la CLI."""

        super().__init__(*args, **kwargs)
        self.fields["batch_size"].initial = 10_000
        self.fields["slow_threshold"].initial = 200
        self.fields["status_code"].initial = 500
        self.fields["workers"].initial = os.cpu_count() or 1

    def clean(self) -> dict:
        """Valida la consistencia de la fuente de entrada."""

        cleaned = super().clean()
        input_path = cleaned.get("input_path")
        uploaded_file = cleaned.get("uploaded_file")

        if not input_path and not uploaded_file:
            raise forms.ValidationError("Debe indicar una ruta de archivo o subir uno pequeño.")

        if input_path:
            if not os.path.exists(input_path):
                raise forms.ValidationError("La ruta indicada no existe.")
            if not os.path.isfile(input_path):
                raise forms.ValidationError("La ruta indicada debe ser un archivo regular.")

        return cleaned
