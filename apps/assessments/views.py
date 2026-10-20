import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.courses.models import Course
from apps.courses.services import course_progress, enroll

from .models import Attempt
from .services import QuizError, active_attempt, attempt_questions, attempts_left, finished_attempts, grade_attempt, save_answers, start_attempt


def _course_with_quiz(request, slug):
    qs = Course.objects.all() if request.user.is_staff else Course.objects.filter(is_published=True)
    course = get_object_or_404(qs, slug=slug)
    quiz = course.quiz_or_none
    if not quiz or not quiz.questions.exists():
        raise Http404("Este curso no tiene evaluación.")
    return course, quiz


def _own_attempt(request, pk):
    attempt = get_object_or_404(Attempt.objects.select_related("quiz__course", "user"), pk=pk)
    if attempt.user != request.user and not request.user.is_staff:
        raise Http404
    return attempt


@login_required
def intro(request, slug):
    course, quiz = _course_with_quiz(request, slug)
    progress = course_progress(request.user, course)
    unlocked = progress.lessons_done or request.user.is_staff
    left = attempts_left(request.user, quiz)
    if request.method == "POST":
        if not unlocked:
            messages.warning(request, "Completa todas las lecciones para habilitar la evaluación.")
            return redirect("assessments:intro", slug=slug)
        try:
            enroll(request.user, course)
            attempt = start_attempt(request.user, quiz)
        except QuizError as exc:
            messages.error(request, str(exc))
            return redirect("assessments:intro", slug=slug)
        return redirect("assessments:take", pk=attempt.pk)
    context = {
        "course": course,
        "quiz": quiz,
        "progress": progress,
        "unlocked": unlocked,
        "attempts_left": left,
        "active": active_attempt(request.user, quiz),
        "history": finished_attempts(request.user, quiz),
        "certificate": request.user.certificates.filter(course=course).first(),
    }
    return render(request, "assessments/intro.html", context)


@login_required
def take(request, pk):
    attempt = _own_attempt(request, pk)
    if attempt.user != request.user:
        raise Http404
    if attempt.is_finished:
        return redirect("assessments:result", pk=attempt.pk)
    if attempt.is_expired:
        grade_attempt(attempt, timed_out=True)
        return redirect("assessments:result", pk=attempt.pk)
    context = {
        "attempt": attempt,
        "course": attempt.quiz.course,
        "quiz": attempt.quiz,
        "questions": attempt_questions(attempt),
        "remaining": attempt.remaining_seconds,
    }
    return render(request, "assessments/take.html", context)


@login_required
@require_POST
def autosave(request, pk):
    attempt = _own_attempt(request, pk)
    try:
        data = json.loads(request.body or "{}")
    except ValueError:
        return JsonResponse({"ok": False}, status=400)
    ok = attempt.user == request.user and save_answers(attempt, data.get("answers", {}))
    return JsonResponse({"ok": ok, "remaining": attempt.remaining_seconds})


@login_required
@require_POST
def submit(request, pk):
    attempt = _own_attempt(request, pk)
    if attempt.user != request.user:
        raise Http404
    answers = {key[2:]: value for key, value in request.POST.items() if key.startswith("q_")}
    attempt = grade_attempt(attempt, answers, timed_out=request.POST.get("timeout") == "1")
    return redirect("assessments:result", pk=attempt.pk)


@login_required
def result(request, pk):
    attempt = _own_attempt(request, pk)
    if not attempt.is_finished:
        return redirect("assessments:take", pk=attempt.pk)
    quiz = attempt.quiz
    show_review = quiz.show_review or request.user.is_staff
    context = {
        "attempt": attempt,
        "quiz": quiz,
        "course": quiz.course,
        "items": attempt_questions(attempt, with_answers=True) if show_review else [],
        "show_review": show_review,
        "certificate": attempt.user.certificates.filter(course=quiz.course).first() if attempt.passed else None,
        "attempts_left": attempts_left(attempt.user, quiz),
        "celebrate": attempt.passed and (timezone.now() - attempt.finished_at).total_seconds() < 60,
    }
    return render(request, "assessments/result.html", context)
