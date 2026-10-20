from django.urls import path

from . import views

app_name = "assessments"

urlpatterns = [
    path("curso/<slug:slug>/", views.intro, name="intro"),
    path("intento/<int:pk>/", views.take, name="take"),
    path("intento/<int:pk>/guardar/", views.autosave, name="autosave"),
    path("intento/<int:pk>/enviar/", views.submit, name="submit"),
    path("intento/<int:pk>/resultado/", views.result, name="result"),
]
