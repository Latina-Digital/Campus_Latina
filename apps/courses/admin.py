from django.contrib import admin

from .models import Category, Course, Enrollment, LearningPath, Lesson, LessonProgress, Module, PathStep, Resource, Review


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "brand", "category", "level", "is_published", "is_featured")
    list_filter = ("brand", "category", "level", "is_published")
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("related_products",)
    inlines = [ModuleInline, ResourceInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    inlines = [LessonInline]


class PathStepInline(admin.TabularInline):
    model = PathStep
    extra = 0


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ("title", "brand", "is_published", "order")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PathStepInline]


admin.site.register(Enrollment, list_display=("user", "course", "created_at", "completed_at"), list_filter=("course",))
admin.site.register(LessonProgress, list_display=("user", "lesson", "completed_at"))
admin.site.register(Review, list_display=("user", "course", "rating", "created_at"))
