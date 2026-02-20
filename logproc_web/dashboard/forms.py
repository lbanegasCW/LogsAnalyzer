"""Forms used by dashboard views."""

from __future__ import annotations

import os

from django import forms

from .models import ProcessingRun


class ProcessingRunForm(forms.ModelForm):
    """Form to create a new processing run."""

    profile = forms.BooleanField(required=False)

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
        """Set defaults tuned for CLI parity."""

        super().__init__(*args, **kwargs)
        self.fields["batch_size"].initial = 10_000
        self.fields["slow_threshold"].initial = 200
        self.fields["status_code"].initial = 500
        self.fields["workers"].initial = os.cpu_count() or 1

    def clean(self) -> dict:
        """Validate file source and path consistency."""

        cleaned = super().clean()
        input_path = cleaned.get("input_path")
        uploaded_file = cleaned.get("uploaded_file")

        if not input_path and not uploaded_file:
            raise forms.ValidationError("Debe indicar un input_path o subir un archivo pequeño.")

        if input_path:
            if not os.path.exists(input_path):
                raise forms.ValidationError("input_path no existe.")
            if not os.path.isfile(input_path):
                raise forms.ValidationError("input_path debe ser un archivo regular.")

        return cleaned
