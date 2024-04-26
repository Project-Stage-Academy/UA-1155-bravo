# Generated by Django 5.0.4 on 2024-04-25 18:43

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
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=150, unique=True)),
                ('project_status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('pending', 'Pending')], default='open', max_length=20)),
                ('startup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='startups.startup')),
            ],
        ),
        migrations.CreateModel(
            name='InvestorProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('share', models.IntegerField()),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='investors.investor')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
        ),
        migrations.AddConstraint(
            model_name='investorproject',
            constraint=models.CheckConstraint(check=models.Q(('share__gte', 0), ('share__lte', 100)), name='percentage_share_range'),
        ),
    ]
