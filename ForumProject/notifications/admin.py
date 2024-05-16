from django.contrib import admin
from notifications.models import Notification, NotificationPreferences

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_time', 'project', 'startup', 'investor', 'trigger', 'initiator']
    search_fields = ['project__name', 'startup', 'investor__username', 'trigger', 'initiator__username']
    list_filter = ['project', 'date_time', 'trigger']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
@admin.register(NotificationPreferences)

class NotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'startup',
        'email_on_followers_change',
        'email_on_share_subscription',
        'in_app_on_followers_change',
        'in_app_on_share_subscription'
    ]

