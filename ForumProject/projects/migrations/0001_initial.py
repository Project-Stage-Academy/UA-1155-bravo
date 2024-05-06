# Generated by Django 5.0.4 on 2024-05-06 12:53

import django.db.models.deletion
import projects.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('investors', '0001_initial'),
        ('startups', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=150)),
                ('description', models.CharField(db_index=True, max_length=500)),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('pending', 'Pending')], default='open', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('duration', models.FloatField(blank=True, null=True, verbose_name='duration (months)')),
                ('budget_currency', models.CharField(blank=True, max_length=3, null=True)),
                ('budget_amount', models.IntegerField(blank=True, null=True)),
                ('startup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='startups.startup')),
            ],
            options={
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
                'ordering': ['startup', 'name'],
            },
        ),
        migrations.CreateModel(
            name='InvestorProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('share', models.IntegerField()),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shortlisted_project', to='investors.investor')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_share', to='projects.project')),
            ],
            options={
                'verbose_name': 'Project Shortlist',
                'verbose_name_plural': 'Project Shortlists',
                'ordering': ['project', '-share'],
            },
        ),
        migrations.CreateModel(
            name='ProjectFiles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_description', models.CharField(db_index=True, max_length=255, verbose_name='file description')),
                ('file', models.FileField(blank=True, null=True, upload_to=projects.models.ProjectFiles._generate_upload_path)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_files', to='projects.project')),
            ],
            options={
                'verbose_name': 'Project File',
                'verbose_name_plural': 'Project Files',
                'ordering': ['project'],
            },
        ),
        migrations.CreateModel(
            name='ProjectLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_birth_id', models.IntegerField(verbose_name='id')),
                ('change_date', models.DateField(auto_now_add=True, db_index=True)),
                ('change_time', models.TimeField(auto_now_add=True)),
                ('user_id', models.IntegerField(db_index=True)),
                ('action', models.CharField(db_index=True, max_length=50)),
                ('previous_state', models.CharField(max_length=255, verbose_name='Before changes')),
                ('modified_state', models.CharField(max_length=255, verbose_name='After changes')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_log', to='projects.project', verbose_name='Project in DB')),
            ],
            options={
                'verbose_name': 'Project Log',
                'verbose_name_plural': 'Project Logs',
                'ordering': ['-pk'],
            },
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.UniqueConstraint(fields=('startup', 'name'), name='unique_project_per_startup'),
        ),
        migrations.AddConstraint(
            model_name='investorproject',
            constraint=models.CheckConstraint(check=models.Q(('share__gte', 0), ('share__lte', 100)), name='percentage_share_range'),
        ),
    ]
