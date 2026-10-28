"""
Actualización en tiempo real de las páginas abiertas.

El campus lleva una "versión de los datos" que cambia cada vez que cambia algo que se
ve en las páginas: un curso, una lección, un producto, un certificado... ya sea desde
este campus (señales de Django) o desde otro (al recargar la copia desde la API, ver
mirror.py). Las páginas abiertas consultan la versión cada pocos segundos
(static/js/campus.js) y, si cambió, se actualizan solas sin recargar.

No se cuentan los cambios que ocurren todo el tiempo mientras alguien estudia
(posición del video, respuestas guardadas del examen), para no refrescar las
páginas de todos a cada rato.
"""
import time

from django.apps import apps

from .registry import M2M, table_for

MODELOS = [
    "catalog.ProductLine", "catalog.Product",
    "courses.Category", "courses.Course", "courses.Module", "courses.Lesson", "courses.Resource",
    "courses.Review", "courses.LearningPath", "courses.PathStep",
    "assessments.Quiz", "assessments.Question", "assessments.Choice",
    "certificates.Certificate", "core.Announcement",
]

_version = time.time_ns()


def version():
    return format(_version, "x")


def bump():
    global _version
    _version = max(_version + 1, time.time_ns())


def tablas():
    """Tablas de la API cuyos cambios se ven en las páginas."""
    return [table_for(apps.get_model(label)) for label in MODELOS] + [tabla for _f, tabla, _c in M2M]


def _es_visible(sender):
    return sender._meta.label in MODELOS


def on_change(sender, **kwargs):
    if _es_visible(sender):
        bump()


def on_m2m_change(sender, action, **kwargs):
    if action in ("post_add", "post_remove", "post_clear"):
        bump()
