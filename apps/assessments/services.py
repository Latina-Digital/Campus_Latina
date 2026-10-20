"""Creación, guardado y calificación de intentos de evaluación."""
import random

from django.db import transaction
from django.utils import timezone

from .models import Attempt, Choice, Question


class QuizError(Exception):
    pass


def finished_attempts(user, quiz):
    return Attempt.objects.filter(user=user, quiz=quiz, finished_at__isnull=False)


def attempts_left(user, quiz):
    """None = ilimitados."""
    if not quiz.max_attempts:
        return None
    return max(0, quiz.max_attempts - finished_attempts(user, quiz).count())


def active_attempt(user, quiz):
    attempt = Attempt.objects.filter(user=user, quiz=quiz, finished_at__isnull=True).first()
    if attempt and attempt.is_expired:
        grade_attempt(attempt, timed_out=True)
        return None
    return attempt


@transaction.atomic
def start_attempt(user, quiz):
    current = active_attempt(user, quiz)
    if current:
        return current
    left = attempts_left(user, quiz)
    if left is not None and left <= 0:
        raise QuizError("Ya usaste todos los intentos permitidos para esta evaluación.")
    questions = list(quiz.questions.prefetch_related("choices"))
    questions = [q for q in questions if q.choices.all()]
    if not questions:
        raise QuizError("Esta evaluación todavía no tiene preguntas configuradas.")
    chosen = random.sample(questions, min(quiz.questions_per_attempt or len(questions), len(questions)))
    order = {}
    for q in chosen:
        ids = [c.pk for c in q.choices.all()]
        random.shuffle(ids)
        order[str(q.pk)] = ids
    return Attempt.objects.create(
        user=user,
        quiz=quiz,
        time_limit_minutes=quiz.time_limit_minutes,
        passing_score=quiz.passing_score,
        question_ids=[q.pk for q in chosen],
        choice_order=order,
        total=len(chosen),
    )


def clean_answers(attempt, raw):
    """Acepta solo respuestas a preguntas y opciones de este intento."""
    cleaned = {}
    for qid, cid in (raw or {}).items():
        qid = str(qid)
        try:
            cid = int(cid)
        except (TypeError, ValueError):
            continue
        if cid in attempt.choice_order.get(qid, []):
            cleaned[qid] = cid
    return cleaned


def save_answers(attempt, raw):
    if attempt.is_finished or attempt.is_expired:
        return False
    attempt.answers = {**attempt.answers, **clean_answers(attempt, raw)}
    attempt.save(update_fields=["answers"])
    return True


@transaction.atomic
def grade_attempt(attempt, raw_answers=None, timed_out=False):
    attempt = Attempt.objects.select_for_update().get(pk=attempt.pk)
    if attempt.is_finished:
        return attempt
    if raw_answers is not None and not attempt.is_expired:
        attempt.answers = {**attempt.answers, **clean_answers(attempt, raw_answers)}
    if attempt.is_expired:
        timed_out = True
    correct_ids = set(
        Choice.objects.filter(question_id__in=attempt.question_ids, is_correct=True).values_list("pk", flat=True)
    )
    correct = sum(1 for cid in attempt.answers.values() if cid in correct_ids)
    attempt.correct_count = correct
    attempt.total = len(attempt.question_ids)
    attempt.score = round(correct * 100 / attempt.total) if attempt.total else 0
    attempt.passed = attempt.score >= attempt.passing_score
    attempt.timed_out = timed_out
    attempt.finished_at = timezone.now()
    attempt.save()
    if attempt.passed:
        from apps.courses.services import check_course_completion

        check_course_completion(attempt.user, attempt.quiz.course, attempt=attempt)
    return attempt


def attempt_questions(attempt, with_answers=False):
    """Preguntas del intento en el orden sorteado, listas para la plantilla."""
    questions = Question.objects.filter(pk__in=attempt.question_ids).prefetch_related("choices")
    by_id = {q.pk: q for q in questions}
    items = []
    for number, qid in enumerate(attempt.question_ids, start=1):
        question = by_id.get(qid)
        if not question:
            continue
        choices = {c.pk: c for c in question.choices.all()}
        chosen = attempt.answers.get(str(qid))
        options = []
        for letter, cid in zip("ABCDEFGH", attempt.choice_order.get(str(qid), [])):
            choice = choices.get(cid)
            if not choice:
                continue
            option = {"id": cid, "letter": letter, "text": choice.text, "chosen": cid == chosen}
            if with_answers:
                option["is_correct"] = choice.is_correct
            options.append(option)
        item = {"id": qid, "number": number, "text": question.text, "options": options, "answered": chosen is not None}
        if with_answers:
            item["explanation"] = question.explanation
            item["is_correct"] = any(o["chosen"] and o["is_correct"] for o in options)
        items.append(item)
    return items
