from django import forms
from .models import StudentProfile


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'registration_number', 'course', 'year_of_study',
            'company_name', 'company_address',
            'placement_start_date', 'placement_end_date'
        ]
        widgets = {
            'placement_start_date': forms.DateInput(attrs={'type': 'date'}),
            'placement_end_date': forms.DateInput(attrs={'type': 'date'}),
            'company_address': forms.Textarea(attrs={'rows': 2}),
        }