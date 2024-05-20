# Generated by Django 5.0.4 on 2024-05-12 15:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_notificationspreferences'),
        ('startups', '0002_remove_startup_startup_prefs'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_on_follower_subscription', models.BooleanField(default=True, verbose_name='Followers change email notices')),
                ('email_on_share_subscription', models.BooleanField(default=True, verbose_name='Sibscriptions change email notices')),
                ('in_app_on_follower_subscription', models.BooleanField(default=True, verbose_name='Followers change in_app notices')),
                ('in_app_on_share_subscription', models.BooleanField(default=True, verbose_name='Sibscriptions change in_app notices')),
                ('startup', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notice_preferences', to='startups.startup')),
            ],
        ),
        migrations.DeleteModel(
            name='NotificationsPreferences',
        ),
    ]
