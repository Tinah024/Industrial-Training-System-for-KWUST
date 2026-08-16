from django.db import models

from django.db import models
from accounts.models import CustomUser


class StudentProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='student_profile'
    )
    registration_number = models.CharField(max_length=20, unique=True)
    course = models.CharField(max_length=100)
    year_of_study = models.IntegerField()
    company_name = models.CharField(max_length=200, blank=True)
    company_address = models.TextField(blank=True)
    placement_start_date = models.DateField(null=True, blank=True)
    placement_end_date = models.DateField(null=True, blank=True)
    university_supervisor = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_students'
    )

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.registration_number}"
