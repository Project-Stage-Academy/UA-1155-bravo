# Generated by Django 5.0.4 on 2024-04-25 23:14

import django.utils.timezone
import projects.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
        ('startups', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='project_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='project_status',
            new_name='status',
        ),
        migrations.AddField(
            model_name='project',
            name='budget_amount',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='budget_currency',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='description',
            field=models.CharField(default='Lorem ipsum', max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='documentation',
            field=models.FileField(blank=True, null=True, upload_to=projects.models.Project._generate_upload_path),
        ),
        migrations.AddField(
            model_name='project',
            name='duration',
            field=models.FloatField(blank=True, null=True, verbose_name='duration (months)'),
        ),
        migrations.AddField(
            model_name='project',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.UniqueConstraint(fields=('startup', 'name'), name='unique_project_per_startup'),
        ),
    ]
