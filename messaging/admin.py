from django.contrib import admin
from .models import Message, ItemReturn


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'item', 'content', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'receiver__username', 'content']


@admin.register(ItemReturn)
class ItemReturnAdmin(admin.ModelAdmin):
    list_display = ['item', 'owner', 'returner', 'returned_at']
    list_filter = ['returned_at']
    search_fields = ['item__name', 'owner__username', 'returner__username']
