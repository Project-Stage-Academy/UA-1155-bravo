
from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('add/', views.AddSubscription.as_view({'get': 'list', 'post': 'create'}), name='add-subscriptions'),
    path('my/', views.SubscriptionViewsets.as_view({'get': 'list'}), name='my-subscriptions'),
    path('my/<int:pk>/', views.SubscriptionViewsets.as_view({'get': 'subscription_by_id', 'delete': 'delete'}), name='subscription-detail'),
]
