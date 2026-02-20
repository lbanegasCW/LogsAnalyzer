"""Vistas del dashboard para listar, crear e inspeccionar ejecuciones."""

from __future__ import annotations

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProcessingRunForm
from .job_runner import launch_run_in_background
from .models import ProcessingRun


def run_list(request):
    """Renderiza el listado con filtros opcionales por estado y fecha."""

    runs: QuerySet[ProcessingRun] = ProcessingRun.objects.all()
    status_filter = request.GET.get("status")
    date_filter = request.GET.get("date")

    if status_filter:
        runs = runs.filter(status=status_filter)
    if date_filter:
        runs = runs.filter(created_at__date=date_filter)

    return render(
        request,
        "dashboard/run_list.html",
        {
            "runs": runs,
            "status_filter": status_filter or "",
            "date_filter": date_filter or "",
            "status_choices": ProcessingRun.Status.choices,
        },
    )


def run_create(request):
    """Renderiza el alta y agenda procesamiento asíncrono."""

    if request.method == "POST":
        form = ProcessingRunForm(request.POST, request.FILES)
        if form.is_valid():
            run = form.save(commit=False)
            if run.uploaded_file and not run.input_path:
                # Solo para pruebas chicas; para logs grandes se recomienda path.
                run.input_path = ""
            run.status = ProcessingRun.Status.PENDING
            run.save()
            launch_run_in_background(run)
            return redirect("run_detail", run_id=run.pk)
    else:
        form = ProcessingRunForm()

    return render(request, "dashboard/run_form.html", {"form": form})


def run_detail(request, run_id: int):
    """Muestra detalles de la ejecución, métricas y datos para gráficos/tablas."""

    run = get_object_or_404(ProcessingRun, pk=run_id)
    top_10_status = run.metrics_json.get("top_10_status", []) if run.metrics_json else []
    top_10_slow = run.metrics_json.get("top_10_slow", []) if run.metrics_json else []

    return render(
        request,
        "dashboard/run_detail.html",
        {
            "run": run,
            "top_10_status": top_10_status,
            "top_10_slow": top_10_slow,
        },
    )
