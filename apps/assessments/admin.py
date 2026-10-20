from django.contrib import admin

from .models import Attempt, Choice, Question, Quiz


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "order")
    list_filter = ("quiz",)
    inlines = [ChoiceInline]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "time_limit_minutes", "questions_per_attempt", "passing_score", "max_attempts")


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "started_at", "score", "passed", "timed_out")
    list_filter = ("passed", "quiz")
    search_fields = ("user__username", "user__first_name", "user__last_name")
