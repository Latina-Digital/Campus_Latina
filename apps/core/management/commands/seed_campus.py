"""
Carga los datos iniciales del campus.

    python manage.py seed_campus                      # admin + contenido de ejemplo
    python manage.py seed_campus --demo               # además, usuarios demo con actividad
    python manage.py seed_campus --remove-demo        # elimina los usuarios demo
    python manage.py seed_campus --admin-password X   # define la clave del admin
"""
import io
import random
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFilter

from apps.accounts.models import User
from apps.assessments.models import Attempt, Choice, Question, Quiz
from apps.catalog.models import Product, ProductLine
from apps.core import seed_data as data
from apps.core.models import Announcement
from apps.courses.models import Category, Course, Enrollment, LearningPath, Lesson, LessonProgress, Module, PathStep, Review
from apps.courses.services import check_course_completion

ASSETS = Path(__file__).resolve().parents[2] / "seed_assets"
LOGO_MARK = settings.BASE_DIR / "static" / "img" / "logo-mark.png"
DEMO_PASSWORD = "Demo2026*"
DEFAULT_ADMIN_PASSWORD = "Latina2026*"

PALETTES = {
    "latina": ((6, 18, 48), (18, 64, 143), (250, 204, 0)),
    "induless": ((80, 0, 8), (227, 0, 15), (255, 255, 255)),
    "corporativo": ((10, 28, 64), (16, 41, 90), (227, 0, 15)),
}


def _gradient(size, c1, c2):
    w, h = size
    base = Image.new("RGB", size, c1)
    top = Image.new("RGB", size, c2)
    mask = Image.linear_gradient("L").rotate(-90).resize(size)
    return Image.composite(top, base, mask)


def _fit(img, max_w, max_h):
    scale = min(max_w / img.width, max_h / img.height)
    return img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)


def _to_file(img, name, fmt="JPEG"):
    buf = io.BytesIO()
    img.convert("RGB").save(buf, fmt, quality=88)
    return ContentFile(buf.getvalue(), name=name)


