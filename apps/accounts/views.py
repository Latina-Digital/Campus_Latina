from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from apps.core.gamification import level_info, user_badges, user_points
from apps.courses.models import Enrollment

from .forms import CampusPasswordChangeForm, LoginForm, ProfileForm
from .models import User


def _client_ip(request):
    return request.META.get("REMOTE_ADDR", "")


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def _lock_key(self):
        username = self.request.POST.get("username", "").strip().lower()
        return f"login-fail:{username}:{_client_ip(self.request)}"

    def post(self, request, *args, **kwargs):
        if cache.get(self._lock_key(), 0) >= settings.LOGIN_MAX_ATTEMPTS:
            # No se valida el formulario: así ni siquiera se consulta la API de Syspro.
            form = self.form_class(request=request, initial={"username": request.POST.get("username", "")})
            lockout = f"Demasiados intentos fallidos. Espera {settings.LOGIN_LOCKOUT_MINUTES} minutos e inténtalo de nuevo."
            return self.render_to_response(self.get_context_data(form=form, lockout=lockout), status=429)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        key = self._lock_key()
        cache.set(key, cache.get(key, 0) + 1, settings.LOGIN_LOCKOUT_MINUTES * 60)
        return super().form_invalid(form)

    def form_valid(self, form):
        cache.delete(self._lock_key())
        if not form.cleaned_data.get("remember"):
            self.request.session.set_expiry(0)
        response = super().form_valid(form)
        messages.success(self.request, f"¡Hola, {self.request.user.short_name}! Qué bueno verte de nuevo.")
        return response


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = CampusPasswordChangeForm
    success_url = reverse_lazy("accounts:profile")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.has_usable_password():
            messages.info(request, "Tu contraseña se administra en el sistema corporativo (Syspro).")
            return redirect("accounts:profile")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Tu contraseña fue actualizada.")
        return super().form_valid(form)


@login_required
def profile(request, username=None):
    person = get_object_or_404(User, username=username, is_active=True) if username else request.user
    is_me = person == request.user
    form = None
    if is_me:
        form = ProfileForm(request.POST or None, request.FILES or None, instance=person)
        if request.method == "POST" and form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado.")
            return redirect("accounts:profile")
    stats = user_points(person)
    context = {
        "person": person,
        "is_me": is_me,
        "form": form,
        "stats": stats,
        "level": level_info(stats["points"]),
        "badges": user_badges(person, stats),
        "certificates": person.certificates.filter(is_revoked=False).select_related("course"),
        "completed": Enrollment.objects.filter(user=person, completed_at__isnull=False).select_related("course")[:12],
    }
    return render(request, "accounts/profile.html", context)


@login_required
def team(request):
    user = request.user
    if not user.is_leader:
        raise PermissionDenied
    supervisors = []
    if user.is_staff:
        supervisors = sorted({s for s in User.objects.exclude(supervisor="").values_list("supervisor", flat=True)})
        selected = request.GET.get("supervisor") or user.display_name
    else:
        selected = user.display_name
    members = User.objects.filter(is_active=True, supervisor__iexact=selected).annotate(
        last_activity=Max("lesson_progress__updated_at")
    )
    rows = []
    for member in members:
        stats = user_points(member)
        enrollments = member.enrollments.all()
        rows.append(
            {
                "user": member,
                "stats": stats,
                "level": level_info(stats["points"]),
                "in_progress": sum(1 for e in enrollments if not e.completed_at),
                "completed": sum(1 for e in enrollments if e.completed_at),
            }
        )
    rows.sort(key=lambda r: -r["stats"]["points"])
    context = {"rows": rows, "selected": selected, "supervisors": supervisors}
    return render(request, "accounts/team.html", context)
