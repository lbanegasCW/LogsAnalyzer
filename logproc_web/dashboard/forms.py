"""Formularios usados por las vistas del dashboard."""

from __future__ import annotations

import os

from django import forms
from django.db import models

from .models import ProcessingRun


class ProcessingRunForm(forms.ModelForm):
    """Formulario para crear una nueva ejecución de procesamiento."""

    class InputMode(models.TextChoices):
        PATH = "path", "Ruta"
        UPLOAD = "upload", "Upload"

    profile = forms.BooleanField(required=False, label="Activar profiling")
    input_mode = forms.ChoiceField(
        label="Fuente de datos",
        choices=InputMode.choices,
        widget=forms.RadioSelect,
        initial=InputMode.PATH,
    )
    status_codes = forms.CharField(
        label="Códigos de estado",
        help_text="Ingresar uno o más códigos separados por coma. Ej: 500,400,200",
    )

    class Meta:
        model = ProcessingRun
        fields = [
            "input_mode",
            "input_path",
            "uploaded_file",
            "batch_size",
            "slow_threshold",
            "status_codes",
            "workers",
            "profile",
        ]
        labels = {
            "input_path": "Ruta al archivo",
            "uploaded_file": "Subir archivo",
            "batch_size": "Tamaño de lote",
            "slow_threshold": "Umbral de lentitud (ms)",
            "workers": "Cantidad de workers",
        }

    def __init__(self, *args, **kwargs):
        """Configura valores por defecto alineados con la CLI."""

        super().__init__(*args, **kwargs)
        self.fields["input_path"].required = False
        self.fields["uploaded_file"].required = False
        self.fields["batch_size"].initial = 10_000
        self.fields["slow_threshold"].initial = 200
        self.fields["status_codes"].initial = "500"
        self.fields["workers"].initial = os.cpu_count() or 1

    def clean_status_codes(self) -> str:
        """Normaliza y valida la lista de códigos HTTP."""

        raw_value = self.cleaned_data.get("status_codes", "")
        tokens = [token.strip() for token in raw_value.split(",") if token.strip()]

        if not tokens:
            raise forms.ValidationError("Debe indicar al menos un código de estado.")

        normalized_codes: list[str] = []
        for token in tokens:
            if not token.isdigit():
                raise forms.ValidationError("Los códigos deben ser numéricos y separados por coma.")
            status_code = int(token)
            if status_code < 100 or status_code > 599:
                raise forms.ValidationError("Cada código debe estar entre 100 y 599.")
            normalized_codes.append(str(status_code))

        unique_sorted = sorted(set(normalized_codes), key=int)
        return ",".join(unique_sorted)

    def clean(self) -> dict:
        """Valida la consistencia de la fuente de entrada."""

        cleaned = super().clean()
        input_mode = cleaned.get("input_mode")
        input_path = (cleaned.get("input_path") or "").strip()
        uploaded_file = cleaned.get("uploaded_file")

        if input_mode == self.InputMode.PATH:
            if not input_path:
                raise forms.ValidationError("Debe indicar una ruta de archivo.")
            if uploaded_file:
                raise forms.ValidationError("Si usa ruta, no debe subir archivo.")
            if not os.path.exists(input_path):
                raise forms.ValidationError("La ruta indicada no existe.")
            if not os.path.isfile(input_path):
                raise forms.ValidationError("La ruta indicada debe ser un archivo regular.")
            cleaned["uploaded_file"] = None
            cleaned["input_path"] = input_path

        if input_mode == self.InputMode.UPLOAD:
            if not uploaded_file:
                raise forms.ValidationError("Debe subir un archivo.")
            if input_path:
                raise forms.ValidationError("Si sube archivo, no debe indicar una ruta.")
            cleaned["input_path"] = ""

        return cleaned

    def save(self, commit: bool = True):
        """Persiste también el primer código para compatibilidad histórica."""

        run = super().save(commit=False)
        parsed_codes = [int(code) for code in run.status_codes.split(",") if code]
        run.status_code = parsed_codes[0]
        if commit:
            run.save()
            self.save_m2m()
        return run
