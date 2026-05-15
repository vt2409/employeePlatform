from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["full_name", "job_title", "department", "country_code", "salary", "currency", "employment_type", "is_active"]
    list_filter = ["country_code", "department", "employment_type", "is_active"]
    search_fields = ["full_name", "job_title", "department"]
    ordering = ["full_name"]
