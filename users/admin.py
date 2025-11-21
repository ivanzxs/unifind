from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Student Info", {"fields": ("student_id", "reputation_points")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Student Info", {"fields": ("student_id",)}),
    )
    list_display = ("username", "email", "student_id", "first_name", "last_name", "is_staff", "reputation_points")
    search_fields = ("username", "email", "student_id", "first_name", "last_name")
