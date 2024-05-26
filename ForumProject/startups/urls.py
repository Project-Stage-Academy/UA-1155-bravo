from django.urls import  path

from subscriptions.views import AddSubscription
from .views import PersonalStartupList, StartupList, StartupListDetailfilter, StartupViewSet


app_name = 'startups'



urlpatterns = [

    path('', StartupList.as_view(), name='startup-list'),
    path('add/', StartupViewSet.as_view({'post': 'create'}), name='startup-add'),
    path('<int:pk>/', StartupViewSet.as_view({'get': 'retrieve',
                                              'put': 'update',
                                              'delete': 'destroy'}), name='startup-detail'),
    path('my/', PersonalStartupList.as_view(), name='my-startup'),
    path('search/', StartupListDetailfilter.as_view(), name='startup-search'),
    path('subscribe/', AddSubscription.as_view({'get': 'list',
                                                'post': 'create', }), name='startup-sub'),
]



