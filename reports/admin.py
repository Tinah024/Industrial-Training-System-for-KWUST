from django.contrib import admin

from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['student', 'title', 'submitted_at', 'status']
