# Generated by Django 5.0.6 on 2024-05-24 10:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('investors', '0001_initial'),
        ('projects', '0001_initial'),
        ('startups', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestorNotificationPrefs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_project_profile_change', models.BooleanField(default=True, verbose_name='Email Project changes')),
                ('push_project_profile_change', models.BooleanField(default=True, verbose_name='Push Project changes')),
                ('email_startup_profile_update', models.BooleanField(default=True, verbose_name='Email Startup updates')),
                ('push_startup_profile_update', models.BooleanField(default=True, verbose_name='Push Startup updates')),
                ('active_email_preferences', models.CharField(blank=True, default='Project profile changed, Startup profile updated', max_length=50)),
                ('active_push_preferences', models.CharField(blank=True, default='Project profile changed, Startup profile updated', max_length=50)),
                ('investor', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='investor_notice_prefs', to='investors.investor')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trigger', models.CharField(choices=[('Project follower list or subscription share change', 'Project follower list or subscription share change'), ('Project profile changed', 'Project profile changed'), ('Startup profile updated', 'Startup profile updated'), ('Startup subscribers list changed', 'Startup subscribers list changed')], max_length=55)),
                ('initiator', models.CharField(choices=[('investor', 'investor'), ('project', 'project'), ('startup', 'startup')], max_length=8)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('investor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notice_investor', to='investors.investor')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notice_project', to='projects.project')),
                ('startup', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notice_startup', to='startups.startup')),
            ],
        ),
        migrations.CreateModel(
            name='StartupNotificationPrefs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_project_on_investor_interest_change', models.BooleanField(default=True, verbose_name='Email Investor-Project interest')),
                ('push_project_on_investor_interest_change', models.BooleanField(default=True, verbose_name='Push Investor-Project interest')),
                ('email_startup_on_investor_interest_change', models.BooleanField(default=True, verbose_name='Email Investor-Startup interest')),
                ('push_startup_on_investor_interest_change', models.BooleanField(default=True, verbose_name='Push Investor-Startup interest')),
                ('active_email_preferences', models.CharField(blank=True, default='Project follower list or subscription share change, Startup subscribers list changed', max_length=100)),
                ('active_push_preferences', models.CharField(blank=True, default='Project follower list or subscription share change, Startup subscribers list changed', max_length=100)),
                ('startup', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='startup_notice_prefs', to='startups.startup')),
            ],
        ),
        migrations.AddConstraint(
            model_name='notification',
            constraint=models.CheckConstraint(check=models.Q(('project__isnull', False), ('investor__isnull', False), _connector='OR'), name='project_or_investor_required'),
        ),
    ]
