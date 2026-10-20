"""
Servidor de producción (Waitress).

Detrás de IIS lo arranca HttpPlatformHandler (ver deploy/web.config), que le
pasa el puerto en la variable PORT y escucha solo en 127.0.0.1.

Uso manual:
    .venv\\Scripts\\python manage.py collectstatic --noinput
    .venv\\Scripts\\python serve.py
"""
import os

from waitress import serve

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.conf import settings  # noqa: E402

from config.wsgi import application  # noqa: E402

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print(f"Campus Latina sirviendo en http://{host}:{port}", flush=True)
    serve(
        application,
        host=host,
        port=port,
        threads=int(os.getenv("THREADS", "8")),
        # IIS termina el HTTPS: así Django genera enlaces y cookies seguras.
        url_scheme="https" if settings.HTTPS else "http",
        # IIS reenvía la IP real del visitante en X-Forwarded-For.
        trusted_proxy="127.0.0.1",
        trusted_proxy_count=1,
        trusted_proxy_headers={"x-forwarded-for"},
        clear_untrusted_proxy_headers=True,
        max_request_body_size=1024 * 1024 * 1024,  # videos de hasta 1 GB
        channel_timeout=300,
        ident="CampusLatina",
    )
