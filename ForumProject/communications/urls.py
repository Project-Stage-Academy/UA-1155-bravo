from django.urls import path

from . import views

app_name = 'communications'

urlpatterns = [
    path('', views.index_view, name='chat-index'),
    path('<int:user_id>/', views.room_view, name='chat-room'),
]
