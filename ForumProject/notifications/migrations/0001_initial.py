# Generated by Django 5.0.4 on 2024-05-07 09:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('investors', '0001_initial'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startup_name', models.CharField(max_length=150)),
                ('trigger', models.CharField(choices=[('follower(s) list changed', 'follower(s) list changed'), ('subscription changed', 'subscription changed'), ('project status changed', 'project status changed'), ('project budget changed', 'project budget changed'), ('message sent', 'message sent')], max_length=50)),
                ('initiator', models.CharField(choices=[('investor', 'investor'), ('project', 'project')], max_length=8)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('investor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notice_to_investor', to='investors.investor')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notice_on_project', to='projects.project')),
            ],
        ),
        migrations.AddConstraint(
            model_name='notification',
            constraint=models.CheckConstraint(check=models.Q(('project__isnull', False), ('investor__isnull', False), _connector='OR'), name='project_or_investor_required'),
        ),
    ]
