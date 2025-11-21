from django.db import models
from django.conf import settings
from items.models import Item


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='message_images/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"


class ItemReturn(models.Model):
    """Track when an item is returned through messaging"""
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='return_record')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items_received')
    returner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items_returned')
    conversation = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    returned_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.returner.username} returned {self.item} to {self.owner.username}"
