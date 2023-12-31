# Generated by Django 4.2.4 on 2023-12-03 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_patientsemd_diagnosis_error'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientsemd',
            name='content_error',
            field=models.CharField(db_index=True, max_length=300, verbose_name='Content error'),
        ),
        migrations.AlterField(
            model_name='patientsemd',
            name='diagnosis_error',
            field=models.CharField(db_index=True, max_length=300, verbose_name='Diagnosis error'),
        ),
    ]
