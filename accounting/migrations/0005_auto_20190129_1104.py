# Generated by Django 2.1.4 on 2019-01-29 02:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_auto_20190129_1102'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tblbank',
            unique_together={('Bkid', 'Bkdivision')},
        ),
    ]
