from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("ingresar/", views.LoginView.as_view(), name="login"),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("perfil/", views.profile, name="profile"),
    path("perfil/<str:username>/", views.profile, name="public_profile"),
    path("contrasena/", views.PasswordChangeView.as_view(), name="password_change"),
    path("mi-equipo/", views.team, name="team"),
]
