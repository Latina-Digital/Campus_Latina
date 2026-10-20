from django.contrib import admin

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("code", "holder_name", "course_title", "score", "issued_at", "is_revoked")
    list_filter = ("is_revoked", "course")
    search_fields = ("code", "holder_name", "user__username")
    readonly_fields = ("code",)
