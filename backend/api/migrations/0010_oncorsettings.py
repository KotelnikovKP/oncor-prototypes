# Generated by Django 4.2.4 on 2023-09-10 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_semdservice'),
    ]

    operations = [
        migrations.CreateModel(
            name='OncorSettings',
            fields=[
                ('code', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='Setting code')),
                ('value', models.JSONField(null=True, verbose_name='Setting value')),
            ],
            options={
                'verbose_name': 'Oncor settings',
                'verbose_name_plural': 'Oncor settings',
                'ordering': ['code'],
            },
        ),
    ]