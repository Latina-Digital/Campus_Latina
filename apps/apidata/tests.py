"""
Pruebas de la sincronización con la API del campus.

FakeCampusApi imita a dbo.spCampus_Datos: lee las tablas, columnas, tipos y llaves
foráneas del script real (deploy/api_campus/01_campus_nuevo.sql), rechaza columnas
desconocidas, asigna los id, borra en cascada y devuelve las fechas como SQL Server.
Así, si el campus enviara una columna que no existe en SQL Server, estas pruebas fallan.
"""
import io
import re
import shutil
import tempfile
from unittest import mock

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User

from . import client
from .client import CampusApiError
from .mirror import load_all
from .registry import EXTRAS, M2M, TABLAS, api_has_column, is_user_fk, set_missing_columns

SQL_FILE = settings.BASE_DIR / "deploy" / "api_campus" / "01_campus_nuevo.sql"


def parse_schema():
    """{tabla: {"cols": {columna: tipo}, "refs": {columna: (tabla, accion)}}} desde el script SQL."""
    sql = re.sub(r"--[^\n]*", "", SQL_FILE.read_text(encoding="utf-8-sig"))
    schema = {}
    for match in re.finditer(r"CREATE TABLE dbo\.CV_(\w+) \((.*?)\n    \);", sql, re.S):
        tabla, body = match.groups()
        partes, depth, actual = [], 0, ""
        for ch in body:
            depth += ch == "("
            depth -= ch == ")"
            if ch == "," and depth == 0:
                partes.append(actual)
                actual = ""
            else:
                actual += ch
        partes.append(actual)
        cols, refs = {}, {}
        for parte in (" ".join(p.split()) for p in partes):
            if not parte or parte.startswith("CONSTRAINT"):
                continue
            nombre, tipo = parte.split(" ")[:2]
            nombre = nombre.strip("[]")
            cols[nombre] = tipo.split("(")[0].upper()
            ref = re.search(r"REFERENCES dbo\.CV_(\w+)\(id\)(?: ON DELETE (CASCADE|SET NULL))?", parte)
            if ref:
                refs[nombre] = (ref[1], ref[2] or "NO ACTION")
        schema[tabla] = {"cols": cols, "refs": refs}
    return schema


class FakeCampusApi:
    def __init__(self):
        self.schema = parse_schema()
        self.rows = {t: {} for t in self.schema}
        self.next_id = dict.fromkeys(self.schema, 1)
        self.calls = []
        self.fail_on = None  # (accion, tabla) que debe fallar

    def _conv(self, tipo, value):
        if value is None:
            return None
        if tipo == "BIT":
            return value if isinstance(value, bool) else str(value).lower() in ("1", "true")
        if tipo in ("INT", "SMALLINT"):
            return int(value)
        if tipo in ("FLOAT", "DECIMAL"):
            return float(value)
        return str(value)

    def _out(self, tabla, row):
        cols = self.schema[tabla]["cols"]
        out = {}
        for col, value in row.items():
            if cols[col] == "DATETIME2" and value is not None:
                value = value + "0" if "." in value else value + ".0000000"  # 7 decimales, como .NET
            out[col] = value
        return out

    def _check(self, tabla, data, permitir_id):
        cols = self.schema[tabla]["cols"]
        for key in data or {}:
            if key not in cols or (key == "id" and not permitir_id):
                raise CampusApiError(f"Columna no válida en {tabla}: {key}")

    def _match(self, tabla, row, filtro):
        cols = self.schema[tabla]["cols"]
        for col, value in (filtro or {}).items():
            actual = row[col]
            valores = value if isinstance(value, list) else [value]
            convertidos = [self._conv(cols[col], v) for v in valores]
            if isinstance(actual, str):
                if actual.lower() not in [str(v).lower() for v in convertidos if v is not None]:
                    return False
            elif value is None:
                if actual is not None:
                    return False
            elif actual not in convertidos:
                return False
        return True

    def _delete(self, tabla, row_id):
        if self.rows[tabla].pop(row_id, None) is None:
            return
        for otra, info in self.schema.items():
            for col, (destino, accion) in info["refs"].items():
                if destino != tabla:
                    continue
                for hijo in [r for r in self.rows[otra].values() if r[col] == row_id]:
                    if accion == "CASCADE":
                        self._delete(otra, hijo["id"])
                    elif accion == "SET NULL":
                        hijo[col] = None

    def call(self, accion, tabla, id=0, filtro=None, datos=None):
        self.calls.append((accion, tabla))
        if self.fail_on == (accion, tabla):
            raise CampusApiError(f"{accion} {tabla}: error simulado")
        if tabla not in self.schema:
            raise CampusApiError("Tabla no permitida.")
        self._check(tabla, filtro, permitir_id=True)
        self._check(tabla, datos, permitir_id=False)
        cols = self.schema[tabla]["cols"]
        filtro = dict(filtro or {}, **({"id": id} if id else {}))
        if accion == "CONSULTAR":
            return [self._out(tabla, r) for r in sorted(self.rows[tabla].values(), key=lambda r: r["id"]) if self._match(tabla, r, filtro)]
        if accion == "CREAR":
            row = dict.fromkeys(cols)
            row.update({k: self._conv(cols[k], v) for k, v in (datos or {}).items()})
            row["id"] = self.next_id[tabla]
            self.next_id[tabla] += 1
            self.rows[tabla][row["id"]] = row
            return [self._out(tabla, row)]
        if accion == "MODIFICAR":
            row = self.rows[tabla].get(id)
            if row is None:
                return []
            row.update({k: self._conv(cols[k], v) for k, v in (datos or {}).items()})
            return [self._out(tabla, row)]
        if accion == "ELIMINAR":
            if not filtro:
                raise CampusApiError("ELIMINAR requiere @Id o @Filtro.")
            ids = [r["id"] for r in self.rows[tabla].values() if self._match(tabla, r, filtro)]
            for row_id in ids:
                self._delete(tabla, row_id)
            return [{"id": i} for i in ids]
        raise CampusApiError(f"Accion no válida: {accion}")


