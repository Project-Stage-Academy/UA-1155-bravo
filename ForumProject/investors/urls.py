from django.urls import path, include
from .views import InvestorViewSet
from . import views
from rest_framework import routers

app_name = 'investors'




urlpatterns = [
    
    path('', InvestorViewSet.as_view({'get': 'list', 'post': 'create'}), name='investor-list'),
    path('<int:pk>/', InvestorViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='investor-detail'),
    
   
]

