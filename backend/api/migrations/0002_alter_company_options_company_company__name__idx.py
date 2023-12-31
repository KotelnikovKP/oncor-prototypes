# Generated by Django 4.2.4 on 2023-08-15 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'ordering': ['name'], 'verbose_name': 'Company', 'verbose_name_plural': 'Companies'},
        ),
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['name'], name='company__name__idx'),
        ),
    ]