MEDIA = tempfile.mkdtemp(prefix="campus-api-media-")


def snapshot():
    """Todos los registros sincronizados.

    Sin las fechas automáticas (auto_now / auto_now_add): Django las vuelve a calcular
    al guardar localmente, unos milisegundos después de enviarlas a la API.
    """
    data = {}
    for label, _tabla in TABLAS:
        model = apps.get_model(label)
        campos = [
            f.attname for f in model._meta.concrete_fields
            if not (getattr(f, "auto_now", False) or getattr(f, "auto_now_add", False))
        ]
        data[label] = list(model.objects.order_by("pk").values_list(*campos))
    course = apps.get_model("courses.Course")
    for field, _tabla, _col in M2M:
        through = course._meta.get_field(field).remote_field.through
        data[field] = sorted(through.objects.values_list(*[f.attname for f in through._meta.concrete_fields if not f.primary_key]))
    return data


class SchemaTests(TransactionTestCase):
    def test_every_column_the_campus_sends_exists_in_sql(self):
        schema = parse_schema()
        for label, tabla in TABLAS:
            model = apps.get_model(label)
            columnas = {"username" if is_user_fk(f) else f.column for f in model._meta.concrete_fields}
            if label in EXTRAS:
                columnas |= {"full_name", "supervisor", "role"} if label == "courses.Enrollment" else {"full_name"}
            faltan = columnas - set(schema[tabla]["cols"])
            self.assertFalse(faltan, f"{label} -> dbo.CV_{tabla}: faltan {faltan}")
        for _field, tabla, columna in M2M:
            self.assertTrue({"course_id", columna} <= set(schema[tabla]["cols"]), tabla)


