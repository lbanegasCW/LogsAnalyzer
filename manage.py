#!/usr/bin/env python
"""Utilidad administrativa de Django para el dashboard web de logproc."""

import os
import sys


def main() -> None:
    """Ejecuta tareas administrativas."""

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logproc_web.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
