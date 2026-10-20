from django.db import models


class Announcement(models.Model):
    class Tone(models.TextChoices):
        INFO = "info", "Informativo"
        NUEVO = "nuevo", "Novedad"
        URGENTE = "urgente", "Importante"

    title = models.CharField("título", max_length=140)
    body = models.TextField("mensaje", max_length=600)
    tone = models.CharField("tipo", max_length=10, choices=Tone.choices, default=Tone.INFO)
    link_url = models.CharField("enlace (opcional)", max_length=300, blank=True)
    link_label = models.CharField("texto del enlace", max_length=40, blank=True, default="Ver más")
    is_active = models.BooleanField("visible", default=True)
    created_at = models.DateTimeField("publicado", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "anuncio"
        verbose_name_plural = "anuncios"

    def __str__(self):
        return self.title
