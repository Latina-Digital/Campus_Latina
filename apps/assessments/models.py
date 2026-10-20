from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

# Margen de gracia (segundos) para envíos que llegan justo al terminar el tiempo.
GRACE_SECONDS = 20


class Quiz(models.Model):
    course = models.OneToOneField("courses.Course", on_delete=models.CASCADE, related_name="quiz", verbose_name="curso")
    title = models.CharField("título", max_length=140, default="Evaluación final")
    instructions = models.TextField("instrucciones", blank=True)
    time_limit_minutes = models.PositiveIntegerField("tiempo límite (min)", default=10)
    questions_per_attempt = models.PositiveIntegerField(
        "preguntas por intento", default=10, help_text="Se eligen al azar del banco de preguntas."
    )
    passing_score = models.PositiveIntegerField("nota mínima (%)", default=70)
    max_attempts = models.PositiveIntegerField("intentos máximos", default=0, help_text="0 = ilimitados.")
    show_review = models.BooleanField("mostrar respuestas al terminar", default=True)

    class Meta:
        verbose_name = "evaluación"
        verbose_name_plural = "evaluaciones"

    def __str__(self):
        return f"{self.title} · {self.course}"

    @property
    def effective_question_count(self):
        return min(self.questions_per_attempt, self.questions.count())


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField("pregunta")
    explanation = models.TextField("explicación", blank=True, help_text="Se muestra en la revisión.")
    order = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "pregunta"
        verbose_name_plural = "preguntas"

    def __str__(self):
        return self.text[:80]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField("opción", max_length=400)
    is_correct = models.BooleanField("correcta", default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "opción"
        verbose_name_plural = "opciones"

    def __str__(self):
        return self.text


class Attempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    time_limit_minutes = models.PositiveIntegerField(default=10)
    passing_score = models.PositiveIntegerField(default=70)
    question_ids = models.JSONField(default=list)
    choice_order = models.JSONField(default=dict)
    answers = models.JSONField(default=dict, blank=True)
    score = models.PositiveIntegerField(null=True, blank=True)
    correct_count = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    passed = models.BooleanField(default=False)
    timed_out = models.BooleanField(default=False)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "intento"
        verbose_name_plural = "intentos"

    def __str__(self):
        return f"{self.user} · {self.quiz.course} · {self.score if self.score is not None else '—'}%"

    @property
    def deadline(self):
        return self.started_at + timedelta(minutes=self.time_limit_minutes)

    @property
    def is_finished(self):
        return self.finished_at is not None

    @property
    def remaining_seconds(self):
        return max(0, int((self.deadline - timezone.now()).total_seconds()))

    @property
    def is_expired(self):
        return timezone.now() > self.deadline + timedelta(seconds=GRACE_SECONDS)

    @property
    def status_label(self):
        if not self.is_finished:
            return "En curso"
        return "Aprobado" if self.passed else "Reprobado"

    @property
    def duration_display(self):
        if not self.finished_at:
            return "—"
        secs = int((self.finished_at - self.started_at).total_seconds())
        return f"{secs // 60} min {secs % 60:02d} s"
