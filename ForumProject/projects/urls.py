from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'projects'

router = routers.DefaultRouter()
router.register('', views.ProjectViewSet)

urlpatterns = [
    path('followed/', views.view_followed_projects, name='view_followed_projects'),
    path('logs/<int:pk>/', views.view_logs, name='view_logs'),
    path('', include(router.urls)), 
    path('<int:pk>/files/', views.ProjectFilesViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'delete': 'destroy',
    }), name='project_files_by_project'),
    path('<int:pk>/file/<int:projectfiles_id>/',
        views.project_file, name='project_file'),
    path('follow/<int:project_id>/',
        views.follow, name='follow'),
    path('subscription/<int:project_id>/<int:share>/',
        views.subscription, name='subscription'),
    path('stop-follow/<int:project_id>/',
        views.delist_project, name='delist_project'),
]
