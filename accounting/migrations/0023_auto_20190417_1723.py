# Generated by Django 2.1.4 on 2019-04-17 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0022_auto_20190415_1058'),
    ]

    operations = [
        migrations.RenameField(
            model_name='business',
            old_name='c_auth_key',
            new_name='s_auth_key',
        ),
    ]
