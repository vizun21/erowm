# Generated by Django 2.1.4 on 2019-04-09 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0017_budget_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='direct',
            field=models.BooleanField(default=False),
        ),
    ]
