from django.contrib import admin

from .models import CustomUser, UserInvestor, UserStartup

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserInvestor)
admin.site.register(UserStartup)
