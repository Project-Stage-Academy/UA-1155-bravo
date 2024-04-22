from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'startups'

router = routers.DefaultRouter()
router.register('', views.StartupView)

urlpatterns = [
    path('', include(router.urls))

]