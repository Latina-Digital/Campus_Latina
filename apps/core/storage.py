"""
Enlaces con versión para que el navegador nunca muestre un archivo viejo.

Archivos estáticos (CSS, JS, imágenes del sitio): se sirven directamente desde static/,
sin depender de collectstatic; basta con que el código nuevo llegue al servidor y el
sitio se reinicie. Archivos subidos (portadas, fotos, videos): el enlace cambia cuando
el archivo se reemplaza. En ambos casos el navegador baja la versión nueva apenas el
archivo cambia y, mientras no cambie, usa la guardada.
"""
import hashlib
from functools import lru_cache

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.core.files.storage import FileSystemStorage


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


class VersionedMediaStorage(FileSystemStorage):
    """Archivos subidos (portadas, fotos, videos): ?v=<fecha de modificación> en cada enlace.

    Si se reemplaza un archivo con el mismo nombre, el enlace cambia y el navegador
    descarga el nuevo en lugar de mostrar el que tenía guardado.
    """

    def url(self, name):
        url = super().url(name)
        try:
            return f"{url}?v={int(self.get_modified_time(name).timestamp())}"
        except OSError:
            return url
