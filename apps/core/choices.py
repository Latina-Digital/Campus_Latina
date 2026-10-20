from django.db import models


class Brand(models.TextChoices):
    LATINA = "latina", "Industrial Latina"
    INDULESS = "induless", "Induless"
    CORPORATIVO = "corporativo", "Corporativo"


class Level(models.TextChoices):
    BASICO = "basico", "Básico"
    INTERMEDIO = "intermedio", "Intermedio"
    AVANZADO = "avanzado", "Avanzado"
