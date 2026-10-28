"""
Archivos estáticos (CSS, JS, imágenes del sitio) servidos directamente desde static/.

No depende de collectstatic: basta con que el código nuevo llegue al servidor y el
sitio se reinicie. Cada enlace lleva ?v=<huella del archivo>, así el navegador baja
la versión nueva apenas el archivo cambia y, mientras no cambie, usa la guardada.
"""
import hashlib
from functools import lru_cache

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import StaticFilesStorage


def _huella(name):
    path = finders.find(name)
    if not path:
        return ""
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:10]


_huella_guardada = lru_cache(maxsize=None)(_huella)


class VersionedStaticFilesStorage(StaticFilesStorage):
    def url(self, name):
        url = super().url(name)
        # En desarrollo los archivos cambian sin reiniciar: se recalcula cada vez.
        huella = _huella(name) if settings.DEBUG else _huella_guardada(name)
        return f"{url}?v={huella}" if huella else url
