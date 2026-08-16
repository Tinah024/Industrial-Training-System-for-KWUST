from django.db import models
from accounts.models import CustomUser


class LogbookEntry(models.Model):
    student = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='logbook_entries'
    )
    week_number = models.IntegerField()
    activities = models.TextField()
    skills_acquired = models.TextField(blank=True)
    challenges = models.TextField(blank=True)
    attachment = models.FileField(
        upload_to='logbook_attachments/', blank=True, null=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    supervisor_comment = models.TextField(blank=True)
    grade = models.CharField(max_length=5, blank=True)

    class Meta:
        unique_together = ('student', 'week_number')  # ← prevents duplicates at DB level

    def __str__(self):
        return f"{self.student.username} - Week {self.week_number}"