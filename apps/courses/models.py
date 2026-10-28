import re

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from apps.core.choices import Brand, Level
from apps.core.utils import format_minutes, unique_slug


class Category(models.Model):
    name = models.CharField("nombre", max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    description = models.CharField("descripción", max_length=200, blank=True)
    icon = models.CharField("ícono", max_length=40, default="book-open", help_text="Nombre de ícono Lucide (lucide.dev).")
    order = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField("título", max_length=140)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    brand = models.CharField("marca", max_length=20, choices=Brand.choices, default=Brand.LATINA)
    category = models.ForeignKey(Category, verbose_name="categoría", on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")
    level = models.CharField("nivel", max_length=20, choices=Level.choices, default=Level.BASICO)
    summary = models.CharField("resumen", max_length=240, help_text="Se muestra en las tarjetas del catálogo.")
    description = models.TextField("descripción", blank=True)
    outcomes = models.TextField("lo que aprenderás", blank=True, help_text="Un objetivo por línea.")
    cover = models.ImageField("portada", upload_to="courses/covers/", blank=True)
    instructor_name = models.CharField("instructor", max_length=120, default="Equipo de Capacitación Latina")
    instructor_title = models.CharField("cargo del instructor", max_length=120, blank=True, default="Industrial Latina S.A.")
    related_products = models.ManyToManyField("catalog.Product", verbose_name="productos relacionados", blank=True, related_name="courses")
    saved_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="saved_courses", editable=False)
    is_published = models.BooleanField("publicado", default=False)
    is_featured = models.BooleanField("destacado", default=False)
    is_mandatory = models.BooleanField("obligatorio", default=False, help_text="Se resalta en el inicio de todos los usuarios.")
    coming_soon = models.BooleanField(
        "próximamente", default=False, help_text="Se ve en el catálogo, pero nadie puede comenzarlo hasta desmarcarlo."
    )
    order = models.PositiveIntegerField("orden", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "curso"
        verbose_name_plural = "cursos"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("courses:detail", args=[self.slug])

    @property
    def lessons(self):
        return Lesson.objects.filter(module__course=self).order_by("module__order", "module_id", "order", "id")

    @property
    def outcomes_list(self):
        return [o.strip() for o in self.outcomes.splitlines() if o.strip()]

    @property
    def total_minutes(self):
        total = self.lessons.aggregate(m=models.Sum("duration_minutes"))["m"] or 0
        quiz = getattr(self, "quiz", None)
        return total + (quiz.time_limit_minutes if quiz else 0)

    @property
    def duration_display(self):
        return format_minutes(self.total_minutes)

    @property
    def quiz_or_none(self):
        try:
            return self.quiz
        except Exception:
            return None


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules", verbose_name="curso")
    title = models.CharField("título", max_length=140)
    description = models.CharField("descripción", max_length=240, blank=True)
    order = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "módulo"
        verbose_name_plural = "módulos"

    def __str__(self):
        return self.title


class Lesson(models.Model):
    class Kind(models.TextChoices):
        VIDEO = "video", "Video (archivo)"
        YOUTUBE = "youtube", "Video de YouTube"
        LECTURA = "lectura", "Lectura"
        DOCUMENTO = "documento", "Documento PDF"

    KIND_ICONS = {"video": "play-circle", "youtube": "youtube", "lectura": "file-text", "documento": "file"}

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons", verbose_name="módulo")
    title = models.CharField("título", max_length=160)
    kind = models.CharField("tipo", max_length=12, choices=Kind.choices, default=Kind.LECTURA)
    order = models.PositiveIntegerField("orden", default=0)
    duration_minutes = models.PositiveIntegerField("duración (min)", default=5)
    video = models.FileField("archivo de video", upload_to="lessons/videos/", blank=True, help_text="MP4 recomendado.")
    youtube_url = models.URLField("URL de YouTube", blank=True)
    document = models.FileField("documento PDF", upload_to="lessons/docs/", blank=True)
    content = models.TextField("contenido", blank=True, help_text="Texto de la lectura o notas debajo del video.")
    require_full_watch = models.BooleanField(
        "exigir ver el video completo", default=True, help_text="Impide adelantar el video la primera vez."
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "lección"
        verbose_name_plural = "lecciones"

    def __str__(self):
        return self.title

    @property
    def course(self):
        return self.module.course

    @property
    def icon(self):
        return self.KIND_ICONS.get(self.kind, "circle")

    @property
    def youtube_id(self):
        match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([\w-]{11})", self.youtube_url or "")
        return match.group(1) if match else ""

    def get_absolute_url(self):
        return reverse("courses:lesson", args=[self.module.course.slug, self.pk])


class Resource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="resources", verbose_name="curso")
    title = models.CharField("título", max_length=140)
    file = models.FileField("archivo", upload_to="resources/", blank=True)
    url = models.URLField("o enlace externo", blank=True)

    class Meta:
        verbose_name = "material descargable"
        verbose_name_plural = "materiales descargables"

    def __str__(self):
        return self.title

    @property
    def href(self):
        return self.file.url if self.file else self.url


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    created_at = models.DateTimeField("inscrito", auto_now_add=True)
    last_accessed = models.DateTimeField("último acceso", auto_now=True)
    last_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    completed_at = models.DateTimeField("completado", null=True, blank=True)

    class Meta:
        unique_together = ("user", "course")
        ordering = ["-last_accessed"]
        verbose_name = "inscripción"
        verbose_name_plural = "inscripciones"

    def __str__(self):
        return f"{self.user} → {self.course}"


class LessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    position_seconds = models.FloatField(default=0)
    max_position_seconds = models.FloatField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "lesson")
        verbose_name = "progreso de lección"
        verbose_name_plural = "progreso de lecciones"


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField("calificación", validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField("comentario", blank=True, max_length=800)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "course")
        ordering = ["-created_at"]
        verbose_name = "reseña"
        verbose_name_plural = "reseñas"


class LearningPath(models.Model):
    title = models.CharField("título", max_length=140)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    summary = models.CharField("resumen", max_length=240)
    description = models.TextField("descripción", blank=True)
    brand = models.CharField("marca", max_length=20, choices=Brand.choices, default=Brand.LATINA)
    cover = models.ImageField("portada", upload_to="paths/", blank=True)
    is_published = models.BooleanField("publicada", default=True)
    order = models.PositiveIntegerField("orden", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "ruta de aprendizaje"
        verbose_name_plural = "rutas de aprendizaje"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("courses:my_learning") + f"?ruta={self.slug}#rutas"

    @property
    def ordered_courses(self):
        return [step.course for step in self.steps.select_related("course", "course__category") if step.course.is_published]


class PathStep(models.Model):
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name="steps")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="path_steps", verbose_name="curso")
    order = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("path", "course")
        verbose_name = "curso de la ruta"
        verbose_name_plural = "cursos de la ruta"
