from django.conf import settings
from django.utils.functional import SimpleLazyObject

from .gamification import level_info, user_points


def campus(request):
    ctx = {
        "CAMPUS_NAME": settings.CAMPUS_NAME,
        "CAMPUS_COMPANY": settings.CAMPUS_COMPANY,
        "CAMPUS_SIGNER_1": settings.CAMPUS_SIGNER_1,
        "CAMPUS_SIGNER_2": settings.CAMPUS_SIGNER_2,
    }
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        def _stats():
            stats = user_points(user)
            return {**stats, "level": level_info(stats["points"])}

        ctx["my_stats"] = SimpleLazyObject(_stats)
    return ctx
