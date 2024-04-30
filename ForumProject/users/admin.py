from django.contrib import admin

from .models import CustomUser, UserInvestor, UserStartup, UserRoleCompany

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserInvestor)
admin.site.register(UserStartup)
admin.site.register(UserRoleCompany)
