from django.contrib import admin
from notifications.models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_time', 'project', 'startup_name', 'investor', 'trigger', 'initiator']
    search_fields = ['project__name', 'startup_name', 'investor__username', 'trigger', 'initiator__username']
    list_filter = ['project', 'date_time', 'trigger']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
