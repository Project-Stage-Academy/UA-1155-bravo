from django.contrib import admin
from notifications.models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_id', 'project', 'investor', 'trigger']
