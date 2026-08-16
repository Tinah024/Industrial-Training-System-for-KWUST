from django.db import models

from django.db import models
from accounts.models import CustomUser


class SupervisorProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE,
        related_name='supervisor_profile'
    )
    department = models.CharField(max_length=100, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    is_industry_supervisor = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()} - Supervisor"
