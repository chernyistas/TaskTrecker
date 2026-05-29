from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "executor", "deadline", "status", "parent_task")
    list_display_links = ("name",)
    search_fields = (
        "name",
        "executor__full_name",
    )
    list_filter = (
        "status",
        "executor",
        "deadline",
    )
    filter_horizontal = ()
    date_hierarchy = "deadline"
    ordering = (
        "-deadline",
        "status",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_per_page = 25
