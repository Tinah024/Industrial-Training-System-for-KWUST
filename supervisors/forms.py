from django import forms
from accounts.models import CustomUser
from logbook.models import LogbookEntry
from supervisors.models import SupervisorProfile


class LogbookReviewForm(forms.ModelForm):
    class Meta:
        model = LogbookEntry
        fields = ['supervisor_comment', 'grade', 'is_reviewed']
        widgets = {
            'supervisor_comment': forms.Textarea(attrs={'rows': 4}),
        }


class SupervisorUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']


class SupervisorProfileForm(forms.ModelForm):
    class Meta:
        model = SupervisorProfile
        fields = ['department', 'company_name', 'is_industry_supervisor']