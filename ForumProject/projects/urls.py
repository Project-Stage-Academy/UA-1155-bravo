from django.urls import path, include
from . import views_projects, views_files, views_follow, views_logs
from rest_framework import routers

app_name = 'projects'

router = routers.DefaultRouter()
router.register('', views_projects.ProjectViewSet)

urlpatterns = [
    path('followed/', views_follow.view_followed_projects, name='view_followed_projects'),
    path('logs/<int:pk>/', views_logs.view_logs, name='view_logs'),
    path('', include(router.urls)), 
    path('<int:pk>/files/', views_files.ProjectFilesViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'delete': 'destroy',
    }), name='project_files_by_project'),
    path('<int:pk>/file/<int:projectfiles_id>/',
        views_files.project_file, name='project_file'),
    path('follow/<int:project_id>/',
        views_follow.follow, name='follow'),
    path('subscription/<int:project_id>/<int:share>/',
        views_follow.subscription, name='subscription'),
    path('stop-follow/<int:project_id>/',
        views_follow.delist_project, name='delist_project'),
]
