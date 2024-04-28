from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'projects'

router = routers.DefaultRouter()
router.register('', views.ProjectViewSet)

urlpatterns = [
    path('', include(router.urls)), 
    path('files/<int:project>/', views.ProjectFilesViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'delete': 'destroy',
    }), name='project_files_by_project')
]