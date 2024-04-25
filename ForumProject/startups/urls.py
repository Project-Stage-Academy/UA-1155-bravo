from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'startups'

# router = routers.DefaultRouter()
# router.register('', views.StartupViewSet)

urlpatterns = [
    # path('', include(router.urls))
    path('', views.StartupList.as_view(), name='startup-list'), 
    path('add/', views.StartupViewSet.as_view({'post': 'create'}), name='startup-add'),
    path('search/', views.StartupListDetailfilter.as_view(), name='startup-search'),

]