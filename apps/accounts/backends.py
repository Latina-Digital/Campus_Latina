"""
Autenticación contra la API corporativa de Syspro.

    POST {SYSPRO_API_URL}
    {"user": "...", "pass": "...", "ApiKey": "..."}

Respuestas observadas:
    200 + lista con datos del usuario -> credenciales válidas
    200 + []                          -> usuario o contraseña incorrectos
    401                               -> ApiKey inválida
    404 / sin conexión                -> se prueba la siguiente URL configurada

La API key vive solo en el servidor (archivo .env), nunca en el navegador.
Si las credenciales son válidas se crea o actualiza el usuario en la copia local
del campus (no hay tabla de usuarios en la API: nombre, rol y supervisor se copian
en sus inscripciones).
"""
import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

logger = logging.getLogger("apps.accounts")

# Nombres de campo aceptados (la API puede cambiar mayúsculas o idioma).
FIELD_ALIASES = {
    "user": ("user", "usuario", "username", "login", "codigo"),
    "name": ("nombre", "name", "nombres", "nombre_completo", "fullname"),
    "role": ("rol", "role", "cargo", "perfil"),
    "supervisor": ("supervisor", "jefe", "nombre_supervisor"),
    "email": ("email", "correo", "mail"),
    "area": ("area", "zona", "departamento"),
    "city": ("ciudad", "city", "sucursal"),
}


def split_name(full_name):
    """Syspro entrega 'APELLIDO1 APELLIDO2 NOMBRE1 NOMBRE2'."""
    parts = full_name.title().split()
    if len(parts) >= 4:
        return " ".join(parts[2:]), " ".join(parts[:2])
    if len(parts) == 3:
        return parts[2], " ".join(parts[:2])
    if len(parts) == 2:
        return parts[1], parts[0]
    return full_name.title(), ""


def map_role(raw):
    text = (raw or "").strip().lower()
    if "admin" in text:
        return "admin"
    if "nacional" in text:
        return "jefe_nacional"
    if "jefe" in text or "gerente" in text:
        return "jefe_ventas"
    if "super" in text:
        return "supervisor"
    return "ejecutivo"


def pick(row, key):
    lowered = {str(k).lower(): v for k, v in row.items()}
    for alias in FIELD_ALIASES[key]:
        value = lowered.get(alias)
        if value not in (None, ""):
            return str(value).strip()
    return ""


def extract_rows(data):
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    if isinstance(data, dict):
        for key in ("data", "result", "results", "users", "usuarios", "value"):
            if isinstance(data.get(key), list):
                return extract_rows(data[key])
        return [data] if pick(data, "user") or pick(data, "name") else []
    return []


@dataclass
class SysproResult:
    ok: bool = False             # la API respondió (válido o no)
    info: dict | None = None     # datos del usuario si las credenciales son válidas
    errors: list = field(default_factory=list)


def api_urls():
    urls = list(getattr(settings, "SYSPRO_API_URLS", []) or [])
    if settings.SYSPRO_API_URL and settings.SYSPRO_API_URL not in urls:
        urls.insert(0, settings.SYSPRO_API_URL)
    return urls


def query_syspro(username, password):
    """Consulta las URLs configuradas en orden hasta obtener una respuesta válida."""
    result = SysproResult()
    payload = json.dumps({"user": username, "pass": password, "ApiKey": settings.SYSPRO_API_KEY}).encode()
    for url in api_urls():
        req = urllib.request.Request(
            url, data=payload, method="POST", headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=settings.SYSPRO_TIMEOUT) as resp:
                body = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code == 401:
                logger.error("Syspro rechazó la ApiKey (401) en %s. Revisa SYSPRO_API_KEY.", url)
            result.errors.append(f"{url} -> HTTP {exc.code}")
            continue
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            result.errors.append(f"{url} -> sin conexión ({exc})")
            continue
        try:
            data = json.loads(body or "null")
        except ValueError:
            result.errors.append(f"{url} -> la respuesta no es JSON")
            continue
        result.ok = True
        rows = extract_rows(data)
        match = next((r for r in rows if pick(r, "user").lower() == username.lower()), None)
        if match is None and len(rows) == 1 and not pick(rows[0], "user"):
            match = rows[0]
        result.info = match
        return result
    for error in result.errors:
        logger.warning("Syspro: %s", error)
    return result


class SysproBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not (settings.SYSPRO_ENABLED and api_urls() and username and password):
            return None
        username = username.strip()
        result = query_syspro(username, password)
        if not result.ok:
            if request is not None:
                request.syspro_unavailable = True
            return None
        if not result.info:
            return None

        info = result.info
        User = get_user_model()
        login = pick(info, "user") or username
        user = User.objects.filter(username__iexact=login).first() or User(username=login.upper())
        if user.pk and user.origin != User.Origin.SYSPRO:
            logger.warning("Existe una cuenta local «%s»: no se reemplaza con datos de Syspro.", user.username)
            return None
        before = (user.first_name, user.last_name, user.supervisor, user.role)
        full_name = pick(info, "name")
        if full_name:
            user.first_name, user.last_name = split_name(full_name)
        role = map_role(pick(info, "role"))
        if login.lower() in settings.SYSPRO_ADMIN_USERS:
            role = "admin"
        user.role = role
        user.supervisor = pick(info, "supervisor").title()
        for attr, key in (("email", "email"), ("area", "area"), ("city", "city")):
            value = pick(info, key)
            if value:
                setattr(user, attr, value if attr == "email" else value.title())
        user.origin = User.Origin.SYSPRO
        if not user.pk:
            user.set_unusable_password()
        user.save()
        if before != (user.first_name, user.last_name, user.supervisor, user.role):
            # No hay tabla de usuarios en la API: estos datos van copiados en sus inscripciones.
            from apps.apidata.sync import push_user_profile

            push_user_profile(user)
        logger.info("Ingreso Syspro: %s (%s)", user.username, user.role)
        return user if user.is_active else None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
