from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'projects'
#
# router = routers.DefaultRouter()
# router.register('', views.ProjectViewSet)

urlpatterns = [
    # path('', include(router.urls))

    path('', views.ProjectViewSet.as_view({'get': 'list'}), name='startup-list'),
    path('add/', views.ProjectViewSet.as_view({'post': 'create'}), name='startup-add'),
    path('<int:pk>/', views.ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='startup-detail'),
]
