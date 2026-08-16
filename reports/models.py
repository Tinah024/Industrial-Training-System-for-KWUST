from django.db import models

from django.db import models
from accounts.models import CustomUser


class Report(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
    )
    student = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='reports'
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='reports/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    supervisor_feedback = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.title}"
