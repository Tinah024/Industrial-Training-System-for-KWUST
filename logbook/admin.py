from django.contrib import admin

from django.contrib import admin
from .models import LogbookEntry

@admin.register(LogbookEntry)
class LogbookEntryAdmin(admin.ModelAdmin):
    list_display = ['student', 'week_number', 'submitted_at', 'is_reviewed']
