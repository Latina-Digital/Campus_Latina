from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        EJECUTIVO = "ejecutivo", "Ejecutivo comercial"
        SUPERVISOR = "supervisor", "Supervisor"
        JEFE_VENTAS = "jefe_ventas", "Jefe de ventas"
        JEFE_NACIONAL = "jefe_nacional", "Jefe nacional de ventas"
        ADMIN = "admin", "Administrador"

    class Origin(models.TextChoices):
        LOCAL = "local", "Campus"
        SYSPRO = "syspro", "Syspro"

    # Roles con acceso al panel de gestión.
    PANEL_ROLES = {Role.ADMIN, Role.JEFE_NACIONAL, Role.JEFE_VENTAS}

    role = models.CharField("rol", max_length=20, choices=Role.choices, default=Role.EJECUTIVO)
    supervisor = models.CharField(
        "supervisor", max_length=150, blank=True, help_text="Nombre completo del supervisor directo."
    )
    area = models.CharField("área / zona", max_length=120, blank=True)
    city = models.CharField("ciudad", max_length=80, blank=True)
    headline = models.CharField("titular", max_length=140, blank=True, help_text="Ej: Asesor técnico de pinturas")
    avatar = models.ImageField("foto", upload_to="avatars/", blank=True)
    origin = models.CharField("origen", max_length=10, choices=Origin.choices, default=Origin.LOCAL)

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ["first_name", "last_name"]

    def save(self, *args, **kwargs):
        self.is_staff = self.is_superuser or self.role in self.PANEL_ROLES
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    @property
    def short_name(self):
        return (self.first_name.split() or [self.username])[0]

    @property
    def initials(self):
        parts = [p for p in (self.first_name.split()[:1] + self.last_name.split()[:1]) if p]
        if not parts:
            return self.username[:2].upper()
        return "".join(p[0] for p in parts).upper()

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.Role.ADMIN

    @property
    def is_leader(self):
        return self.role != self.Role.EJECUTIVO
