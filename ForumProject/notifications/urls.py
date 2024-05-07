from django.urls import path
from . import views
from .views import NotificationPreferenceAPIView

app_name = 'notifications'

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('api/notifications/preferences/', NotificationPreferenceAPIView.as_view(), name='notification_preferences'),
]