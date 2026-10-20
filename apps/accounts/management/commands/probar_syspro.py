"""
Diagnóstico de la conexión con Syspro.

    python manage.py probar_syspro USUARIO CLAVE
"""
import json
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.accounts.backends import api_urls, extract_rows, map_role, pick, split_name


class Command(BaseCommand):
    help = "Prueba el login contra cada URL de Syspro configurada y muestra la respuesta."

    def add_arguments(self, parser):
        parser.add_argument("usuario")
        parser.add_argument("clave")

    def handle(self, usuario, clave, **opts):
        self.stdout.write(f"SYSPRO_ENABLED = {settings.SYSPRO_ENABLED}")
        payload = json.dumps({"user": usuario, "pass": clave, "ApiKey": settings.SYSPRO_API_KEY}).encode()
        for url in api_urls():
            self.stdout.write(self.style.HTTP_INFO(f"\nPOST {url}"))
            req = urllib.request.Request(url, data=payload, method="POST", headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=settings.SYSPRO_TIMEOUT) as resp:
                    body = resp.read().decode("utf-8", errors="replace")
                    self.stdout.write(f"  HTTP {resp.status}")
            except urllib.error.HTTPError as exc:
                hint = " (ApiKey inválida)" if exc.code == 401 else " (ruta inexistente)" if exc.code == 404 else ""
                self.stdout.write(self.style.ERROR(f"  HTTP {exc.code}{hint}"))
                continue
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                self.stdout.write(self.style.ERROR(f"  Sin conexión: {exc}"))
                continue
            self.stdout.write(f"  Respuesta: {body[:600]}")
            try:
                rows = extract_rows(json.loads(body or "null"))
            except ValueError:
                self.stdout.write(self.style.ERROR("  La respuesta no es JSON."))
                continue
            if not rows:
                self.stdout.write(self.style.WARNING("  Lista vacía: usuario o contraseña incorrectos."))
                continue
            row = rows[0]
            first, last = split_name(pick(row, "name"))
            self.stdout.write(self.style.SUCCESS("  Credenciales válidas. Se crearía así en el campus:"))
            self.stdout.write(f"    usuario={pick(row, 'user') or usuario}  nombres={first!r}  apellidos={last!r}")
            self.stdout.write(f"    rol={map_role(pick(row, 'role'))} (Syspro: {pick(row, 'role')!r})  supervisor={pick(row, 'supervisor')!r}")
            self.stdout.write(f"    campos recibidos: {sorted(row.keys())}")
