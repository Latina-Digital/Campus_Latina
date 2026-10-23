"""
Copia local de los datos de la API.

Al arrancar, el campus descarga todas las tablas dbo.CV_* y las carga en su base
local (SQLite), que funciona solo como copia de trabajo: las páginas leen de ella
y cada cambio se envía primero a la API (ver sync.py). Los datos permanentes
viven únicamente en SQL Server.

Los usuarios no están en la API: se reconstruyen a partir de los registros que
los mencionan (inscripciones, intentos, certificados...), con el nombre, rol y
supervisor copiados de Syspro.
"""
import logging
import time

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, transaction

from apps.accounts.backends import split_name

from . import client
from .registry import M2M, TABLAS, from_api, is_user_fk
from .sync import paused

logger = logging.getLogger("apps.apidata")


def prepare():
    """Crea las tablas locales y carga los datos de la API. Se llama al arrancar el sitio."""
    if not client.enabled():
        return
    with paused():
        call_command("migrate", interactive=False, verbosity=0)
    load_all()


def load_all():
    inicio = time.monotonic()
    # Primero se descarga todo; así la base local queda bloqueada el menor tiempo posible.
    datos = {tabla: client.call("CONSULTAR", tabla) for _label, tabla in TABLAS}
    for _field, tabla, _col in M2M:
        datos[tabla] = client.call("CONSULTAR", tabla)
    with paused(), transaction.atomic():
        usuarios = _sync_users(datos)
        Course = apps.get_model("courses.Course")
        for field, _tabla, _col in M2M:
            Course._meta.get_field(field).remote_field.through.objects.all()._raw_delete(DEFAULT_DB_ALIAS)
        for label, _tabla in reversed(TABLAS):
            apps.get_model(label)._base_manager.all()._raw_delete(DEFAULT_DB_ALIAS)
        cargados = {}
        for label, tabla in TABLAS:
            model = apps.get_model(label)
            objs = [obj for fila in datos[tabla] if (obj := _build(model, fila, usuarios, cargados)) is not None]
            model._base_manager.bulk_create(objs, batch_size=500)
            cargados[model] = {obj.pk for obj in objs}
        _load_m2m(datos, usuarios, cargados)
    total = sum(len(filas) for filas in datos.values())
    logger.info("Datos del campus cargados desde la API: %s registros en %.1f s.", total, time.monotonic() - inicio)
    return total


def _build(model, fila, usuarios, cargados):
    kwargs = {}
    for field in model._meta.concrete_fields:
        if is_user_fk(field):
            user_id = usuarios.get((fila.get("username") or "").lower())
            if user_id is None:
                return None
            kwargs[field.attname] = user_id
            continue
        value = from_api(field, fila.get(field.column))
        if field.many_to_one and value is not None and value not in cargados.get(field.related_model, ()):
            # Referencia a un registro que ya no existe (ej. la última lección vista fue borrada).
            if not field.null:
                return None
            value = None
        kwargs[field.attname] = value
    return model(**kwargs)


def _load_m2m(datos, usuarios, cargados):
    Course = apps.get_model("courses.Course")
    for field, tabla, columna in M2M:
        through = Course._meta.get_field(field).remote_field.through
        cursos = cargados[Course]
        objs = []
        for fila in datos[tabla]:
            if fila["course_id"] not in cursos:
                continue
            if columna == "username":
                user_id = usuarios.get((fila["username"] or "").lower())
                if user_id is not None:
                    objs.append(through(course_id=fila["course_id"], user_id=user_id))
            elif fila[columna] in cargados[apps.get_model("catalog.Product")]:
                objs.append(through(course_id=fila["course_id"], product_id=fila[columna]))
        through.objects.bulk_create(objs, batch_size=500, ignore_conflicts=True)


def _sync_users(datos):
    """Crea o actualiza los usuarios mencionados en los datos. Devuelve {username en minúsculas: id}."""
    User = get_user_model()
    perfiles = {}  # username -> (nombre Syspro, supervisor, rol), del acceso más reciente
    for fila in sorted(datos["Inscripciones"], key=lambda f: f.get("last_accessed") or ""):
        perfiles[fila["username"].lower()] = (fila.get("full_name") or "", fila.get("supervisor") or "", fila.get("role") or "")
    nombres = {fila["username"].lower(): fila.get("holder_name") or "" for fila in datos["Certificados"]}
    usernames = {}
    for filas in datos.values():
        for fila in filas:
            if fila.get("username"):
                usernames.setdefault(fila["username"].lower(), fila["username"])

    existentes = {u.username.lower(): u for u in User.objects.all()}
    resultado = {}
    for key, username in usernames.items():
        user = existentes.get(key)
        nuevo = user is None
        if nuevo:
            user = User(username=username.upper(), origin=User.Origin.SYSPRO)
            user.set_unusable_password()
        if key in perfiles:
            full_name, supervisor, role = perfiles[key]
            first, last = split_name(full_name) if full_name else (user.first_name, user.last_name)
            nuevos = {"first_name": first, "last_name": last, "supervisor": supervisor, "role": role or user.role}
        elif nuevo and nombres.get(key):
            # El certificado guarda el nombre ya formateado ("Nombres Apellidos").
            nuevos = {"first_name": nombres[key], "last_name": ""}
        else:
            nuevos = {}
        cambios = nuevo
        for attr, value in nuevos.items():
            if getattr(user, attr) != value:
                setattr(user, attr, value)
                cambios = True
        if cambios:
            user.save()
        resultado[key] = user.pk
    return resultado
