from django.db import models
from django.conf import settings


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        ITEM_APPROVED = 'item_approved', 'Item Approved'
        ITEM_REJECTED = 'item_rejected', 'Item Rejected'
        MATCH_FOUND = 'match_found', 'Potential Match Found'
        ITEM_CLAIMED = 'item_claimed', 'Item Claimed'
        MESSAGE_RECEIVED = 'message_received', 'New Message'
        GENERAL = 'general', 'General'
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=30, choices=NotificationType.choices, default=NotificationType.GENERAL)
    title = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE, null=True, blank=True, related_name='item_notifications')
    match = models.ForeignKey('items.ItemMatch', on_delete=models.CASCADE, null=True, blank=True, related_name='match_notifications')
    link_url = models.CharField(max_length=500, blank=True, help_text='URL to redirect when notification is clicked')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"To {self.user}: {self.title or self.message[:40]}..."
