from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "tone", "is_active", "created_at")
    list_filter = ("tone", "is_active")
