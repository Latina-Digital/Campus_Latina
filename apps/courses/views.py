import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.assessments.services import attempts_left, finished_attempts
from apps.core.choices import Brand, Level
from apps.core.gamification import leaderboard
from apps.core.models import Announcement

from .models import Category, Course, Enrollment, LearningPath, Lesson, LessonProgress, Review
from .services import complete_lesson, course_progress, enroll, progress_map, published_courses

SORTS = {
    "populares": ("-n_enrolled", "order"),
    "recientes": ("-created_at",),
    "valorados": ("-rating", "-n_reviews"),
    "az": ("title",),
}


def visible_courses(user):
    qs = Course.objects.select_related("category")
    return qs if user.is_staff else qs.filter(is_published=True)


def path_progress(user, paths):
    certified = set(user.certificates.filter(is_revoked=False).values_list("course_id", flat=True))
    result = []
    for path in paths:
        courses = path.ordered_courses
        done = sum(1 for c in courses if c.pk in certified)
        result.append({
            "path": path,
            "courses": courses,
            "done": done,
            "percent": round(done * 100 / len(courses)) if courses else 0,
            "next": next((c for c in courses if c.pk not in certified and not c.coming_soon), None),
        })
    return result


@login_required
def home(request):
    user = request.user
    enrollments = list(
        Enrollment.objects.filter(user=user, course__is_published=True).select_related("course", "course__category", "last_lesson")
    )
    in_progress = [e for e in enrollments if not e.completed_at][:6]
    enrolled_ids = {e.course_id for e in enrollments}
    published = published_courses()
    mandatory = [c for c in published.filter(is_mandatory=True) if not user.certificates.filter(course=c).exists()]
    recommended = list(published.exclude(pk__in=enrolled_ids).order_by("-is_featured", "order")[:8])
    progress = progress_map(user, [e.course for e in in_progress] + mandatory + recommended)
    board = leaderboard()
    my_rank = next((r["rank"] for r in board if r["user"].pk == user.pk), None)
    context = {
        "in_progress": in_progress,
        "mandatory": mandatory,
        "recommended": recommended,
        "progress": progress,
        "completed_count": sum(1 for e in enrollments if e.completed_at),
        "courses_total": published.filter(coming_soon=False).count(),
        "paths": path_progress(user, LearningPath.objects.filter(is_published=True).prefetch_related("steps__course")[:3]),
        "announcements": Announcement.objects.filter(is_active=True)[:3],
        "categories": Category.objects.annotate(n=Count("courses", filter=Q(courses__is_published=True))).filter(n__gt=0),
        "my_rank": my_rank,
        "ranking_total": len(board),
        "top3": board[:3],
        "recent_certs": user.certificates.filter(is_revoked=False)[:3],
    }
    return render(request, "courses/home.html", context)


@login_required
def explore(request):
    qs = visible_courses(request.user).annotate(
        n_enrolled=Count("enrollments", distinct=True),
        n_reviews=Count("reviews", distinct=True),
        rating=Avg("reviews__rating"),
        n_lessons=Count("modules__lessons", distinct=True),
    )
    q = request.GET.get("q", "").strip()
    brand = request.GET.get("marca", "")
    category = request.GET.get("categoria", "")
    level = request.GET.get("nivel", "")
    sort = request.GET.get("orden", "populares")
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(summary__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q)
            | Q(related_products__name__icontains=q)
        ).distinct()
    if brand:
        qs = qs.filter(brand=brand)
    if category:
        qs = qs.filter(category__slug=category)
    if level:
        qs = qs.filter(level=level)
    qs = qs.order_by(*SORTS.get(sort, SORTS["populares"]))
    page = Paginator(qs, 12).get_page(request.GET.get("page"))
    context = {
        "page": page,
        "total": page.paginator.count,
        "progress": progress_map(request.user, list(page.object_list)),
        "saved_ids": set(request.user.saved_courses.values_list("pk", flat=True)),
        "categories": Category.objects.annotate(n=Count("courses", filter=Q(courses__is_published=True))),
        "brands": Brand.choices,
        "levels": Level.choices,
        "filters": {"q": q, "marca": brand, "categoria": category, "nivel": level, "orden": sort},
        "has_filters": any([q, brand, category, level]),
    }
    return render(request, "courses/explore.html", context)


