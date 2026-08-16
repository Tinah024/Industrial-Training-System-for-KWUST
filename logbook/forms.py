from django import forms
from .models import LogbookEntry


class LogbookEntryForm(forms.ModelForm):
    class Meta:
        model = LogbookEntry
        fields = ['week_number', 'activities', 'skills_acquired', 'challenges', 'attachment']
        widgets = {
            'activities': forms.Textarea(attrs={'rows': 4}),
            'skills_acquired': forms.Textarea(attrs={'rows': 3}),
            'challenges': forms.Textarea(attrs={'rows': 3}),
        }