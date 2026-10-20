from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CampusUserAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "role", "supervisor", "origin", "is_active", "last_login")
    list_filter = ("role", "origin", "is_active", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email", "supervisor")
    fieldsets = UserAdmin.fieldsets + (
        ("Campus", {"fields": ("role", "supervisor", "area", "city", "headline", "avatar", "origin")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (("Campus", {"fields": ("first_name", "last_name", "role", "supervisor")}),)