@override_settings(CAMPUS_API_URL="http://api-falsa/api/syspro/campus/datos", MEDIA_ROOT=MEDIA)
class ApiSyncTests(TransactionTestCase):
    def setUp(self):
        self.api = FakeCampusApi()
        patcher = mock.patch.object(client, "call", self.api.call)
        patcher.start()
        self.addCleanup(patcher.stop)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def test_full_flow_is_stored_in_the_api_and_reloads_identically(self):
        from apps.assessments.models import Attempt, Choice
        from apps.certificates.models import Certificate
        from apps.courses.models import Course, Enrollment

        call_command("seed_campus", stdout=io.StringIO())
        self.assertEqual(len(self.api.rows["Cursos"]), Course.objects.count())
        self.assertGreater(len(self.api.rows["CursoProductos"]), 0)
        # Los id locales son los que asignó la API.
        self.assertEqual(sorted(self.api.rows["Cursos"]), sorted(Course.objects.values_list("pk", flat=True)))

        learner = User.objects.create(username="TESTER", first_name="Ana", last_name="Prueba", supervisor="Fernando Abarca", origin="syspro")
        self.client.force_login(learner)
        course = Course.objects.get(title__startswith="Duralin")
        self.client.post(reverse("courses:toggle_save", args=[course.slug]))
        for lesson in course.lessons:
            self.assertEqual(self.client.post(reverse("courses:lesson_complete", args=[lesson.pk])).status_code, 200)
        self.client.post(reverse("assessments:intro", args=[course.slug]))
        attempt = Attempt.objects.get(user=learner)
        answers = {f"q_{qid}": Choice.objects.get(question_id=qid, is_correct=True).pk for qid in attempt.question_ids}
        self.client.post(reverse("assessments:submit", args=[attempt.pk]), answers)
        cert = Certificate.objects.get(user=learner, course=course)

        inscripcion = next(iter(self.api.rows["Inscripciones"].values()))
        self.assertEqual((inscripcion["username"], inscripcion["full_name"], inscripcion["supervisor"]), ("TESTER", "Prueba Ana", "Fernando Abarca"))
        self.assertIsNotNone(inscripcion["completed_at"])
        intento = self.api.rows["Intentos"][attempt.pk]
        self.assertEqual((intento["score"], intento["passed"]), (100, True))
        self.assertEqual(self.api.rows["Certificados"][cert.pk]["code"], cert.code)
        self.assertEqual([r["username"] for r in self.api.rows["CursosGuardados"].values()], ["TESTER"])

        # Recargar desde la API deja exactamente los mismos datos.
        antes = snapshot()
        load_all()
        self.assertEqual(snapshot(), antes)
        self.assertEqual(Enrollment.objects.get(user=learner).course, course)
        self.assertEqual(User.objects.get(username="TESTER").pk, learner.pk)  # la sesión sigue válida

        # Un usuario que solo existe en la API se reconstruye con sus datos de Syspro.
        learner.delete()
        self.assertFalse(self.api.rows["Inscripciones"])
        self.assertFalse(self.api.rows["CursosGuardados"])

    def test_deleting_a_course_cascades_in_the_api(self):
        from apps.courses.models import Course, Lesson

        call_command("seed_campus", stdout=io.StringIO())
        course = Course.objects.first()
        lecciones = Lesson.objects.filter(module__course=course).count()
        antes = len(self.api.rows["Lecciones"])
        self.api.calls.clear()
        course.delete()
        self.assertEqual(len(self.api.rows["Lecciones"]), antes - lecciones)
        self.assertNotIn(course.pk, self.api.rows["Cursos"])
        # Solo se envía el curso: SQL Server borra en cascada módulos, lecciones, preguntas...
        self.assertEqual(self.api.calls, [("ELIMINAR", "Cursos")])
        antes = snapshot()
        load_all()
        self.assertEqual(snapshot(), antes)

    def test_column_missing_in_the_api_is_not_sent(self):
        from apps.courses.models import Course

        call_command("seed_campus", stdout=io.StringIO())
        # Tabla de cursos de antes de ejecutar 03_proximamente.sql.
        del self.api.schema["Cursos"]["cols"]["coming_soon"]
        for fila in self.api.rows["Cursos"].values():
            del fila["coming_soon"]
        load_all()
        self.addCleanup(set_missing_columns, "Cursos", [])
        self.assertFalse(api_has_column(Course, "coming_soon"))
        course = Course.objects.first()
        course.title = "Título editado"
        course.save()
        self.assertEqual(self.api.rows["Cursos"][course.pk]["title"], "Título editado")

    def test_api_error_cancels_the_local_change(self):
        from apps.core.models import Announcement

        self.api.fail_on = ("CREAR", "Anuncios")
        with self.assertRaises(CampusApiError):
            Announcement.objects.create(title="Hola", body="x")
        self.assertFalse(Announcement.objects.exists())

        self.api.fail_on = None
        anuncio = Announcement.objects.create(title="Hola", body="x")
        self.api.fail_on = ("ELIMINAR", "Anuncios")
        with self.assertRaises(CampusApiError):
            anuncio.delete()
        self.assertTrue(Announcement.objects.filter(pk=anuncio.pk).exists())
        self.assertIn(anuncio.pk, self.api.rows["Anuncios"])

    def test_login_updates_profile_copied_in_enrollments(self):
        from apps.accounts.backends import SysproBackend
        from apps.courses.models import Course, Enrollment

        call_command("seed_campus", stdout=io.StringIO())
        user = User.objects.create(username="CYAGUACHI", first_name="Carlos", last_name="Yaguachi", origin="syspro")
        Enrollment.objects.create(user=user, course=Course.objects.first())
        info = {"user": "CYAGUACHI", "nombre": "YAGUACHI MENDOZA CARLOS EDUARDO", "rol": "SUPERVISOR", "supervisor": "ANA PEREZ"}
        with mock.patch("apps.accounts.backends.query_syspro", return_value=mock.Mock(ok=True, info=info)), \
             override_settings(SYSPRO_ENABLED=True, SYSPRO_API_URL="http://syspro"):
            SysproBackend().authenticate(None, username="cyaguachi", password="x")
        fila = next(iter(self.api.rows["Inscripciones"].values()))
        self.assertEqual((fila["full_name"], fila["supervisor"], fila["role"]), ("Yaguachi Mendoza Carlos Eduardo", "Ana Perez", "supervisor"))
