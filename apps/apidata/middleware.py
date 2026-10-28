"""
Mantiene la copia local al día con la API.

Cada campus (el del servidor, el de una laptop de pruebas...) tiene su propia copia
local. Los cambios que hace uno llegan a la API al instante, pero los demás solo los
ven cuando vuelven a leerla. Por eso, cuando la copia tiene más de
CAMPUS_API_REFRESH_SECONDS, la siguiente visita la recarga en segundo plano: esa
visita no espera, y las siguientes ya ven los datos nuevos.
"""
import logging
import threading
import time

from django.conf import settings
from django.db import connection

from . import client, mirror

logger = logging.getLogger("apps.apidata")
_recargando = threading.Lock()


def refresh_if_stale():
    intervalo = settings.CAMPUS_API_REFRESH_SECONDS
    if not client.enabled() or not intervalo or time.monotonic() - mirror.ultima_carga < intervalo:
        return
    if _recargando.acquire(blocking=False):
        threading.Thread(target=_recargar, name="recarga-api", daemon=True).start()


def _recargar():
    try:
        mirror.load_all()
    except Exception:
        # Se reintenta en el siguiente intervalo; mientras tanto sigue la copia anterior.
        mirror.ultima_carga = time.monotonic()
        logger.exception("No se pudo actualizar la copia local desde la API.")
    finally:
        connection.close()
        _recargando.release()


class ApiRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        refresh_if_stale()
        return self.get_response(request)
