from django.urls import path
from . import views
from .views import NotificationPrefsViewSet

app_name = 'notifications'

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    # path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('preferences/', 
            NotificationPrefsViewSet.as_view({'get': 'retrieve', 'put': 'update'}), 
            name='notification_detail'
        )
]