@login_required
def course_detail(request, slug):
    course = get_object_or_404(visible_courses(request.user), slug=slug)
    user = request.user
    if course.coming_soon:
        messages.info(request, "Este curso estará disponible próximamente.")
        return redirect("courses:explore")
    modules = course.modules.prefetch_related("lessons")
    progress = course_progress(user, course)
    reviews = course.reviews.select_related("user")
    agg = reviews.aggregate(avg=Avg("rating"), n=Count("id"))
    distribution = {i: 0 for i in range(5, 0, -1)}
    for rating in reviews.values_list("rating", flat=True):
        distribution[rating] += 1
    quiz = course.quiz_or_none
    context = {
        "course": course,
        "modules": modules,
        "progress": progress,
        "enrollment": Enrollment.objects.filter(user=user, course=course).first(),
        "reviews": reviews[:6],
        "rating_avg": agg["avg"] or 0,
        "rating_count": agg["n"],
        "distribution": [(k, v, round(v * 100 / agg["n"]) if agg["n"] else 0) for k, v in distribution.items()],
        "my_review": reviews.filter(user=user).first(),
        "quiz": quiz if progress.has_quiz else None,
        "attempts_left": attempts_left(user, quiz) if progress.has_quiz else None,
        "attempts_used": finished_attempts(user, quiz).count() if progress.has_quiz else 0,
        "certificate": user.certificates.filter(course=course).first(),
        "is_saved": course.saved_by.filter(pk=user.pk).exists(),
        "learners": course.enrollments.count(),
        "paths": LearningPath.objects.filter(is_published=True, steps__course=course),
        "related": published_courses().filter(category=course.category).exclude(pk=course.pk)[:3],
        "products": course.related_products.filter(is_active=True),
        "resources": course.resources.all(),
    }
    return render(request, "courses/detail.html", context)


@login_required
@require_POST
def course_start(request, slug):
    course = get_object_or_404(visible_courses(request.user), slug=slug)
    if course.coming_soon:
        messages.info(request, "Este curso estará disponible próximamente.")
        return redirect("courses:explore")
    enrollment = enroll(request.user, course)
    progress = course_progress(request.user, course)
    target = progress.next_lesson or enrollment.last_lesson or (progress.lessons[0] if progress.lessons else None)
    if target:
        return redirect(target.get_absolute_url())
    if progress.has_quiz:
        return redirect("assessments:intro", slug=course.slug)
    messages.info(request, "Este curso aún no tiene lecciones publicadas.")
    return redirect(course.get_absolute_url())


@login_required
def lesson_view(request, slug, lesson_id):
    course = get_object_or_404(visible_courses(request.user), slug=slug)
    if course.coming_soon:
        messages.info(request, "Este curso estará disponible próximamente.")
        return redirect("courses:explore")
    lesson = get_object_or_404(Lesson.objects.select_related("module"), pk=lesson_id, module__course=course)
    enrollment = enroll(request.user, course)
    enrollment.last_lesson = lesson
    enrollment.save(update_fields=["last_lesson", "last_accessed"])
    progress = course_progress(request.user, course)
    lesson_state, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    lessons = progress.lessons
    index = next(i for i, item in enumerate(lessons) if item.pk == lesson.pk)
    context = {
        "course": course,
        "lesson": lesson,
        "modules": course.modules.prefetch_related("lessons"),
        "progress": progress,
        "state": lesson_state,
        "number": index + 1,
        "prev_lesson": lessons[index - 1] if index > 0 else None,
        "next_lesson": lessons[index + 1] if index + 1 < len(lessons) else None,
        "can_skip": request.user.is_staff or bool(lesson_state.completed_at) or not lesson.require_full_watch,
        "quiz": course.quiz_or_none if progress.has_quiz else None,
    }
    return render(request, "courses/lesson.html", context)


def _json_body(request):
    try:
        return json.loads(request.body or "{}")
    except ValueError:
        return {}


