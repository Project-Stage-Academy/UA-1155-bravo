# Generated by Django 5.0.4 on 2024-04-28 14:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0001_initial'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investorproject',
            name='investor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shortlisted_project', to='investors.investor'),
        ),
        migrations.AlterField(
            model_name='investorproject',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_share', to='projects.project'),
        ),
    ]
