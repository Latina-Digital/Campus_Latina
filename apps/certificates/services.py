from decimal import Decimal

from .models import Certificate


def issue_certificate(user, course, score=None, attempt=None):
    hours = max(Decimal("0.5"), round(Decimal(course.total_minutes) / 60, 1))
    certificate, created = Certificate.objects.get_or_create(
        user=user,
        course=course,
        defaults={
            "score": score,
            "attempt": attempt,
            "hours": hours,
            "holder_name": user.display_name.title(),
            "course_title": course.title,
        },
    )
    if not created and score is not None and (certificate.score or 0) < score:
        certificate.score = score
        certificate.attempt = attempt
        certificate.save(update_fields=["score", "attempt"])
    return certificate
