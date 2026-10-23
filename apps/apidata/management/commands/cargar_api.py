"""
Descarga de nuevo todos los datos desde la API del campus.

    python manage.py cargar_api

El sitio lo hace solo al arrancar; este comando sirve para probar la conexión o
para ver datos cargados directamente en SQL Server sin reiniciar.
"""
from django.core.management.base import BaseCommand, CommandError

from apps.apidata import client
from apps.apidata.mirror import prepare


class Command(BaseCommand):
    help = "Carga en la copia local todos los datos de la API del campus."

    def handle(self, **opts):
        if not client.enabled():
            raise CommandError("CAMPUS_API_URL no está configurada en .env.")
        self.stdout.write(f"API: {', '.join(client.api_urls())}")
        try:
            prepare()
        except client.CampusApiError as exc:
            raise CommandError(str(exc)) from exc
        from apps.courses.models import Course, Enrollment

        self.stdout.write(self.style.SUCCESS(
            f"Datos cargados: {Course.objects.count()} cursos, {Enrollment.objects.count()} inscripciones."
        ))
