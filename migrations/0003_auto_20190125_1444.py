# Generated by Django 2.1.4 on 2019-01-25 05:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_auto_20190125_1443'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='transaction',
            unique_together={('Bkid', 'Bkdivision')},
        ),
    ]
