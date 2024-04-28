from django.urls import path, include
from .views import StartupViewSet
from rest_framework import routers
from .views import StartupViewSet, StartupList
from rest_framework.routers import DefaultRouter


app_name = 'startups'



urlpatterns = [
    
    
    path('', views.StartupList.as_view({'get': 'list'}), name='startup-list'),
    path('add/', views.StartupViewSet.as_view({'post': 'create'}), name='startup-add'),
    path('<int:pk>/', views.StartupViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='startup-detail'),
    path('search/', views.StartupListDetailfilter.as_view(), name='startup-search'),
    
]

