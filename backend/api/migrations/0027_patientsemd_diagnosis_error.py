# Generated by Django 4.2.4 on 2023-12-03 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_patientsemd_has_cancer_diagnosis_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientsemd',
            name='diagnosis_error',
            field=models.CharField(db_index=True, default='', max_length=1024, verbose_name='Diagnosis error'),
            preserve_default=False,
        ),
    ]
