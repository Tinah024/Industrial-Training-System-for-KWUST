from django.db import models
from accounts.models import CustomUser


class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='received_messages'
    )
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}"


class Notification(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications'  # keep ONLY here
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"