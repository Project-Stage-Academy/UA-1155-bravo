from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'projects'

router = routers.DefaultRouter()
router.register('', views.ProjectViewSet)

urlpatterns = [
    path('', include(router.urls)), 
    path('<int:project>/files/', views.ProjectFilesViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'delete': 'destroy',
    }), name='project_files_by_project'),
    path('<int:project>/file/<int:projectfiles_id>/',
        views.project_file, name='project_file'),


    
    path('shortlist-project/<int:project_id>/by-investor/<int:investor_id>/',
        views.shortlist_project, name='shortlist_project'),
    path('subscribe-for-project/<int:project_id>/by-investor/<int:investor_id>/for-share/<int:share>/',
        views.subscribe_for_project, name='subscribe_for_project'),
    path('delist-project/<int:project_id>/by-investor/<int:investor_id>/',
        views.delist_project, name='delist_project'),
    path('shortlisted-projects-of-startup/<int:startup_id>/', 
        views.shortlisted_projects_of_startup, name='shortlisted_projects_of_startup'),
    path('shortlisted-projects-of-investor/<int:investor_id>/',
        views.shortlisted_projects_of_investor, name='shortlisted_projects_of_investor'),
    path('logs/<int:project>/', views.ProjectFilesViewSet.as_view({
        'get': 'list',
    }), name='project_logs')
]
