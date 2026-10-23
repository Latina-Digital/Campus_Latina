"""
Prueba la conexión con SQL Server y crea la base del campus si no existe.

    python manage.py preparar_sqlserver

Usa los datos DB_* del .env. Después hay que correr `migrate` para crear las tablas.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import connections

PISTAS = {
    "IM002": "No está instalado el driver ODBC indicado en DB_DRIVER. Instala 'ODBC Driver 18 for SQL Server'.",
    "18456": "Usuario o contraseña de SQL Server incorrectos (o el usuario no tiene acceso).",
    "08001": "No se encontró el servidor. Revisa DB_HOST / DB_PORT y que SQL Server acepte conexiones TCP/IP.",
    "HYT00": "Se agotó el tiempo de espera. Revisa DB_HOST, el puerto y el firewall.",
    "262": "El usuario no tiene permiso para crear bases. Créala a mano en SSMS o usa un usuario con permiso dbcreator.",
}


class Command(BaseCommand):
    help = "Prueba la conexión con SQL Server y crea la base del campus si no existe."
    # Las revisiones de Django ya se conectan a la base, que puede no existir todavía.
    requires_system_checks = []

    def handle(self, **opts):
        conn = connections["default"]
        if conn.vendor != "microsoft":
            raise CommandError(f"El .env no tiene DB_ENGINE=sqlserver: el campus está usando {conn.vendor}.")
        datos = conn.settings_dict
        nombre = datos["NAME"]
        servidor = datos["HOST"] + (f",{datos['PORT']}" if datos["PORT"] else "")
        self.stdout.write(f"Servidor: {servidor}   Base: {nombre}   Usuario: {datos['USER'] or '(autenticación de Windows)'}")

        # CREATE DATABASE se ejecuta desde master, fuera de la base del campus.
        master = conn.__class__({**datos, "NAME": "master"}, alias="__master__")
        try:
            with master.cursor() as cursor:
                cursor.execute("SELECT @@VERSION")
                self.stdout.write(self.style.SUCCESS("Conectado: " + cursor.fetchone()[0].splitlines()[0]))
                cursor.execute("SELECT DB_ID(%s)", [nombre])
                if cursor.fetchone()[0] is not None:
                    self.stdout.write(f"La base {nombre} ya existe.")
                else:
                    cursor.execute(f"CREATE DATABASE {master.ops.quote_name(nombre)}")
                    self.stdout.write(self.style.SUCCESS(f"Base {nombre} creada."))
        except CommandError:
            raise
        except Exception as exc:
            texto = str(exc)
            pista = next((p for codigo, p in PISTAS.items() if codigo in texto), "")
            raise CommandError(f"No se pudo conectar con SQL Server.\n{texto}\n{pista}".rstrip())
        finally:
            master.close()
        self.stdout.write("Siguiente paso: python manage.py migrate")
