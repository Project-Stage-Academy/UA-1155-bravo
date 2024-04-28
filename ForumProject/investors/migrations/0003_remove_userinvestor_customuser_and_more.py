
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0002_investorproject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinvestor',
            name='customuser',
        ),
        migrations.RemoveField(
            model_name='userinvestor',
            name='investor',
        ),
        migrations.DeleteModel(
            name='InvestorProject',
        ),
        migrations.DeleteModel(
            name='UserInvestor',
        ),
    ]
