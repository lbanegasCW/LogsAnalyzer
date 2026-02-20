"""Rutas de URL del dashboard."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.run_list, name="run_list"),
    path("runs/new/", views.run_create, name="run_create"),
    path("runs/<int:run_id>/", views.run_detail, name="run_detail"),
]
