from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'projects'

router = routers.DefaultRouter()
router.register('', views.ProjectViewSet)

urlpatterns = [
    path('', include(router.urls)), 
    path('files-of-project/<int:project>/', views.ProjectFilesViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'delete': 'destroy',
    }), name='project_files_by_project'),
    path('delete-file/<int:projectfiles_id>/of-project/<int:project>/', views.delete_project_file, name='delete_project_file')
]