@login_required
@require_POST
def lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson.objects.select_related("module__course"), pk=lesson_id)
    course = lesson.module.course
    if course.coming_soon:
        return JsonResponse({"ok": False}, status=403)
    complete_lesson(request.user, lesson)
    progress = course_progress(request.user, course)
    certificate = request.user.certificates.filter(course=course).first()
    return JsonResponse(
        {
            "ok": True,
            "percent": progress.percent,
            "lessons_done": progress.lessons_done,
            "certificate_url": certificate.get_absolute_url() if certificate else None,
        }
    )


@login_required
@require_POST
def lesson_position(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    data = _json_body(request)
    try:
        position = max(0.0, float(data.get("position", 0)))
        furthest = max(0.0, float(data.get("max", 0)))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False}, status=400)
    state, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    state.position_seconds = position
    state.max_position_seconds = max(state.max_position_seconds, furthest)
    state.save(update_fields=["position_seconds", "max_position_seconds", "updated_at"])
    return JsonResponse({"ok": True})


@login_required
@require_POST
def toggle_save(request, slug):
    course = get_object_or_404(visible_courses(request.user), slug=slug)
    if course.saved_by.filter(pk=request.user.pk).exists():
        course.saved_by.remove(request.user)
        saved = False
    else:
        course.saved_by.add(request.user)
        saved = True
    if request.headers.get("Accept") == "application/json":
        return JsonResponse({"saved": saved})
    return redirect(request.META.get("HTTP_REFERER") or course.get_absolute_url())


@login_required
@require_POST
def review_submit(request, slug):
    course = get_object_or_404(visible_courses(request.user), slug=slug)
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "Inscríbete en el curso para poder calificarlo.")
        return redirect(course.get_absolute_url())
    try:
        rating = int(request.POST.get("rating", 0))
    except ValueError:
        rating = 0
    if not 1 <= rating <= 5:
        messages.error(request, "Elige una calificación de 1 a 5 estrellas.")
        return redirect(course.get_absolute_url() + "#resenas")
    Review.objects.update_or_create(
        user=request.user, course=course, defaults={"rating": rating, "comment": request.POST.get("comment", "")[:800]}
    )
    messages.success(request, "¡Gracias por tu opinión!")
    return redirect(course.get_absolute_url() + "#resenas")


@login_required
def my_learning(request):
    """Rutas de aprendizaje (con los cursos de la ruta elegida) y los cursos propios por estado."""
    tab = request.GET.get("tab", "en-curso")
    user = request.user
    paths = path_progress(user, LearningPath.objects.filter(is_published=True).prefetch_related("steps__course"))
    selected = next((p for p in paths if p["path"].slug == request.GET.get("ruta")), paths[0] if paths else None)
    enrollments = Enrollment.objects.filter(user=user, course__is_published=True).select_related("course", "course__category")
    if tab == "completados":
        courses = [e.course for e in enrollments.filter(completed_at__isnull=False)]
    elif tab == "guardados":
        courses = list(user.saved_courses.filter(is_published=True).select_related("category"))
    else:
        tab = "en-curso"
        courses = [e.course for e in enrollments.filter(completed_at__isnull=True)]
    context = {
        "paths": paths,
        "selected": selected,
        "path_progress": progress_map(user, selected["courses"]) if selected else {},
        "tab": tab,
        "courses": courses,
        "progress": progress_map(user, courses),
        "counts": {
            "en_curso": enrollments.filter(completed_at__isnull=True).count(),
            "completados": enrollments.filter(completed_at__isnull=False).count(),
            "guardados": user.saved_courses.filter(is_published=True).count(),
        },
        "attempts": user.attempts.filter(finished_at__isnull=False).select_related("quiz__course")[:10],
    }
    return render(request, "courses/my_learning.html", context)


# Las rutas se ven dentro de "Mi aprendizaje"; estas direcciones se mantienen por los enlaces ya compartidos.
def paths(request):
    return redirect(reverse("courses:my_learning") + "#rutas")


def path_detail(request, slug):
    return redirect(reverse("courses:my_learning") + f"?ruta={slug}#rutas")
