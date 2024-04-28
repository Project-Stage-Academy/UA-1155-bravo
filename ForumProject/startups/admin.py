from django.contrib import admin
from .models import Startup

class StartupAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'startup_name',
                    'startup_industry',
                    'startup_city'
                    ]

admin.site.register(Startup, StartupAdmin)

