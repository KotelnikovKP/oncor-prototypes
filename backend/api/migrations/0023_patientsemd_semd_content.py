# Generated by Django 4.2.4 on 2023-11-28 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_patientsemd'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientsemd',
            name='semd_content',
            field=models.JSONField(null=True, verbose_name='SEMD content'),
        ),
    ]
