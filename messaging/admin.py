from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "short_body", "sent_at", "is_read")
    list_filter = ("is_read", "sent_at")
    search_fields = ("sender__username", "receiver__username", "body")
    ordering = ("-sent_at",)

    def short_body(self, obj):
        return obj.body[:50]

    short_body.short_description = "Message"