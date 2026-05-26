from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeesAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "position", "created_at")
    list_display_links = ("full_name",)
    search_fields = (
        "full_name",
        "position",
    )
    list_filter = ("position",)
    ordering = ("full_name",)
