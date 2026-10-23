"""
Qué modelo del campus corresponde a qué tabla de la API, y cómo se convierten
los valores en ambos sentidos.

Las columnas de las tablas dbo.CV_* se llaman igual que en los modelos, con una
excepción: no hay tabla de usuarios, así que cada llave foránea a un usuario se
guarda como la columna "username" (el usuario de Syspro).
"""
import json
import re
from datetime import UTC, datetime
from decimal import Decimal

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

# Orden de carga: cada tabla va después de las tablas a las que apunta.
TABLAS = [
    ("catalog.ProductLine", "LineasProducto"),
    ("catalog.Product", "Productos"),
    ("courses.Category", "Categorias"),
    ("courses.Course", "Cursos"),
    ("courses.Module", "Modulos"),
    ("courses.Lesson", "Lecciones"),
    ("courses.Resource", "Materiales"),
    ("courses.Enrollment", "Inscripciones"),
    ("courses.LessonProgress", "ProgresoLecciones"),
    ("courses.Review", "Resenas"),
    ("courses.LearningPath", "Rutas"),
    ("courses.PathStep", "RutaCursos"),
    ("assessments.Quiz", "Evaluaciones"),
    ("assessments.Question", "Preguntas"),
    ("assessments.Choice", "Opciones"),
    ("assessments.Attempt", "Intentos"),
    ("certificates.Certificate", "Certificados"),
    ("core.Announcement", "Anuncios"),
]

# Relaciones muchos a muchos de Course: (campo, tabla, columna del otro lado).
M2M = [
    ("related_products", "CursoProductos", "product_id"),
    ("saved_by", "CursosGuardados", "username"),
]


def syspro_name(user):
    """Nombre en el orden de Syspro (apellidos y nombres), que split_name sabe separar."""
    return f"{user.last_name} {user.first_name}".strip() or user.username


# Columnas que la API guarda además de los campos del modelo: datos del usuario
# copiados de Syspro, porque no hay tabla de usuarios.
EXTRAS = {
    "courses.Enrollment": lambda e: {"full_name": syspro_name(e.user), "supervisor": e.user.supervisor, "role": e.user.role},
    "courses.Review": lambda r: {"full_name": syspro_name(r.user)},
}

_por_modelo = None


def table_for(model):
    global _por_modelo
    if _por_modelo is None:
        _por_modelo = {apps.get_model(label): tabla for label, tabla in TABLAS}
    return _por_modelo.get(model)


def m2m_for_through(through):
    """(campo, tabla, columna) si `through` es una tabla intermedia sincronizada."""
    course = apps.get_model("courses.Course")
    for field, tabla, columna in M2M:
        if course._meta.get_field(field).remote_field.through is through:
            return field, tabla, columna
    return None


def is_user_fk(field):
    return field.many_to_one and field.related_model is get_user_model()


# --------------------------------------------------------------------------- hacia la API
def to_api(field, value):
    if value is None:
        return None
    if isinstance(field, models.DateTimeField):
        if timezone.is_naive(value):
            value = timezone.make_aware(value, UTC)
        return value.astimezone(UTC).replace(tzinfo=None).isoformat(timespec="microseconds")
    if isinstance(field, models.DateField):
        return value.isoformat()
    if isinstance(field, models.FileField):
        return value.name or ""
    if isinstance(field, models.JSONField):
        return json.dumps(value)
    if isinstance(field, models.DecimalField):
        return str(value)
    return value


def row_for(instance, adding, fields=None):
    """Valores de `instance` como columnas de la API.

    Usa field.pre_save, igual que Django al guardar, para que las fechas automáticas
    y los archivos subidos tengan su valor final. `fields` limita a update_fields.
    """
    datos = {}
    for field in instance._meta.concrete_fields:
        if field.primary_key:
            continue
        if fields is not None and field.name not in fields and field.attname not in fields:
            continue
        if is_user_fk(field):
            datos["username"] = getattr(instance, field.name).username
            continue
        datos[field.column] = to_api(field, field.pre_save(instance, adding))
    extras = EXTRAS.get(instance._meta.label)
    if extras:
        datos.update(extras(instance))
    return datos


# --------------------------------------------------------------------------- desde la API
_FECHA = re.compile(r"^(?P<base>[\d-]+T[\d:]+)(?P<frac>\.\d+)?(?P<tz>Z|[+-]\d{2}:\d{2})?$")


def parse_datetime(texto):
    """SQL Server (vía .NET) entrega '2026-10-23T15:04:05.1234567' en UTC, sin zona."""
    match = _FECHA.match(texto)
    if not match:
        raise ValueError(f"Fecha no reconocida: {texto!r}")
    frac = (match["frac"] or "")[:7]  # Python acepta hasta 6 decimales
    tz = match["tz"]
    dt = datetime.fromisoformat(match["base"] + frac + ("+00:00" if tz in (None, "Z") else tz))
    return dt.astimezone(UTC)


def from_api(field, value):
    if value is None:
        return None
    if isinstance(field, models.DateTimeField):
        return parse_datetime(value)
    if isinstance(field, models.JSONField):
        return json.loads(value) if isinstance(value, str) else value
    if isinstance(field, models.DecimalField):
        return Decimal(str(value))
    if isinstance(field, models.BooleanField):
        return bool(value)
    return value
