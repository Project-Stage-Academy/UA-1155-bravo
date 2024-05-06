from django.contrib import admin
from .models import Investor

class InvestorAdmin(admin.ModelAdmin):
    list_display = ['id', 'investor_name', 'investor_industry', 'investor_country', 'investor_city']

admin.site.register(Investor, InvestorAdmin)
