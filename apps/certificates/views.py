from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Certificate
from .pdf import render_certificate


def public_url(request, path):
    if settings.CAMPUS_PUBLIC_URL:
        return settings.CAMPUS_PUBLIC_URL + path
    return request.build_absolute_uri(path)


def _owned(request, code):
    certificate = get_object_or_404(Certificate.objects.select_related("course", "user"), code=code.upper())
    if certificate.user != request.user and not request.user.is_staff:
        raise Http404
    return certificate


@login_required
def my_certificates(request):
    certificates = request.user.certificates.filter(is_revoked=False).select_related("course", "course__category")
    return render(request, "certificates/list.html", {"certificates": certificates})


@login_required
def detail(request, code):
    certificate = _owned(request, code)
    verify_url = public_url(request, certificate.get_verify_path())
    issued = timezone.localtime(certificate.issued_at)
    linkedin = "https://www.linkedin.com/profile/add?" + urlencode(
        {
            "startTask": "CERTIFICATION_NAME",
            "name": certificate.course_title,
            "organizationName": settings.CAMPUS_COMPANY,
            "issueYear": issued.year,
            "issueMonth": issued.month,
            "certUrl": verify_url,
            "certId": certificate.code,
        }
    )
    return render(
        request,
        "certificates/detail.html",
        {"certificate": certificate, "verify_url": verify_url, "linkedin_url": linkedin},
    )


@login_required
def pdf(request, code):
    certificate = _owned(request, code)
    buffer = render_certificate(certificate, public_url(request, certificate.get_verify_path()))
    filename = f"Certificado-{certificate.code}.pdf"
    return FileResponse(buffer, as_attachment=request.GET.get("descargar") == "1", filename=filename, content_type="application/pdf")


def verify(request, code=None):
    code = (code or request.GET.get("codigo", "")).strip().upper()
    if code and not request.resolver_match.kwargs.get("code"):
        return redirect("certificates:verify_code", code=code)
    certificate = None
    if code:
        certificate = Certificate.objects.select_related("course", "user").filter(code=code).first()
    return render(request, "certificates/verify.html", {"code": code, "certificate": certificate})
