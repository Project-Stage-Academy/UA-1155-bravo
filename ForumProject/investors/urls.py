from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'investors'

router = routers.DefaultRouter()
router.register('', views.InvestorViewSet)

urlpatterns = [
    path('', include(router.urls))
]
