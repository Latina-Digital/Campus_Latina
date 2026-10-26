from django.conf import settings
from django.contrib import admin
from django.templatetags.static import static
from django.shortcuts import redirect
from django.urls import include, path, re_path

from apps.core.views import serve_media

admin.site.site_header = "Campus Latina · Administración avanzada"
admin.site.site_title = "Campus Latina"
admin.site.index_title = "Datos de la plataforma"


def favicon(request):
    # La ruta se calcula al pedirla: al importar este archivo collectstatic puede no haberse ejecutado aún.
    return redirect(static("img/favicon.ico"))

urlpatterns = [
    # Algunos navegadores piden /favicon.ico aunque la página declare otro ícono.
    path("favicon.ico", favicon),
    path("", include("apps.core.urls")),
    path("cuenta/", include("apps.accounts.urls")),
    path("aprender/", include("apps.courses.urls")),
    path("evaluaciones/", include("apps.assessments.urls")),
    path("certificados/", include("apps.certificates.urls")),
    path("productos/", include("apps.catalog.urls")),
    path("panel/", include("apps.panel.urls")),
    path("django-admin/", admin.site.urls),
]

if settings.SERVE_MEDIA:
    urlpatterns += [re_path(r"^media/(?P<path>.+)$", serve_media, name="media")]
handler404 = "apps.core.views.error_404"
