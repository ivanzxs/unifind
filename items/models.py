from django.db import models
from django.conf import settings


class Item(models.Model):
    class ItemType(models.TextChoices):
        LOST = 'lost', 'Lost'
        FOUND = 'found', 'Found'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Approval'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        CLAIMED = 'claimed', 'Claimed'
        ARCHIVED = 'archived', 'Archived'
    
    class Severity(models.TextChoices):
        LOW = 'low', 'Low Priority'
        MEDIUM = 'medium', 'Medium Priority'
        HIGH = 'high', 'High Priority'
        CRITICAL = 'critical', 'Critical'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items')
    type = models.CharField(max_length=10, choices=ItemType.choices)
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    location_text = models.CharField(max_length=255, blank=True)
    location_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    verification_question = models.CharField(max_length=255, null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)
    claim_proof = models.ImageField(upload_to='claim_proofs/', blank=True, null=True)
    claimed_by_username = models.CharField(max_length=150, blank=True, help_text='Username of person who returned/claimed the item')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_items')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.get_type_display()} - {self.category}: {self.description[:30]}"


class ItemMatch(models.Model):
    """Stores potential matches between lost and found items"""
    lost_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='lost_matches')
    found_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='found_matches')
    match_percentage = models.IntegerField(help_text='Percentage match score')
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['lost_item', 'found_item']
        ordering = ['-match_percentage', '-created_at']
    
    def __str__(self):
        return f"Match {self.match_percentage}%: {self.lost_item.id} <-> {self.found_item.id}"


