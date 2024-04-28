from django.urls import path, include
from .views import StartupViewSet
from rest_framework import routers
from .views import StartupViewSet
from rest_framework.routers import DefaultRouter


app_name = 'startups'


urlpatterns = [
    
    
    path('', StartupViewSet.as_view({'get': 'list', 'post': 'create'}), name='startup-list'),
    path('<int:pk>/', StartupViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='startup-detail'),
    
]
