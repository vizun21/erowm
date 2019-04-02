# Generated by Django 2.1.4 on 2019-02-27 14:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0011_auto_20190221_1117'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deadline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('regdatetime', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.Business')),
            ],
        ),
    ]
