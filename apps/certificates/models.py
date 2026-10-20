import secrets

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_code():
    return f"IL-{timezone.now():%Y}-" + "".join(secrets.choice(CODE_ALPHABET) for _ in range(8))


class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certificates", verbose_name="usuario")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="certificates", verbose_name="curso")
    code = models.CharField("código", max_length=24, unique=True, default=generate_code, editable=False)
    issued_at = models.DateTimeField("emitido", default=timezone.now)
    score = models.PositiveIntegerField("nota", null=True, blank=True)
    hours = models.DecimalField("horas", max_digits=5, decimal_places=1, default=1)
    attempt = models.ForeignKey("assessments.Attempt", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    # Datos congelados al emitir, para que el certificado no cambie si se edita el curso.
    holder_name = models.CharField("nombre en el certificado", max_length=160)
    course_title = models.CharField("curso en el certificado", max_length=160)
    is_revoked = models.BooleanField("revocado", default=False)

    class Meta:
        unique_together = ("user", "course")
        ordering = ["-issued_at"]
        verbose_name = "certificado"
        verbose_name_plural = "certificados"

    def __str__(self):
        return f"{self.code} · {self.holder_name}"

    def get_absolute_url(self):
        return reverse("certificates:detail", args=[self.code])

    def get_verify_path(self):
        return reverse("certificates:verify_code", args=[self.code])
