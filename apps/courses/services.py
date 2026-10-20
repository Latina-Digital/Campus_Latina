"""Reglas de progreso de cursos: inscripción, lecciones completadas y cierre del curso."""
from dataclasses import dataclass, field

from django.db.models import Count
from django.utils import timezone

from .models import Course, Enrollment, Lesson, LessonProgress


def enroll(user, course):
    enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course)
    return enrollment


def course_has_quiz(course):
    quiz = course.quiz_or_none
    return bool(quiz and quiz.questions.exists())


@dataclass
class CourseProgress:
    lessons: list
    completed_ids: set = field(default_factory=set)
    has_quiz: bool = False
    quiz_passed: bool = False
    best_score: int | None = None

    @property
    def total_units(self):
        return len(self.lessons) + (1 if self.has_quiz else 0)

    @property
    def completed_units(self):
        return len(self.completed_ids) + (1 if self.quiz_passed else 0)

    @property
    def percent(self):
        return round(self.completed_units * 100 / self.total_units) if self.total_units else 0

    @property
    def lessons_done(self):
        return len(self.completed_ids) >= len(self.lessons)

    @property
    def next_lesson(self):
        return next((lesson for lesson in self.lessons if lesson.pk not in self.completed_ids), None)

    @property
    def is_complete(self):
        return self.total_units > 0 and self.completed_units >= self.total_units


def course_progress(user, course):
    from apps.assessments.models import Attempt

    lessons = list(course.lessons.select_related("module"))
    ids = {lesson.pk for lesson in lessons}
    completed = set(
        LessonProgress.objects.filter(user=user, lesson_id__in=ids, completed_at__isnull=False).values_list("lesson_id", flat=True)
    )
    progress = CourseProgress(lessons=lessons, completed_ids=completed, has_quiz=course_has_quiz(course))
    if progress.has_quiz:
        attempts = Attempt.objects.filter(user=user, quiz=course.quiz, finished_at__isnull=False)
        progress.quiz_passed = attempts.filter(passed=True).exists()
        progress.best_score = max((a.score or 0 for a in attempts), default=None)
    return progress


def progress_map(user, courses):
    """Porcentaje de avance por curso para muchas tarjetas con pocas consultas."""
    from apps.assessments.models import Attempt, Quiz

    ids = [c.pk for c in courses]
    if not ids or not user.is_authenticated:
        return {}
    totals = dict(
        Lesson.objects.filter(module__course_id__in=ids)
        .values("module__course_id").annotate(n=Count("id")).values_list("module__course_id", "n")
    )
    done = dict(
        LessonProgress.objects.filter(user=user, completed_at__isnull=False, lesson__module__course_id__in=ids)
        .values("lesson__module__course_id").annotate(n=Count("id")).values_list("lesson__module__course_id", "n")
    )
    with_quiz = set(Quiz.objects.filter(course_id__in=ids, questions__isnull=False).values_list("course_id", flat=True))
    passed = set(Attempt.objects.filter(user=user, passed=True, quiz__course_id__in=ids).values_list("quiz__course_id", flat=True))
    result = {}
    for cid in ids:
        total = totals.get(cid, 0) + (1 if cid in with_quiz else 0)
        completed = done.get(cid, 0) + (1 if cid in passed else 0)
        result[cid] = round(completed * 100 / total) if total else 0
    return result


def complete_lesson(user, lesson):
    progress, _ = LessonProgress.objects.get_or_create(user=user, lesson=lesson)
    if not progress.completed_at:
        progress.completed_at = timezone.now()
        progress.save(update_fields=["completed_at", "updated_at"])
    enrollment = enroll(user, lesson.module.course)
    enrollment.last_lesson = lesson
    enrollment.save(update_fields=["last_lesson", "last_accessed"])
    check_course_completion(user, lesson.module.course)
    return progress


def check_course_completion(user, course, attempt=None):
    """Cierra el curso y emite el certificado cuando se cumplen todos los requisitos."""
    from apps.certificates.services import issue_certificate

    progress = course_progress(user, course)
    if not progress.is_complete:
        return None
    enrollment = enroll(user, course)
    if not enrollment.completed_at:
        enrollment.completed_at = timezone.now()
        enrollment.save(update_fields=["completed_at", "last_accessed"])
    score = attempt.score if attempt else progress.best_score
    return issue_certificate(user, course, score=score, attempt=attempt)


def published_courses():
    return Course.objects.filter(is_published=True).select_related("category")
