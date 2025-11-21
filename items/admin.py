from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "category", "user", "status", "created_at", "is_anonymous")
    list_filter = ("type", "status", "category", "is_anonymous", "created_at")
    search_fields = ("description", "category", "location_text", "user__username", "user__student_id")
