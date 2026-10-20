from django.db import models
from django.urls import reverse

from apps.core.choices import Brand
from apps.core.utils import unique_slug


class ProductLine(models.Model):
    name = models.CharField("nombre", max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    icon = models.CharField("ícono", max_length=40, default="package", help_text="Nombre de ícono Lucide (lucide.dev).")
    order = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "línea de productos"
        verbose_name_plural = "líneas de productos"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    brand = models.CharField(
        "marca", max_length=20, choices=[c for c in Brand.choices if c[0] != Brand.CORPORATIVO], default=Brand.LATINA
    )
    line = models.ForeignKey(ProductLine, verbose_name="línea", on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    name = models.CharField("nombre", max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    summary = models.CharField("descripción breve", max_length=220)
    description = models.TextField("descripción", blank=True)
    features = models.TextField("características", blank=True, help_text="Una característica por línea.")
    uses = models.TextField("usos recomendados", blank=True, help_text="Un uso por línea.")
    presentations = models.CharField("presentaciones", max_length=200, blank=True, help_text="Ej: Galón, Caneca 5 gl")
    image = models.ImageField("imagen", upload_to="products/", blank=True)
    datasheet = models.FileField("ficha técnica (PDF)", upload_to="products/fichas/", blank=True)
    is_active = models.BooleanField("activo", default=True)
    order = models.PositiveIntegerField("orden", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:detail", args=[self.slug])

    @property
    def features_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]

    @property
    def uses_list(self):
        return [f.strip() for f in self.uses.splitlines() if f.strip()]
