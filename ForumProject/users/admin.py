from django.contrib import admin

from .models import CustomUser, UserInvestor, UserStartup, UserRoleCompany


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'first_name', 'last_name', 'is_active']
    list_editable = ['is_active']
admin.site.register(CustomUser, CustomUserAdmin)

class UserInvestorAdmin(admin.ModelAdmin):
    list_display = ['customuser', 'investor', 'investor_role_id']
admin.site.register(UserInvestor, UserInvestorAdmin)

class UserStartupAdmin(admin.ModelAdmin):
    list_display = ['customuser', 'startup', 'startup_role_id']
admin.site.register(UserStartup, UserStartupAdmin)

class UserRoleCompanyAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'company_id']
admin.site.register(UserRoleCompany, UserRoleCompanyAdmin)