def product_image(key):
    src = Image.open(ASSETS / f"prod-{key}.jpg").convert("RGB")
    size = 800
    canvas = _gradient((size, size), (6, 18, 48), (22, 52, 112))
    glow = Image.new("L", (size, size), 0)
    ImageDraw.Draw(glow).ellipse((120, 120, 680, 680), fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    canvas = Image.composite(Image.new("RGB", (size, size), (60, 100, 190)), canvas, glow)
    src = _fit(src, 600, 600)
    x, y = (size - src.width) // 2, (size - src.height) // 2
    canvas.paste(src, (x, y))
    return _to_file(canvas, f"{key}.jpg")


def course_cover(brand, product_key, seed):
    w, h = 1280, 720
    dark, light, accent = PALETTES.get(brand, PALETTES["latina"])
    img = _gradient((w, h), dark, light).convert("RGBA")
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((w - 520, -220, w + 180, 480), outline=accent + (70,), width=46)
    d.polygon([(0, h), (0, h - 70), (w, h - 190), (w, h - 120)], fill=(227, 0, 15, 200) if brand != "induless" else (250, 204, 0, 190))
    d.polygon([(0, h), (w, h - 120), (w, h)], fill=(255, 255, 255, 28))
    rnd = random.Random(seed)
    for _ in range(14):
        cx, cy, r = rnd.randint(0, w), rnd.randint(0, h), rnd.randint(2, 5)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, 60))
    img = Image.alpha_composite(img, layer)
    if product_key:
        prod = Image.open(ASSETS / f"prod-{product_key}.jpg").convert("RGBA")
        prod = _fit(prod, 520, 500)
        mask = Image.new("L", prod.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, prod.width, prod.height), radius=28, fill=255)
        shadow = Image.new("RGBA", (prod.width + 80, prod.height + 80), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle((40, 50, prod.width + 40, prod.height + 50), radius=28, fill=(0, 0, 0, 150))
        shadow = shadow.filter(ImageFilter.GaussianBlur(22))
        px, py = w - prod.width - 110, (h - prod.height) // 2 - 20
        img.alpha_composite(shadow, (px - 40, py - 40))
        img.paste(prod, (px, py), mask)
    else:
        mark = Image.open(LOGO_MARK).convert("RGBA")
        mark.thumbnail((330, 480))
        img.alpha_composite(mark, (w - mark.width - 170, (h - mark.height) // 2 - 30))
    return _to_file(img, f"cover-{seed}.jpg")


class Command(BaseCommand):
    help = "Crea el usuario administrador y el contenido inicial del campus."

    def add_arguments(self, parser):
        parser.add_argument("--admin-user", default="admin")
        parser.add_argument("--admin-password", default=None, help=f"Por defecto {DEFAULT_ADMIN_PASSWORD} al crearlo.")
        parser.add_argument("--demo", action="store_true", help="Crea usuarios demo con actividad para ver el ranking y los gráficos.")
        parser.add_argument("--remove-demo", action="store_true", help="Elimina los usuarios demo.")

    def handle(self, *args, **opts):
        if opts["remove_demo"]:
            usernames = [u[0] for u in data.DEMO_USERS] + [s[0] for s in data.DEMO_SUPERVISORS]
            n, _ = User.objects.filter(username__in=usernames).delete()
            self.stdout.write(self.style.SUCCESS(f"Usuarios demo eliminados ({n} registros)."))
            return
        with transaction.atomic():
            admin = self.create_admin(opts["admin_user"], opts["admin_password"])
            if not Course.objects.exists():
                self.create_content()
            else:
                self.stdout.write("Ya existen cursos: se omite el contenido de ejemplo.")
            if opts["demo"]:
                self.create_demo()
        self.stdout.write(self.style.SUCCESS("\nCampus listo."))
        self.stdout.write(f"  Usuario administrador: {admin.username}")
        if admin.password_set:
            self.stdout.write(f"  Contraseña:            {admin.password_set}  (cámbiala al ingresar)")

    def create_admin(self, username, password):
        admin, created = User.objects.get_or_create(
            username=username,
            defaults={"first_name": "Administrador", "last_name": "Campus", "email": "", "role": User.Role.ADMIN, "headline": "Administración del Campus Latina"},
        )
        admin.is_superuser = True
        admin.role = User.Role.ADMIN
        admin.is_active = True
        admin.password_set = None
        if created or password:
            admin.password_set = password or DEFAULT_ADMIN_PASSWORD
            admin.set_password(admin.password_set)
        admin.save()
        self.stdout.write(("Creado" if created else "Actualizado") + f" el administrador «{username}».")
        return admin

    def create_content(self):
        categories = {}
        for i, (name, icon, desc) in enumerate(data.CATEGORIES):
            categories[name] = Category.objects.create(name=name, icon=icon, description=desc, order=i)
        lines = {}
        for i, (name, icon) in enumerate(data.PRODUCT_LINES):
            lines[name] = ProductLine.objects.create(name=name, icon=icon, order=i)
        products = {}
        for i, p in enumerate(data.PRODUCTS):
            product = Product(
                name=p["name"], brand=p["brand"], line=lines[p["line"]], summary=p["summary"], description=p["description"],
                features=p["features"], uses=p["uses"], presentations=p["presentations"], order=i,
            )
            if p["image"]:
                product.image = product_image(p["image"])
            product.save()
            products[p["name"]] = product
        self.stdout.write(f"{len(products)} productos y {len(categories)} categorías creados.")

        courses = []
        for i, c in enumerate(data.COURSES):
            course = Course(
                title=c["title"], brand=c["brand"], category=categories[c["category"]], level=c["level"], summary=c["summary"],
                description=c["description"], outcomes=c["outcomes"], is_published=True, is_featured=c.get("featured", False),
                is_mandatory=c.get("mandatory", False), order=i,
            )
            course.cover = course_cover(c["brand"], c["image"], i + 1)
            course.save()
            course.related_products.set([products[name] for name in c["products"]])
            for m_order, (m_title, lessons) in enumerate(c["modules"], start=1):
                module = Module.objects.create(course=course, title=m_title, order=m_order)
                for l_order, (l_title, minutes, html) in enumerate(lessons, start=1):
                    Lesson.objects.create(module=module, title=l_title, kind=Lesson.Kind.LECTURA, duration_minutes=minutes, content=html.strip(), order=l_order)
            quiz = Quiz.objects.create(course=course, time_limit_minutes=10, questions_per_attempt=10, passing_score=70)
            for q_order, (text, options, correct, explanation) in enumerate(c["questions"], start=1):
                question = Question.objects.create(quiz=quiz, text=text, explanation=explanation, order=q_order)
                Choice.objects.bulk_create([Choice(question=question, text=t, is_correct=j == correct, order=j) for j, t in enumerate(options)])
            courses.append(course)
        self.stdout.write(f"{len(courses)} cursos con lecciones y evaluaciones creados.")

        for i, p in enumerate(data.PATHS):
            path = LearningPath.objects.create(title=p["title"], brand=p["brand"], summary=p["summary"], description=p["description"], order=i)
            for order, idx in enumerate(p["courses"], start=1):
                PathStep.objects.create(path=path, course=courses[idx], order=order)
        Announcement.objects.create(
            title="¡Te damos la bienvenida al nuevo Campus Latina!",
            body="Ahora puedes aprender a tu ritmo, rendir evaluaciones, ganar puntos y descargar certificados verificables. Empieza por el curso obligatorio de Duralin Premium Forte.",
            tone=Announcement.Tone.NUEVO, link_url="/aprender/explorar/", link_label="Explorar cursos",
        )

    def create_demo(self):
        rnd = random.Random(2026)
        courses = list(Course.objects.filter(is_published=True))
        now = timezone.now()
        for username, first, last in data.DEMO_SUPERVISORS:
            user, created = User.objects.get_or_create(username=username, defaults={"first_name": first, "last_name": last, "role": User.Role.SUPERVISOR})
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
        for username, first, last, supervisor, city in data.DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first, "last_name": last, "supervisor": supervisor, "city": city, "role": User.Role.EJECUTIVO, "headline": "Ejecutivo comercial"},
            )
            if not created:
                continue
            user.set_password(DEMO_PASSWORD)
            user.save()
            for course in rnd.sample(courses, rnd.randint(2, len(courses))):
                Enrollment.objects.get_or_create(user=user, course=course)
                lessons = list(course.lessons)
                done = lessons if rnd.random() < 0.75 else lessons[: rnd.randint(1, len(lessons))]
                when = now - timedelta(days=rnd.randint(3, 150), hours=rnd.randint(0, 20))
                for lesson in done:
                    LessonProgress.objects.update_or_create(user=user, lesson=lesson, defaults={"completed_at": when})
                if len(done) < len(lessons):
                    continue
                quiz = course.quiz
                questions = list(quiz.questions.values_list("pk", flat=True))
                for attempt_n in range(rnd.choice([1, 1, 2])):
                    correct = rnd.choice([5, 6, 7, 8, 8, 9, 9, 10]) if attempt_n == 0 else rnd.choice([8, 9, 10])
                    total = min(10, len(questions))
                    correct = min(correct, total)
                    score = round(correct * 100 / total)
                    finished = when + timedelta(days=attempt_n, minutes=rnd.randint(4, 9))
                    attempt = Attempt.objects.create(
                        user=user, quiz=quiz, question_ids=questions[:total], total=total, correct_count=correct, score=score,
                        passed=score >= quiz.passing_score, finished_at=finished,
                    )
                    Attempt.objects.filter(pk=attempt.pk).update(started_at=finished - timedelta(minutes=rnd.randint(3, 9)))
                    if attempt.passed:
                        cert = check_course_completion(user, course, attempt=attempt)
                        if cert:
                            type(cert).objects.filter(pk=cert.pk).update(issued_at=finished)
                        Enrollment.objects.filter(user=user, course=course).update(completed_at=finished)
                        if rnd.random() < 0.6:
                            Review.objects.get_or_create(
                                user=user, course=course,
                                defaults={"rating": rnd.choice([4, 5, 5, 5]), "comment": rnd.choice([
                                    "Muy práctico, ya lo estoy aplicando con mis clientes.",
                                    "Claro y directo. Me sirvió para explicar mejor el producto.",
                                    "Excelente para repasar antes de visitar a los distribuidores.",
                                    "",
                                ])},
                            )
                        break
        self.stdout.write(f"Usuarios demo creados (contraseña: {DEMO_PASSWORD}).")
