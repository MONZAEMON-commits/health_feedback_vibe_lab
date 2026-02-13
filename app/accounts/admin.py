from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EmployeeProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Role", {"fields": ("role_level",)}),
    )
    list_display = ("username", "email", "role_level", "is_staff", "is_active")


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "department", "gender", "age", "is_target")
