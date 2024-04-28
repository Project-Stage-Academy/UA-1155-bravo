from django.contrib import admin
from .models import Project, ProjectFiles, InvestorProject

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'name',
                    'startup',
                    'description',
                    'status',
                    'created_at',
                    'updated_at',
                    'duration',
                    'budget_currency',
                    'budget_amount'
                    ]
    search_fields = ['name', 'description']

admin.site.register(Project, ProjectAdmin)

class ProjectFilesAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'file_description', 'file']
    search_fields = ['id', 'project', 'file_description', 'file']

admin.site.register(ProjectFiles, ProjectFilesAdmin)

class InvestorProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'investor', 'project', 'share']
    search_fields = ['id', 'investor', 'project']

admin.site.register(InvestorProject, InvestorProjectAdmin)