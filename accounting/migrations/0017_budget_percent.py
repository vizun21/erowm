# Generated by Django 2.1.4 on 2019-03-29 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0016_auto_20190312_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='percent',
            field=models.TextField(blank=True, null=True),
        ),
    ]