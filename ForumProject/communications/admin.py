from django.contrib import admin

from .models import Room, Message, ChatNotification

admin.site.register(Room)
admin.site.register(Message)
admin.site.register(ChatNotification)