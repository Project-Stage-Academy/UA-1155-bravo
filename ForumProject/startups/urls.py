from django.urls import path, include
from .views import StartupViewSet
from rest_framework import routers
from .views import StartupViewSet, StartupList, StartupListDetailfilter, NotificationPreferencesAPIView
from rest_framework.routers import DefaultRouter


app_name = 'startups'



urlpatterns = [
    
    
    path('', StartupList.as_view(), name='startup-list'),
    path('add/', StartupViewSet.as_view({'post': 'create'}), name='startup-add'),
    path('<int:pk>/', StartupViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='startup-detail'),
    path('search/', StartupListDetailfilter.as_view(), name='startup-search'),
    path('notification/preferences/', NotificationPreferencesAPIView.as_view(), name='notification-preferences'),
]

