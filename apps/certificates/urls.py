from django.urls import path

from . import views

app_name = "certificates"

urlpatterns = [
    path("", views.my_certificates, name="list"),
    path("verificar/", views.verify, name="verify"),
    path("verificar/<str:code>/", views.verify, name="verify_code"),
    path("<str:code>/", views.detail, name="detail"),
    path("<str:code>/pdf/", views.pdf, name="pdf"),
]
