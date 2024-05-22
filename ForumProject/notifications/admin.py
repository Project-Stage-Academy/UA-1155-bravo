from django.contrib import admin
from notifications.models import Notification, StartupNotificationPrefs, InvestorNotificationPrefs

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
    
@admin.register(StartupNotificationPrefs)

class StartupNotificationPrefsAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'startup',
        'email_project_followers_change',
        'email_project_subscription_change',
        'push_project_followers_change',
        'push_project_subscription_change',
        'email_startup_subscribed',
        'email_startup_unsubscribed',
        'push_startup_subscribed',
        'push_startup_unsubscribed'
    ]


@admin.register(InvestorNotificationPrefs)

class InvestorNotificationPrefsAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'investor',
        'email_project_profile_change',
        'push_project_profile_change',
        'email_startup_profile_update',
        'push_startup_profile_update'
    ]

