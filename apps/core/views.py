import mimetypes
import os
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import SuspiciousFileOperation
from django.db.models import Count
from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.utils._os import safe_join

from apps.catalog.models import Product
from apps.certificates.models import Certificate
from apps.courses.models import Category, Course, Lesson

from .gamification import LEVELS, POINTS_CERTIFICATE, POINTS_LESSON, leaderboard

# Carpetas de /media/ que requieren sesión iniciada.
PRIVATE_MEDIA = ("lessons/", "resources/")


def landing(request):
    if request.user.is_authenticated:
        return redirect("courses:home")
    published = Course.objects.filter(is_published=True)
    context = {
        "featured": published.select_related("category").order_by("-is_featured", "order")[:6],
        "categories": Category.objects.annotate(n=Count("courses")).filter(n__gt=0)[:8],
        "stats": {
            "courses": published.count(),
            "lessons": Lesson.objects.filter(module__course__is_published=True).count(),
            "certificates": Certificate.objects.filter(is_revoked=False).count(),
            "products": Product.objects.filter(is_active=True).count(),
        },
    }
    return render(request, "core/landing.html", context)


@login_required
def ranking(request):
    rows = leaderboard()
    context = {
        "podium": rows[:3],
        "rows": rows[3:50],
        "me": next((r for r in rows if r["user"].pk == request.user.pk), None),
        "levels": LEVELS,
        "points_lesson": POINTS_LESSON,
        "points_cert": POINTS_CERTIFICATE,
    }
    return render(request, "core/ranking.html", context)


def serve_media(request, path):
    """Sirve archivos subidos con soporte de rangos HTTP (necesario para adelantar/retomar videos)."""
    if path.startswith(PRIVATE_MEDIA) and not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    try:
        full_path = safe_join(settings.MEDIA_ROOT, path)
    except (SuspiciousFileOperation, ValueError):
        raise Http404
    if not os.path.isfile(full_path):
        raise Http404
    size = os.path.getsize(full_path)
    content_type = mimetypes.guess_type(full_path)[0] or "application/octet-stream"
    match = re.match(r"bytes=(\d*)-(\d*)", request.headers.get("Range", ""))
    if match and (match.group(1) or match.group(2)):
        if match.group(1):
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else size - 1
        else:
            start, end = max(0, size - int(match.group(2))), size - 1
        end = min(end, size - 1)
        if start > end:
            return HttpResponse(status=416, headers={"Content-Range": f"bytes */{size}"})
        length = end - start + 1

        def stream(remaining=length):
            with open(full_path, "rb") as fh:
                fh.seek(start)
                while remaining > 0:
                    chunk = fh.read(min(256 * 1024, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        response = StreamingHttpResponse(stream(), status=206, content_type=content_type)
        response["Content-Length"] = str(length)
        response["Content-Range"] = f"bytes {start}-{end}/{size}"
    else:
        response = FileResponse(open(full_path, "rb"), content_type=content_type)
    response["Accept-Ranges"] = "bytes"
    response["Cache-Control"] = "private, max-age=3600"
    return response


def error_404(request, exception=None):
    return render(request, "core/404.html", status=404)
