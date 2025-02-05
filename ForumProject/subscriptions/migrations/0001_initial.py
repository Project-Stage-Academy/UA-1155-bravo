# Generated by Django 5.0.6 on 2024-05-24 10:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('investors', '0001_initial'),
        ('startups', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscribeInvestorStartup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_at', models.DateTimeField(auto_now_add=True)),
                ('investor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='investors.investor')),
                ('startup', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='startups.startup')),
            ],
            options={
                'unique_together': {('investor', 'startup')},
            },
        ),
    ]
