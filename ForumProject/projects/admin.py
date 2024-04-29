from django.contrib import admin
from .models import Project, ProjectFiles, InvestorProject, ProjectLog

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

class ProjectLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'project',
        'project_title',
        'change_date',
        'change_time',
        'user_id',
        'action',
        'previous_state',
        'modified_state'
    ]
    search_fields = ['project', 'change_date', 'user_id', 'action']

admin.site.register(ProjectLog, ProjectLogAdmin)