from django import forms
from django.contrib.auth.forms import AuthenticationForm

from apps.core.forms import StyledFormMixin


class LoginForm(StyledFormMixin, AuthenticationForm):
    remember = forms.BooleanField(label="Mantener sesión iniciada", required=False, initial=True)

    error_messages = {
        "invalid_login": "Usuario o contraseña incorrectos.",
        "inactive": "Esta cuenta está desactivada. Contacta a Capacitación.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario"
        self.fields["username"].widget.attrs.update({"placeholder": "Tu usuario", "autofocus": True})
        self.fields["password"].label = "Contraseña"
        self.fields["password"].widget.attrs.update({"placeholder": "••••••••"})

    def get_invalid_login_error(self):
        if getattr(self.request, "syspro_unavailable", False):
            return forms.ValidationError(
                "No pudimos conectarnos con el sistema corporativo (Syspro). Intenta de nuevo en unos minutos.",
                code="syspro_unavailable",
            )
        return super().get_invalid_login_error()
