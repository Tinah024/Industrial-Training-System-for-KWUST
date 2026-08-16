from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('supervisor', 'Supervisor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(
        upload_to='profiles/', blank=True, null=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


