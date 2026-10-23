import io
import shutil
import tempfile

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User
from apps.assessments.models import Attempt, Choice
from apps.certificates.models import Certificate
from apps.courses.models import Course, LessonProgress
from apps.panel.importers import parse_question_text

MEDIA = tempfile.mkdtemp(prefix="campus-test-media-")


@override_settings(MEDIA_ROOT=MEDIA)
class CampusFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_campus", "--demo", stdout=io.StringIO())
        cls.admin = User.objects.create(username="ADMIN", first_name="Administrador", role=User.Role.ADMIN, is_superuser=True)
        cls.learner = User.objects.create_user("tester", password="Prueba2026*", first_name="Ana", last_name="Prueba", supervisor="Fernando Abarca")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def test_public_pages(self):
        for url in [reverse("core:landing"), reverse("accounts:login"), reverse("certificates:verify")]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.assertRedirects(self.client.get(reverse("courses:home")), reverse("accounts:login") + "?next=" + reverse("courses:home"))

    def test_learner_pages(self):
        self.client.force_login(self.learner)
        course = Course.objects.first()
        lesson = course.lessons.first()
        urls = [
            reverse("courses:home"), reverse("courses:explore"), reverse("courses:explore") + "?q=duralin&marca=latina&orden=valorados",
            reverse("courses:my_learning"), reverse("courses:my_learning") + "?tab=guardados", reverse("courses:paths"),
            reverse("courses:path_detail", args=[course.path_steps.first().path.slug]), course.get_absolute_url(), lesson.get_absolute_url(),
            reverse("assessments:intro", args=[course.slug]), reverse("catalog:list"), reverse("catalog:list") + "?marca=induless",
            reverse("core:ranking"), reverse("core:ranking") + "?vista=equipos&periodo=mes", reverse("accounts:profile"),
            reverse("accounts:public_profile", args=["mcevallos"]), reverse("certificates:list"),
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.assertEqual(self.client.get(reverse("panel:dashboard")).status_code, 302)

    def test_full_course_flow_issues_certificate(self):
        self.client.force_login(self.learner)
        course = Course.objects.get(title__startswith="Duralin")
        intro = reverse("assessments:intro", args=[course.slug])
        # La evaluación está bloqueada hasta completar las lecciones.
        self.client.post(intro)
        self.assertFalse(Attempt.objects.filter(user=self.learner).exists())
        for lesson in course.lessons:
            r = self.client.post(reverse("courses:lesson_complete", args=[lesson.pk]))
            self.assertEqual(r.status_code, 200)
        self.assertEqual(LessonProgress.objects.filter(user=self.learner, completed_at__isnull=False).count(), course.lessons.count())
        r = self.client.post(intro)
        attempt = Attempt.objects.get(user=self.learner)
        self.assertRedirects(r, reverse("assessments:take", args=[attempt.pk]))
        self.assertEqual(self.client.get(reverse("assessments:take", args=[attempt.pk])).status_code, 200)
        answers = {}
        for qid in attempt.question_ids:
            answers[f"q_{qid}"] = Choice.objects.get(question_id=qid, is_correct=True).pk
        r = self.client.post(reverse("assessments:submit", args=[attempt.pk]), answers)
        self.assertRedirects(r, reverse("assessments:result", args=[attempt.pk]))
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 100)
        self.assertTrue(attempt.passed)
        cert = Certificate.objects.get(user=self.learner, course=course)
        self.assertEqual(self.client.get(reverse("assessments:result", args=[attempt.pk])).status_code, 200)
        self.assertEqual(self.client.get(cert.get_absolute_url()).status_code, 200)
        pdf = self.client.get(reverse("certificates:pdf", args=[cert.code]))
        self.assertEqual(pdf["Content-Type"], "application/pdf")
        self.assertTrue(b"".join(pdf.streaming_content).startswith(b"%PDF"))
        self.client.logout()
        verify = self.client.get(reverse("certificates:verify_code", args=[cert.code]))
        self.assertContains(verify, "Certificado válido")

    def test_wrong_answers_fail_and_autosave_validates(self):
        self.client.force_login(self.learner)
        course = Course.objects.get(title__startswith="Satinado")
        for lesson in course.lessons:
            self.client.post(reverse("courses:lesson_complete", args=[lesson.pk]))
        self.client.post(reverse("assessments:intro", args=[course.slug]))
        attempt = Attempt.objects.get(user=self.learner, quiz__course=course)
        qid = attempt.question_ids[0]
        wrong = Choice.objects.filter(question_id=qid, is_correct=False).first()
        foreign = Choice.objects.exclude(question_id__in=attempt.question_ids).first()
        r = self.client.post(reverse("assessments:autosave", args=[attempt.pk]),
                             data={"answers": {str(qid): wrong.pk, str(attempt.question_ids[1]): foreign.pk}}, content_type="application/json")
        self.assertTrue(r.json()["ok"])
        attempt.refresh_from_db()
        self.assertEqual(attempt.answers, {str(qid): wrong.pk})
        self.client.post(reverse("assessments:submit", args=[attempt.pk]), {})
        attempt.refresh_from_db()
        self.assertFalse(attempt.passed)
        self.assertFalse(Certificate.objects.filter(user=self.learner, course=course).exists())

    def test_other_users_cannot_see_attempts_or_certificates(self):
        cert = Certificate.objects.exclude(user=self.learner).first()
        self.client.force_login(self.learner)
        self.assertEqual(self.client.get(cert.get_absolute_url()).status_code, 404)
        attempt = Attempt.objects.exclude(user=self.learner).first()
        self.assertEqual(self.client.get(reverse("assessments:result", args=[attempt.pk])).status_code, 404)

    def test_panel_pages(self):
        self.client.force_login(self.admin)
        course = Course.objects.first()
        question = course.quiz.questions.first()
        attempt = Attempt.objects.filter(finished_at__isnull=False).first()
        urls = [
            reverse("panel:dashboard"), reverse("panel:user_list"),
            reverse("panel:course_list"), reverse("panel:course_create"), reverse("panel:course_builder", args=[course.pk]),
            reverse("panel:course_edit", args=[course.pk]), reverse("panel:lesson_create", args=[course.pk]),
            reverse("panel:lesson_edit", args=[course.pk, course.lessons.first().pk]), reverse("panel:questions", args=[course.pk]),
            reverse("panel:question_edit", args=[question.pk]), reverse("panel:module_edit", args=[course.modules.first().pk]),
            reverse("panel:path_list"), reverse("panel:path_create"), reverse("panel:results"), reverse("panel:results") + "?estado=aprobado&primer=1",
            reverse("panel:attempt_report", args=[attempt.pk]), reverse("panel:certificates"), reverse("panel:product_list"),
            reverse("panel:product_create"), reverse("panel:category_list"), reverse("panel:line_list"), reverse("panel:announcement_list"),
            reverse("panel:course_delete", args=[course.pk]), reverse("accounts:team"),
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        xlsx = self.client.get(reverse("panel:results") + "?exportar=xlsx")
        self.assertEqual(xlsx.status_code, 200)
        self.assertTrue(xlsx.content.startswith(b"PK"))

    def test_panel_imports_questions(self):
        self.client.force_login(self.admin)
        course = Course.objects.get(title__startswith="Induzinc")
        before = course.quiz.questions.count()
        text = "1. ¿Pregunta de prueba?\na) Uno\n*b) Dos\nc) Tres\n\n2. ¿Otra?\na) Sí\nb) No\nRespuesta: A"
        self.client.post(reverse("panel:questions", args=[course.pk]), {"action": "import", "imp-text": text})
        self.assertEqual(course.quiz.questions.count(), before + 2)

    def test_learner_cannot_access_panel(self):
        self.client.force_login(self.learner)
        for url in [reverse("panel:dashboard"), reverse("panel:user_list"), reverse("panel:results")]:
            self.assertNotEqual(self.client.get(url).status_code, 200, url)


class ImporterTests(TestCase):
    def test_parse_question_text(self):
        questions, errors = parse_question_text("1. ¿A?\na) x\n*b) y\n2. ¿Sin correcta?\na) 1\nb) 2\n")
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["choices"], [["x", False], ["y", True]])
        self.assertEqual(len(errors), 1)
