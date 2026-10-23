"""
Escritura en la API.

Cada vez que el campus guarda o elimina un registro, primero se envía a la API;
solo si la API responde bien se completa la operación en la copia local. Si la API
falla, se lanza CampusApiError y Django cancela el cambio local.

Al crear, la API asigna el id y la copia local usa ese mismo id, así las relaciones
coinciden en ambos lados.
"""
import threading
from contextlib import contextmanager

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from . import client
from .client import CampusApiError
from .registry import m2m_for_through, row_for, syspro_name, table_for

_estado = threading.local()


@contextmanager
def paused():
    """Desactiva el envío a la API (por ejemplo, al cargar los datos que vienen de ella)."""
    previo = getattr(_estado, "paused", False)
    _estado.paused = True
    try:
        yield
    finally:
        _estado.paused = previo


def active():
    return client.enabled() and not getattr(_estado, "paused", False)


def on_pre_save(sender, instance, raw=False, update_fields=None, **kwargs):
    tabla = table_for(sender)
    if not tabla or raw or not active():
        return
    adding = instance._state.adding
    fields = None if update_fields is None else set(update_fields)
    datos = row_for(instance, adding, fields)
    if adding and instance.pk is None:
        fila = client.call("CREAR", tabla, datos=datos)[0]
        instance.pk = fila["id"]
    elif not client.call("MODIFICAR", tabla, id=instance.pk, datos=datos):
        raise CampusApiError(f"MODIFICAR {tabla}: el registro {instance.pk} no existe en la API.")


def on_post_delete(sender, instance, origin=None, **kwargs):
    if not active():
        return
    if sender is get_user_model():
        # Los usuarios no están en la API, pero sus cursos guardados sí.
        client.call("ELIMINAR", "CursosGuardados", filtro={"username": instance.username})
        return
    tabla = table_for(sender)
    if not tabla:
        return
    # Si se borra un registro "padre" (ej. un curso), SQL Server elimina sus hijos en
    # cascada; basta con eliminar el padre en la API.
    origen = origin.model if isinstance(origin, QuerySet) else type(origin) if origin is not None else sender
    if origen is not sender and table_for(origen):
        return
    client.call("ELIMINAR", tabla, id=instance.pk)


def on_m2m_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    info = m2m_for_through(sender)
    if not info or not active() or action not in ("post_add", "post_remove", "pre_clear"):
        return
    _field, tabla, columna = info
    User = get_user_model()

    def otro(obj_or_pks):
        """Valor de la columna del otro lado (product_id o username)."""
        if columna != "username":
            return obj_or_pks
        if isinstance(obj_or_pks, User):
            return obj_or_pks.username
        return list(User.objects.filter(pk__in=obj_or_pks).values_list("username", flat=True))

    if action == "pre_clear":
        filtro = {columna: otro(instance) if columna == "username" else instance.pk} if reverse else {"course_id": instance.pk}
        client.call("ELIMINAR", tabla, filtro=filtro)
        return
    if not pk_set:
        return
    if reverse:  # instance es el producto o el usuario; pk_set son cursos
        pares = [(course_id, otro(instance) if columna == "username" else instance.pk) for course_id in pk_set]
    else:  # instance es el curso
        valores = otro(list(pk_set)) if columna == "username" else list(pk_set)
        pares = [(instance.pk, valor) for valor in valores]
    if action == "post_add":
        for course_id, valor in pares:
            client.call("CREAR", tabla, datos={"course_id": course_id, columna: valor})
    else:
        for course_id, valor in pares:
            client.call("ELIMINAR", tabla, filtro={"course_id": course_id, columna: valor})


def push_user_profile(user):
    """Actualiza en la API el nombre, supervisor y rol copiados en las inscripciones del usuario."""
    if not active():
        return
    datos = {"full_name": syspro_name(user), "supervisor": user.supervisor, "role": user.role}
    for enrollment_id in user.enrollments.values_list("pk", flat=True):
        client.call("MODIFICAR", "Inscripciones", id=enrollment_id, datos=datos)
