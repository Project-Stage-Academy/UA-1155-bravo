from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'projects'

router = routers.DefaultRouter()
router.register('', views.ProjectView)

urlpatterns = [
    path('', include(router.urls))
]