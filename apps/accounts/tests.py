import io
import json
import urllib.error
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import User

URL_A = "http://api-a/api/syspro/users"
URL_B = "http://api-b/api/syspro/users"
SYSPRO = dict(SYSPRO_ENABLED=True, SYSPRO_API_URL=URL_A, SYSPRO_API_URLS=[URL_B], SYSPRO_API_KEY="k", SYSPRO_ADMIN_USERS=["jefe1"])


class FakeResponse(io.BytesIO):
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def fake_api(responses):
    """responses: {url: lista/dict | Exception}. Guarda los payloads recibidos."""
    calls = []

    def urlopen(req, timeout=None):
        calls.append((req.full_url, json.loads(req.data)))
        result = responses[req.full_url]
        if isinstance(result, Exception):
            raise result
        return FakeResponse(json.dumps(result).encode())

    return urlopen, calls


def http_error(code):
    return urllib.error.HTTPError(URL_A, code, "error", {}, None)


@override_settings(**SYSPRO)
class SysproLoginTests(TestCase):
    def login(self, user, password):
        return self.client.post(reverse("accounts:login"), {"username": user, "password": password})

    def test_valid_user_is_created_with_syspro_data(self):
        urlopen, calls = fake_api({URL_A: [{"user": "CYAGUACHI", "nombre": "YAGUACHI LEON CARLOS ANDRES", "rol": "SUPERVISOR", "supervisor": "FERNANDO ABARCA"}]})
        with mock.patch("urllib.request.urlopen", urlopen):
            r = self.login("cyaguachi", "12345")
        self.assertRedirects(r, reverse("courses:home"), fetch_redirect_response=False)
        self.assertEqual(calls[0][1], {"user": "cyaguachi", "pass": "12345", "ApiKey": "k"})
        user = User.objects.get(username="CYAGUACHI")
        self.assertEqual((user.first_name, user.last_name), ("Carlos Andres", "Yaguachi Leon"))
        self.assertEqual(user.role, "supervisor")
        self.assertEqual(user.supervisor, "Fernando Abarca")
        self.assertEqual(user.origin, "syspro")
        self.assertFalse(user.has_usable_password())

    def test_empty_list_means_wrong_credentials(self):
        urlopen, _ = fake_api({URL_A: []})
        with mock.patch("urllib.request.urlopen", urlopen):
            r = self.login("CYAGUACHI", "mala")
        self.assertContains(r, "Usuario o contraseña incorrectos")
        self.assertFalse(User.objects.filter(username__iexact="cyaguachi").exists())

    def test_falls_back_to_next_url_and_accepts_field_variants(self):
        urlopen, calls = fake_api({URL_A: http_error(404), URL_B: {"data": [{"Usuario": "JEFE1", "Nombre": "PEREZ MORA ANA", "Rol": "Jefe de ventas"}]}})
        with mock.patch("urllib.request.urlopen", urlopen):
            r = self.login("jefe1", "x")
        self.assertEqual(r.status_code, 302)
        self.assertEqual([c[0] for c in calls], [URL_A, URL_B])
        user = User.objects.get(username="JEFE1")
        self.assertEqual(user.role, "admin")  # incluido en SYSPRO_ADMIN_USERS
        self.assertTrue(user.is_staff)

    def test_server_down_shows_connection_message(self):
        down = urllib.error.URLError("timed out")
        urlopen, _ = fake_api({URL_A: down, URL_B: http_error(401)})
        with mock.patch("urllib.request.urlopen", urlopen):
            r = self.login("alguien", "x")
        self.assertContains(r, "No pudimos conectarnos con el sistema corporativo")

    def test_local_accounts_are_not_overwritten(self):
        User.objects.create_user("CYAGUACHI", password="local123", first_name="Local")
        urlopen, _ = fake_api({URL_A: [{"user": "CYAGUACHI", "nombre": "OTRO NOMBRE X Y"}]})
        with mock.patch("urllib.request.urlopen", urlopen):
            self.login("CYAGUACHI", "otra")
        self.assertEqual(User.objects.get(username="CYAGUACHI").first_name, "Local")

    def test_local_passwords_are_not_accepted(self):
        # No hay cuentas propias del campus: todo ingreso se valida en Syspro.
        User.objects.create_user("admin2", password="Clave2026*")
        urlopen, _ = fake_api({URL_A: []})
        with mock.patch("urllib.request.urlopen", urlopen):
            r = self.login("admin2", "Clave2026*")
        self.assertContains(r, "Usuario o contraseña incorrectos")
