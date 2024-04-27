from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'startups'

router = routers.DefaultRouter()
router.register('', views.StartupViewSet)

urlpatterns = [
    
    
    
    path('post', views.PostForUserStartup.as_view(), name='check'),
    path('', include(router.urls)),
]