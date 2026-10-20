"""Puntos, niveles, insignias y rankings del campus."""
from collections import defaultdict

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Max

POINTS_LESSON = 10
POINTS_CERTIFICATE = 50

LEVELS = [
    (0, "Aprendiz", "sprout"),
    (150, "Asesor", "badge-check"),
    (400, "Especialista", "award"),
    (800, "Experto", "medal"),
    (1500, "Maestro Latina", "crown"),
]


def level_info(points):
    current = LEVELS[0]
    nxt = None
    for i, lvl in enumerate(LEVELS):
        if points >= lvl[0]:
            current = lvl
            nxt = LEVELS[i + 1] if i + 1 < len(LEVELS) else None
    if nxt:
        span = nxt[0] - current[0]
        progress = round((points - current[0]) * 100 / span)
    else:
        progress = 100
    return {
        "name": current[1],
        "icon": current[2],
        "number": LEVELS.index(current) + 1,
        "next_name": nxt[1] if nxt else None,
        "next_points": nxt[0] if nxt else None,
        "missing": (nxt[0] - points) if nxt else 0,
        "progress": progress,
    }


def _scores(since=None, user_ids=None):
    from apps.assessments.models import Attempt
    from apps.certificates.models import Certificate
    from apps.courses.models import LessonProgress

    lessons = LessonProgress.objects.filter(completed_at__isnull=False)
    certs = Certificate.objects.filter(is_revoked=False)
    passed = Attempt.objects.filter(passed=True)
    finished = Attempt.objects.filter(finished_at__isnull=False)
    if since:
        lessons = lessons.filter(completed_at__gte=since)
        certs = certs.filter(issued_at__gte=since)
        passed = passed.filter(finished_at__gte=since)
        finished = finished.filter(finished_at__gte=since)
    if user_ids is not None:
        lessons = lessons.filter(user_id__in=user_ids)
        certs = certs.filter(user_id__in=user_ids)
        passed = passed.filter(user_id__in=user_ids)
        finished = finished.filter(user_id__in=user_ids)

    data = defaultdict(lambda: {"lessons": 0, "certs": 0, "quiz_points": 0, "avg": None})
    for row in lessons.values("user_id").annotate(n=Count("id")):
        data[row["user_id"]]["lessons"] = row["n"]
    for row in certs.values("user_id").annotate(n=Count("id")):
        data[row["user_id"]]["certs"] = row["n"]
    for row in passed.values("user_id", "quiz_id").annotate(best=Max("score")):
        data[row["user_id"]]["quiz_points"] += row["best"] or 0
    for row in finished.values("user_id").annotate(avg=Avg("score")):
        data[row["user_id"]]["avg"] = round(row["avg"] or 0)
    for d in data.values():
        d["points"] = d["lessons"] * POINTS_LESSON + d["certs"] * POINTS_CERTIFICATE + d["quiz_points"]
    return data


def user_points(user):
    return _scores(user_ids=[user.pk]).get(user.pk, {"points": 0, "lessons": 0, "certs": 0, "quiz_points": 0, "avg": None})


def leaderboard(since=None, roles=None):
    User = get_user_model()
    users = User.objects.filter(is_active=True, is_superuser=False)
    if roles:
        users = users.filter(role__in=roles)
    users = {u.pk: u for u in users}
    scores = _scores(since=since, user_ids=list(users))
    rows = []
    for uid, s in scores.items():
        if uid in users and s["points"] > 0:
            rows.append({"user": users[uid], **s})
    rows.sort(key=lambda r: (-r["points"], -(r["avg"] or 0), r["user"].display_name))
    for i, row in enumerate(rows, start=1):
        row["rank"] = i
        row["level"] = level_info(row["points"])
    return rows


def team_leaderboard(since=None):
    User = get_user_model()
    members = User.objects.filter(is_active=True, is_superuser=False).exclude(supervisor="")
    scores = _scores(since=since, user_ids=list(members.values_list("pk", flat=True)))
    teams = defaultdict(lambda: {"members": 0, "points": 0, "certs": 0, "avgs": []})
    for user in members:
        key = user.supervisor.strip().upper()
        s = scores.get(user.pk)
        team = teams[key]
        team["members"] += 1
        if s:
            team["points"] += s["points"]
            team["certs"] += s["certs"]
            if s["avg"] is not None:
                team["avgs"].append(s["avg"])
    rows = []
    for name, t in teams.items():
        if not t["points"]:
            continue
        rows.append(
            {
                "name": name.title(),
                "members": t["members"],
                "points": round(t["points"] / t["members"]),
                "certs": t["certs"],
                "avg": round(sum(t["avgs"]) / len(t["avgs"])) if t["avgs"] else None,
            }
        )
    rows.sort(key=lambda r: (-r["points"], -(r["avg"] or 0)))
    for i, row in enumerate(rows, start=1):
        row["rank"] = i
    return rows


def user_badges(user, stats=None):
    from apps.assessments.models import Attempt
    from apps.courses.models import LearningPath

    stats = stats or user_points(user)
    perfect = Attempt.objects.filter(user=user, score=100).exists()
    reviews = user.reviews.exists()
    certified_courses = set(user.certificates.filter(is_revoked=False).values_list("course_id", flat=True))
    path_done = any(
        (ids := [c.pk for c in path.ordered_courses]) and set(ids) <= certified_courses
        for path in LearningPath.objects.filter(is_published=True).prefetch_related("steps__course")
    )
    return [
        {"name": "Primer paso", "icon": "footprints", "desc": "Completa tu primera lección.", "earned": stats["lessons"] >= 1},
        {"name": "Constante", "icon": "flame", "desc": "Completa 20 lecciones.", "earned": stats["lessons"] >= 20},
        {"name": "Certificado", "icon": "award", "desc": "Obtén tu primer certificado.", "earned": stats["certs"] >= 1},
        {"name": "Coleccionista", "icon": "library", "desc": "Obtén 5 certificados.", "earned": stats["certs"] >= 5},
        {"name": "Nota perfecta", "icon": "target", "desc": "Saca 100% en una evaluación.", "earned": perfect},
        {"name": "Ruta completa", "icon": "route", "desc": "Termina una ruta de aprendizaje.", "earned": path_done},
        {"name": "Voz del equipo", "icon": "message-square-heart", "desc": "Califica un curso.", "earned": reviews},
    ]
