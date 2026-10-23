"""
Cliente de la API de datos del campus.

    POST {CAMPUS_API_URL}   (api/syspro/campus/datos)
    {"ApiKey": "...", "Accion": "CONSULTAR|CREAR|MODIFICAR|ELIMINAR", "tabla": "Cursos",
     "id": 0, "filtro": "<json>", "datos": "<json>"}

La API ejecuta dbo.spCampus_Datos sobre las tablas dbo.CV_* (ver
deploy/api_campus/01_campus_nuevo.sql) y responde siempre una lista de filas.
Es el único módulo que habla con ella.
"""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger("apps.apidata")


class CampusApiError(Exception):
    """La API rechazó la operación o no se pudo conectar con ella."""


def enabled():
    return bool(settings.CAMPUS_API_URL)


_ultima_url = None  # la que respondió la última vez se prueba primero


def api_urls():
    urls = [settings.CAMPUS_API_URL] if settings.CAMPUS_API_URL else []
    urls += [u for u in settings.CAMPUS_API_URLS if u not in urls]
    if _ultima_url in urls:
        urls.remove(_ultima_url)
        urls.insert(0, _ultima_url)
    return urls


def call(accion, tabla, id=0, filtro=None, datos=None):
    global _ultima_url
    # La API exige "filtro" y "datos" aunque vayan vacíos.
    payload = json.dumps({
        "ApiKey": settings.CAMPUS_API_KEY,
        "Accion": accion,
        "tabla": tabla,
        "id": id or 0,
        "filtro": json.dumps(filtro, ensure_ascii=False) if filtro else "",
        "datos": json.dumps(datos, ensure_ascii=False) if datos is not None else "",
    }, ensure_ascii=False).encode("utf-8")
    errores = []
    for url in api_urls():
        req = urllib.request.Request(
            url, data=payload, method="POST", headers={"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=settings.CAMPUS_API_TIMEOUT) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detalle = _mensaje(exc)
            if exc.code in (400, 401):
                # Error de datos o de API key: otra URL respondería lo mismo.
                raise CampusApiError(f"{accion} {tabla}: {detalle}") from exc
            errores.append(f"{url} -> HTTP {exc.code} {detalle}")
            continue
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            errores.append(f"{url} -> sin conexión ({exc})")
            continue
        _ultima_url = url
        filas = json.loads(body or "[]")
        if not isinstance(filas, list):
            raise CampusApiError(f"{accion} {tabla}: respuesta inesperada de la API.")
        return filas
    for error in errores:
        logger.error("API del campus: %s", error)
    raise CampusApiError("No se pudo conectar con la API del campus. " + "; ".join(errores))


def _mensaje(exc):
    try:
        data = json.loads(exc.read().decode("utf-8") or "{}")
    except ValueError:
        return exc.reason
    return data.get("mensaje") or data.get("title") or data.get("detail") or exc.reason
