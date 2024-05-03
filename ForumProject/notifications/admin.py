from django.contrib import admin
from notifications.models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_time', 'project', 'startup_name', 'investor', 'trigger', 'initiator']