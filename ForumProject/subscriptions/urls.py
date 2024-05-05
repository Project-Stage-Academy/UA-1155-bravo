from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('add/', views.SubscriptionsListView.as_view(), name='add-subscriptions'),
    path('my/', views.SubscriptionsListView.as_view(), name='my-subscriptions'),
]