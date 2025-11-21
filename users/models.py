from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('instructor', 'Instructor'),
    ]
    
    student_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    reputation_points = models.PositiveIntegerField(default=0)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self) -> str:
        display = self.get_full_name() or self.username or self.email
        return f"{display} ({self.student_id})" if self.student_id else display

# Create your models here.
