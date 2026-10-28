from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("ranking/", views.ranking, name="ranking"),
    path("estado/", views.live_state, name="live_state"),
]
